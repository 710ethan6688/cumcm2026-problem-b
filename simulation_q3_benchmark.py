# -*- coding: utf-8 -*-
"""
2026 CUMCM Problem B - Question 3: Complete Unified Simulation Engine
Faithful Implementation of:
- 12-sided regular polygon uncertainty domain P_0
- Angular wedge half-plane clipping W(p_actual, theta_hat) with +-1 deg bearing error
- Exact 2D Minimum Enclosing Ball (Welzl algorithm with collinear handling)
- True Minimax baseline waypoint selection J_c(b) = max_y r(Posterior(K_c^+, b, y))
- Negative observation exclusion disks (no_signal: B(p_actual, 1000), clear_fail: B(p_actual, 20))
- Exact discrete grid fallback: Nx * Ny cells with Nx = max(1, ceil(W_c/delta_g))
- Full candidate task pool T_k and argmax S(tau) rolling horizon scheduler
- Physical Baseline C: dynamic 5-station cross cruise with nearest-neighbor greedy pursuit
- Dynamic empirical self-healing success rate tracking under random packet drops
- Comprehensive fine-grained event logging:
  * station_arrival
  * channel_tune
  * direction_measurement
  * clear_attempt
  * comm_retry
  * certificate_issued
- Exact reproducibility suite:
  1. 3 Official Formal Test Runs (with full JSON event logs)
  2. 5 Extreme Stress Scenarios (50 Monte Carlo runs each = 250 runs, saving raw run data)
  3. 100 Baseline & Ablation Comparison Runs (4 variants x 100 runs = 400 runs, saving raw run data)
  4. Multi-parameter Sensitivity Analysis
"""

import math
import random
import time
import json
import os
import shutil
import numpy as np

SEED = 2026
random.seed(SEED)
np.random.seed(SEED)

R_TARGET_AREA = 1800.0
R_MIN_SIG = 1000.0
R_MAX_SIG = 1500.0
SPEED = 5.0
DELTA_P = 0.5
R_MEB_THRESH = 19.5
DELTA_G = 26.0
R_RING = 1140.0
N_LOC_MAX = 3

# 7 Base Search Stations
Q7 = [(0.0, 0.0)]
for m in range(6):
    ang = m * math.pi / 3.0
    Q7.append((R_RING * math.cos(ang), R_RING * math.sin(ang)))

# --- Geometry Utilities ---

def make_regular_polygon(n_sides, radius):
    """Generate vertices of regular n-gon circumscribing circle of given radius."""
    R_outer = radius / math.cos(math.pi / n_sides)
    poly = []
    for i in range(n_sides):
        ang = (2.0 * math.pi * i + math.pi) / n_sides
        poly.append((R_outer * math.cos(ang), R_outer * math.sin(ang)))
    return poly

def clip_polygon(poly, p1, p2):
    """Sutherland-Hodgman clipping: keep points to the left of directed line p1 -> p2."""
    def is_inside(p):
        return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0]) >= -1e-7
    
    def intersection(cp1, cp2):
        dc = (cp1[0] - cp2[0], cp1[1] - cp2[1])
        dp = (p1[0] - p2[0], p1[1] - p2[1])
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = p1[0] * p2[1] - p1[1] * p2[0]
        denom = dc[0] * dp[1] - dc[1] * dp[0]
        if abs(denom) < 1e-11:
            return cp2
        return ((n1 * dp[0] - n2 * dc[0]) / denom, (n1 * dp[1] - n2 * dc[1]) / denom)

    output = []
    if not poly:
        return output
    s = poly[-1]
    for e in poly:
        if is_inside(e):
            if not is_inside(s):
                output.append(intersection(s, e))
            output.append(e)
        elif is_inside(s):
            output.append(intersection(s, e))
        s = e
    return output

def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def circle_from_2(p1, p2):
    c = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
    return c, dist(p1, p2) / 2.0

def circle_from_3(p1, p2, p3):
    ax, ay = p1; bx, by = p2; cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        d12 = dist(p1, p2)
        d23 = dist(p2, p3)
        d31 = dist(p3, p1)
        if d12 >= d23 and d12 >= d31:
            return circle_from_2(p1, p2)
        elif d23 >= d12 and d23 >= d31:
            return circle_from_2(p2, p3)
        else:
            return circle_from_2(p3, p1)
    ux = ((ax*ax + ay*ay)*(by - cy) + (bx*bx + by*by)*(cy - ay) + (cx*cx + cy*cy)*(ay - by)) / d
    uy = ((ax*ax + ay*ay)*(cx - bx) + (bx*bx + by*by)*(ax - cx) + (cx*cx + cy*cy)*(bx - ax)) / d
    c = (ux, uy)
    return c, dist(c, p1)

def is_in(c, r, p):
    return dist(c, p) <= r + 1e-6

def welzl(P, R, n):
    if n == 0 or len(R) == 3:
        if len(R) == 0:
            return (0.0, 0.0), 0.0
        elif len(R) == 1:
            return R[0], 0.0
        elif len(R) == 2:
            return circle_from_2(R[0], R[1])
        else:
            return circle_from_3(R[0], R[1], R[2])
    p = P[n - 1]
    c, r = welzl(P, R, n - 1)
    if is_in(c, r, p):
        return c, r
    return welzl(P, R + [p], n - 1)

def meb(points):
    """Welzl algorithm for 2D Minimum Enclosing Ball with collinear handling."""
    if not points:
        return (0.0, 0.0), 0.0
    pts = list(points)
    random.shuffle(pts)
    return welzl(pts, [], len(pts))

def polygon_centroid(poly):
    if not poly:
        return (0.0, 0.0)
    sx = sum(p[0] for p in poly)
    sy = sum(p[1] for p in poly)
    return (sx / len(poly), sy / len(poly))

def clip_wedge(poly, p_actual, theta_hat, eps_deg=1.0, max_dist=1500.0):
    """Clip polygon with sensor angular wedge [theta_hat - eps, theta_hat + eps] from p_actual."""
    th_low = theta_hat - math.radians(eps_deg)
    th_high = theta_hat + math.radians(eps_deg)
    
    d_high = (math.cos(th_high), math.sin(th_high))
    p_high = (p_actual[0] + 5000.0 * d_high[0], p_actual[1] + 5000.0 * d_high[1])
    poly = clip_polygon(poly, p_high, p_actual)
    if not poly:
        return []

    d_low = (math.cos(th_low), math.sin(th_low))
    p_low = (p_actual[0] + 5000.0 * d_low[0], p_actual[1] + 5000.0 * d_low[1])
    poly = clip_polygon(poly, p_actual, p_low)
    if not poly:
        return []
    
    d_mid = (math.cos(theta_hat), math.sin(theta_hat))
    p_cap_center = (p_actual[0] + max_dist * d_mid[0], p_actual[1] + max_dist * d_mid[1])
    p_cap_1 = (p_cap_center[0] + 5000.0 * d_mid[1], p_cap_center[1] - 5000.0 * d_mid[0])
    p_cap_2 = (p_cap_center[0] - 5000.0 * d_mid[1], p_cap_center[1] + 5000.0 * d_mid[0])
    poly = clip_polygon(poly, p_cap_1, p_cap_2)
    return poly

def clip_near_field(poly, p_actual, radius=5.0):
    """Clip polygon with 12-sided polygon circumscribed around B(p_actual, 5)."""
    p_near = make_regular_polygon(12, radius)
    for i in range(len(p_near)):
        p1 = (p_near[i][0] + p_actual[0], p_near[i][1] + p_actual[1])
        p2 = (p_near[(i+1)%len(p_near)][0] + p_actual[0], p_near[(i+1)%len(p_near)][1] + p_actual[1])
        poly = clip_polygon(poly, p1, p2)
        if not poly:
            break
    return poly

def find_minimax_waypoint(poly, robot_pos):
    """
    Minimax candidate waypoint optimization:
    J_c(b) = max_{y} r(Posterior(K_c^+, b, y))
    b* = argmin_b J_c(b)
    """
    cent = polygon_centroid(poly)
    d_cent = math.hypot(cent[0] - robot_pos[0], cent[1] - robot_pos[1])
    los_ang = math.atan2(cent[1] - robot_pos[1], cent[0] - robot_pos[0])
    
    # Generate lateral baseline candidates
    candidates = []
    for d_off in [120.0, 200.0, 280.0]:
        for ang_off in [-math.pi / 2.0, math.pi / 2.0, -math.pi / 3.0, math.pi / 3.0]:
            candidates.append((robot_pos[0] + 0.45 * d_cent * math.cos(los_ang) + d_off * math.cos(los_ang + ang_off),
                               robot_pos[1] + 0.45 * d_cent * math.sin(los_ang) + d_off * math.sin(los_ang + ang_off)))
    
    best_b = candidates[0]
    best_J = 1e9
    
    for b in candidates:
        # Range of bearings to poly vertices
        angs = [math.atan2(v[1] - b[1], v[0] - b[0]) for v in poly]
        th_min, th_max = min(angs), max(angs)
        
        # Sample possible bearing feedbacks
        worst_r = 0.0
        for th in [th_min, (th_min + th_max) / 2.0, th_max]:
            post = clip_wedge(list(poly), b, th, eps_deg=1.0)
            if post:
                _, r_post = meb(post)
            else:
                r_post = 0.0
            if r_post > worst_r:
                worst_r = r_post
        
        if worst_r < best_J:
            best_J = worst_r
            best_b = b
            
    return best_b, best_J

# --- Simulation Engine ---

class Q3Simulation:
    def __init__(self, targets_config, comm_fault_rate=0.0, force_grid=False, no_active_loc=False, no_interleave=False,
                 r_meb_thresh=R_MEB_THRESH, delta_g=DELTA_G, n_loc_max=N_LOC_MAX, rng=None):
        self.rng = rng or random.Random(SEED)
        self.targets = targets_config
        self.comm_fault_rate = comm_fault_rate
        self.force_grid = force_grid
        self.no_active_loc = no_active_loc
        self.no_interleave = no_interleave
        self.r_meb_thresh = r_meb_thresh
        self.delta_g = delta_g
        self.n_loc_max = n_loc_max
        
        self.robot_pos = (0.0, 0.0)
        self.current_channel = 1
        self.virtual_time = 0.0
        self.step = 0
        self.logs = []
        
        self.cleared_channels = set()
        self.absent_channels = set()
        self.alive_channels = set()
        
        # Uncertainty sets K_c^+
        self.polygons = {c: make_regular_polygon(12, R_TARGET_AREA) for c in range(1, 21)}
        # Explicit exclusion disks B(p_actual, R_excl)
        self.exclusion_disks = {c: [] for c in range(1, 21)}
        # Grid visited units
        self.grid_visited = {c: set() for c in range(1, 21)}
        
        self.loc_counts = {c: 0 for c in range(1, 21)}
        self.searched_stations = set() # (station_idx, channel)
        
        self.station_visit_count = 0
        self.channel_measure_count = 0
        self.clear_action_count = 0
        self.grid_triggered_count = 0
        
        # Communication tracking
        self.comm_attempts = 0
        self.comm_successes = 0
        self.comm_failures = 0
        self.self_healed_tx = 0
        
        self.certificate_issued = False

    def _log(self, event_type, channel=None, details=None):
        self.step += 1
        record = {
            "step": self.step,
            "virtual_time": round(self.virtual_time, 2),
            "event_type": event_type,
            "channel": channel,
            "robot_pos": [round(self.robot_pos[0], 2), round(self.robot_pos[1], 2)],
            "details": details or {}
        }
        self.logs.append(record)

    def _check_comm_link(self, op_name, channel=None):
        self.comm_attempts += 1
        if self.comm_fault_rate <= 0:
            self.comm_successes += 1
            return True
        
        # Try up to 3 retries
        for retry in range(3):
            if self.rng.random() < self.comm_fault_rate:
                self.virtual_time += 1.0 # 1s timeout
                self.self_healed_tx += 1
                self._log("comm_retry", channel=channel, details={"operation": op_name, "retry": retry + 1})
            else:
                self.comm_successes += 1
                return True
        self.comm_failures += 1
        return False

    def _move_to(self, target_waypoint):
        ang = self.rng.uniform(0, 2 * math.pi)
        err = self.rng.uniform(0, DELTA_P)
        p_actual = (target_waypoint[0] + err * math.cos(ang), target_waypoint[1] + err * math.sin(ang))
        
        dist_m = math.hypot(p_actual[0] - self.robot_pos[0], p_actual[1] - self.robot_pos[1])
        t_move = dist_m / SPEED
        self.virtual_time += t_move
        self.robot_pos = p_actual
        self.station_visit_count += 1
        
        self._check_comm_link("move_ack")
        self._log("station_arrival", details={"nominal_waypoint": [round(target_waypoint[0], 2), round(target_waypoint[1], 2)], "actual_pos": [round(p_actual[0], 2), round(p_actual[1], 2)]})
        return p_actual

    def _tune_channel(self, channel):
        if self.current_channel != channel:
            self.virtual_time += 1.0
            self._log("channel_tune", channel=channel, details={"from_channel": self.current_channel, "to_channel": channel, "tune_time": 1.0})
            self.current_channel = channel

    def _measure_bearing(self, channel):
        self._tune_channel(channel)
        self.virtual_time += 5.0
        self.channel_measure_count += 1
        self._check_comm_link("sensor_measure", channel)

        if channel not in self.targets or self.targets[channel]['cleared']:
            self.exclusion_disks[channel].append((self.robot_pos, 1000.0))
            self._log("direction_measurement", channel=channel, details={"feedback": "no_signal", "exclusion_radius": 1000.0})
            return "no_signal", None

        tgt = self.targets[channel]
        d = math.hypot(tgt['pos'][0] - self.robot_pos[0], tgt['pos'][1] - self.robot_pos[1])
        
        if d > tgt['radius']:
            self.exclusion_disks[channel].append((self.robot_pos, 1000.0))
            self._log("direction_measurement", channel=channel, details={"feedback": "no_signal", "exclusion_radius": 1000.0})
            return "no_signal", None
        
        if d <= 5.0:
            self.polygons[channel] = clip_near_field(self.polygons[channel], self.robot_pos, radius=5.0)
            c_meb, r_meb = meb(self.polygons[channel])
            self.alive_channels.add(channel)
            self._log("direction_measurement", channel=channel, details={"feedback": "near", "meb_center": [round(c_meb[0], 2), round(c_meb[1], 2)], "meb_radius": round(r_meb, 2)})
            return "near", (c_meb, r_meb)
        
        true_theta = math.atan2(tgt['pos'][1] - self.robot_pos[1], tgt['pos'][0] - self.robot_pos[0])
        theta_hat = true_theta + math.radians(self.rng.uniform(-1.0, 1.0))
        self.polygons[channel] = clip_wedge(self.polygons[channel], self.robot_pos, theta_hat, eps_deg=1.0, max_dist=R_MAX_SIG)
        c_meb, r_meb = meb(self.polygons[channel])
        self.alive_channels.add(channel)
        self._log("direction_measurement", channel=channel, details={"feedback": "direction", "bearing_deg": round(math.degrees(theta_hat), 2), "meb_center": [round(c_meb[0], 2), round(c_meb[1], 2)], "meb_radius": round(r_meb, 2)})
        return "direction", (c_meb, r_meb)

    def _clear_target(self, channel, clear_waypoint):
        self._move_to(clear_waypoint)
        self.clear_action_count += 1
        
        tgt = self.targets.get(channel)
        if tgt and not tgt['cleared']:
            d_true = math.hypot(tgt['pos'][0] - self.robot_pos[0], tgt['pos'][1] - self.robot_pos[1])
            if d_true <= 20.0:
                self.virtual_time += 5.0
                tgt['cleared'] = True
                self.cleared_channels.add(channel)
                if channel in self.alive_channels:
                    self.alive_channels.remove(channel)
                self._log("clear_attempt", channel=channel, details={"result": "success", "true_distance": round(d_true, 2), "duration": 5.0})
                return True
        
        # Clear failure: record exclusion disk B(p_actual, 20)
        self.virtual_time += 3.0
        self.exclusion_disks[channel].append((self.robot_pos, 20.0))
        self._log("clear_attempt", channel=channel, details={"result": "fail", "duration": 3.0, "exclusion_radius": 20.0})
        return False

    def _check_termination(self):
        if self.certificate_issued:
            return True
        if len(self.cleared_channels) >= 16:
            self.certificate_issued = True
            self._log("certificate_issued", details={"certificate": "CERT_1_ALL_16_CLEARED", "cleared_count": len(self.cleared_channels)})
            return True
        if len(self.cleared_channels) + len(self.absent_channels) == 20:
            self.certificate_issued = True
            self._log("certificate_issued", details={"certificate": "CERT_2_ALL_20_ACCOUNTED", "cleared_count": len(self.cleared_channels), "absent_count": len(self.absent_channels)})
            return True
        return False

    def _build_task_pool(self):
        """
        Build full candidate task pool T_k = T_clear U T_loc U T_grid U T_search
        Compute exact ordinal score S(tau) = W_type - Delta T_exec + beta * G_shrink
        """
        tasks = []
        
        # 1. Clear tasks (T_clear)
        for c in list(self.alive_channels):
            if c in self.cleared_channels:
                continue
            c_meb, r_meb = meb(self.polygons[c])
            if r_meb <= self.r_meb_thresh:
                d_wpt = math.hypot(c_meb[0] - self.robot_pos[0], c_meb[1] - self.robot_pos[1])
                dt = d_wpt / SPEED + 5.0
                score = 2000.0 - dt
                tasks.append({"type": "clear", "channel": c, "waypoint": c_meb, "score": score, "dt": dt})
        
        # If clear tasks exist, clear takes absolute priority
        if tasks:
            return tasks
        
        # 2. Localization tasks (T_loc)
        if not self.force_grid and not self.no_active_loc:
            for c in list(self.alive_channels):
                if c in self.cleared_channels or self.loc_counts[c] >= self.n_loc_max:
                    continue
                c_meb, r_meb = meb(self.polygons[c])
                b_star, J_star = find_minimax_waypoint(self.polygons[c], self.robot_pos)
                d_wpt = math.hypot(b_star[0] - self.robot_pos[0], b_star[1] - self.robot_pos[1])
                tune_cost = 1.0 if self.current_channel != c else 0.0
                dt = d_wpt / SPEED + tune_cost + 5.0
                g_shrink = max(0.0, r_meb - J_star)
                score = 500.0 - dt + 1.2 * g_shrink
                tasks.append({"type": "loc", "channel": c, "waypoint": b_star, "score": score, "dt": dt})

        # 3. Grid tasks (T_grid)
        for c in list(self.alive_channels):
            if c in self.cleared_channels:
                continue
            if self.force_grid or self.no_active_loc or self.loc_counts[c] >= self.n_loc_max:
                poly = self.polygons[c]
                if not poly:
                    continue
                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                W_c = max_x - min_x
                H_c = max_y - min_y
                Nx = max(1, math.ceil(W_c / self.delta_g))
                Ny = max(1, math.ceil(H_c / self.delta_g))
                
                for ix in range(Nx):
                    gx = min_x + (ix + 0.5) * (W_c / Nx)
                    for iy in range(Ny):
                        gy = min_y + (iy + 0.5) * (H_c / Ny)
                        cell_key = (round(gx, 1), round(gy, 1))
                        if cell_key in self.grid_visited[c]:
                            continue
                        # Check exclusion disks
                        is_excluded = any(math.hypot(gx - ep[0], gy - ep[1]) <= er for ep, er in self.exclusion_disks[c])
                        if is_excluded:
                            self.grid_visited[c].add(cell_key)
                            continue
                        d_wpt = math.hypot(gx - self.robot_pos[0], gy - self.robot_pos[1])
                        dt = d_wpt / SPEED + 5.0
                        score = 800.0 - dt
                        tasks.append({"type": "grid", "channel": c, "waypoint": (gx, gy), "cell_key": cell_key, "score": score, "dt": dt})

        # 4. Search tasks (T_search)
        for s_idx, station in enumerate(Q7):
            for c in range(1, 21):
                if c in self.cleared_channels or c in self.absent_channels or c in self.alive_channels:
                    continue
                if (s_idx, c) in self.searched_stations:
                    continue
                d_wpt = math.hypot(station[0] - self.robot_pos[0], station[1] - self.robot_pos[1])
                tune_cost = 1.0 if self.current_channel != c else 0.0
                dt = d_wpt / SPEED + tune_cost + 5.0
                score = 100.0 - dt
                tasks.append({"type": "search", "channel": c, "station_idx": s_idx, "waypoint": station, "score": score, "dt": dt})

        return tasks

    def run(self):
        t_start = time.time()
        
        if self.no_interleave:
            # Variant B: Strictly sequential - all 7 Q7 stations searched first, then locate/clear all
            for s_idx, station in enumerate(Q7):
                self._move_to(station)
                for c in range(1, 21):
                    if c in self.cleared_channels or c in self.absent_channels or c in self.alive_channels:
                        continue
                    fb, info = self._measure_bearing(c)
                    self.searched_stations.add((s_idx, c))
                if self._check_termination():
                    break
            
            # Now locate and clear alive channels
            for c in list(self.alive_channels):
                while c not in self.cleared_channels:
                    c_meb, r_meb = meb(self.polygons[c])
                    if r_meb <= self.r_meb_thresh:
                        self._clear_target(c, c_meb)
                        break
                    if self.no_active_loc or self.loc_counts[c] >= self.n_loc_max:
                        # Grid fallback
                        poly = self.polygons[c]
                        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
                        W_c, H_c = max(xs) - min(xs), max(ys) - min(ys)
                        Nx = max(1, math.ceil(W_c / self.delta_g))
                        Ny = max(1, math.ceil(H_c / self.delta_g))
                        cleared_it = False
                        for ix in range(Nx):
                            gx = min(xs) + (ix + 0.5) * (W_c / Nx)
                            for iy in range(Ny):
                                gy = min(ys) + (iy + 0.5) * (H_c / Ny)
                                self.grid_triggered_count += 1
                                if self._clear_target(c, (gx, gy)):
                                    cleared_it = True
                                    break
                            if cleared_it:
                                break
                        break
                    else:
                        self.loc_counts[c] += 1
                        b_star, _ = find_minimax_waypoint(self.polygons[c], self.robot_pos)
                        self._move_to(b_star)
                        fb_sub, _ = self._measure_bearing(c)
                        if fb_sub == "near":
                            c_meb, _ = meb(self.polygons[c])
                            self._clear_target(c, c_meb)
                            break
                if self._check_termination():
                    break
            
            # Check absent channels
            for c in range(1, 21):
                if c not in self.cleared_channels and c not in self.alive_channels:
                    self.absent_channels.add(c)
            self._check_termination()

        else:
            # Full scheme with argmax S(tau) rolling scheduler
            while not self._check_termination():
                tasks = self._build_task_pool()
                if not tasks:
                    # All possible tasks completed, certify absent channels
                    for c in range(1, 21):
                        if c not in self.cleared_channels and c not in self.alive_channels:
                            self.absent_channels.add(c)
                    self._check_termination()
                    break
                
                # argmax S(tau)
                best_task = max(tasks, key=lambda tk: tk["score"])
                t_type = best_task["type"]
                c = best_task["channel"]
                
                if t_type == "clear":
                    self._clear_target(c, best_task["waypoint"])
                elif t_type == "loc":
                    self.loc_counts[c] += 1
                    self._move_to(best_task["waypoint"])
                    fb, info = self._measure_bearing(c)
                    if fb == "near":
                        c_meb, _ = meb(self.polygons[c])
                        self._clear_target(c, c_meb)
                elif t_type == "grid":
                    self.grid_triggered_count += 1
                    self.grid_visited[c].add(best_task["cell_key"])
                    self._clear_target(c, best_task["waypoint"])
                elif t_type == "search":
                    s_idx = best_task["station_idx"]
                    # If robot needs to move to station, move first
                    if math.hypot(best_task["waypoint"][0] - self.robot_pos[0], best_task["waypoint"][1] - self.robot_pos[1]) > 1.0:
                        self._move_to(best_task["waypoint"])
                    fb, info = self._measure_bearing(c)
                    self.searched_stations.add((s_idx, c))

        t_elapsed = round(time.time() - t_start, 3)
        self_heal_rate = self.comm_successes / max(1, self.comm_attempts)
        
        summary = {
            "true_targets": len(self.targets),
            "cleared_targets": len(self.cleared_channels),
            "clear_rate": round(len(self.cleared_channels) / max(1, len(self.targets)), 4),
            "station_count": self.station_visit_count,
            "channel_measure_count": self.channel_measure_count,
            "clear_action_count": self.clear_action_count,
            "virtual_time": round(self.virtual_time, 1),
            "compute_time": t_elapsed,
            "grid_triggered": self.grid_triggered_count,
            "self_heal_success": round(self_heal_rate, 4),
            "healed_tx": self.self_healed_tx,
            "certificate": "CERT_1" if len(self.cleared_channels) >= 16 else "CERT_2"
        }
        return summary, self.logs

# --- Target Generator ---
def generate_targets(rng, N_targets, r_range=(0.0, R_TARGET_AREA - 20.0), cluster=False):
    active_channels = sorted(rng.sample(range(1, 21), N_targets))
    targets = {}
    if cluster:
        c_r = rng.uniform(200.0, 900.0)
        c_th = rng.uniform(0, 2 * math.pi)
        cx, cy = c_r * math.cos(c_th), c_r * math.sin(c_th)
        for c in active_channels:
            cr = rng.uniform(0, 180.0)
            cth = rng.uniform(0, 2 * math.pi)
            targets[c] = {
                'pos': (cx + cr * math.cos(cth), cy + cr * math.sin(cth)),
                'radius': rng.uniform(R_MIN_SIG, R_MAX_SIG),
                'cleared': False
            }
    else:
        for c in active_channels:
            r = math.sqrt(rng.random()) * (r_range[1] - r_range[0]) + r_range[0]
            theta = rng.random() * 2 * math.pi
            targets[c] = {
                'pos': (r * math.cos(theta), r * math.sin(theta)),
                'radius': rng.uniform(R_MIN_SIG, R_MAX_SIG),
                'cleared': False
            }
    return targets

# --- Physical Baseline C (5-Station Cross Patrol with Dynamic Nearest Neighbor Greedy Pursuit) ---
def run_baseline_c_dynamic(targets_config, rng):
    t0 = time.time()
    patrol_stations = [(0.0, 0.0), (650.0, 0.0), (0.0, 650.0), (-650.0, 0.0), (0.0, -650.0)]
    robot_pos = (0.0, 0.0)
    virt_time = 0.0
    cleared = set()
    
    for station in patrol_stations:
        d_move = math.hypot(station[0] - robot_pos[0], station[1] - robot_pos[1])
        virt_time += d_move / SPEED
        robot_pos = station
        
        detected = []
        for c, tgt in targets_config.items():
            if c not in cleared:
                d_tgt = math.hypot(tgt['pos'][0] - robot_pos[0], tgt['pos'][1] - robot_pos[1])
                if d_tgt <= tgt['radius']:
                    detected.append(c)
        
        while detected:
            nearest_c = min(detected, key=lambda ch: math.hypot(targets_config[ch]['pos'][0] - robot_pos[0], targets_config[ch]['pos'][1] - robot_pos[1]))
            t_pos = targets_config[nearest_c]['pos']
            d_track = math.hypot(t_pos[0] - robot_pos[0], t_pos[1] - robot_pos[1])
            virt_time += d_track / SPEED + 5.0
            robot_pos = t_pos
            cleared.add(nearest_c)
            detected.remove(nearest_c)
            
    t_elapsed = round(time.time() - t0, 3)
    return {
        "true_targets": len(targets_config),
        "cleared_targets": len(cleared),
        "clear_rate": round(len(cleared) / max(1, len(targets_config)), 4),
        "virtual_time": round(virt_time, 1),
        "compute_time": t_elapsed
    }

def main():
    print("=== Starting Q3 Unified Simulation Engine (Full Algorithm) ===")
    t_suite_start = time.time()
    
    log_dir_1 = "C:/Users/23066/Desktop/mathmode/logs"
    log_dir_2 = "C:/Users/23066/Desktop/logs"
    os.makedirs(log_dir_1, exist_ok=True)
    os.makedirs(log_dir_2, exist_ok=True)
    
    # -------------------------------------------------------------
    # 1. Official 3 Formal Test Runs
    # -------------------------------------------------------------
    print("\n--- 1. Running Official 3 Formal Tests ---")
    official_results = {}
    master_rng = random.Random(SEED)
    
    for tid, n in [(1, 11), (2, 14), (3, 16)]:
        t_conf = generate_targets(master_rng, n)
        t_run = {c: dict(t_conf[c]) for c in t_conf}
        sim = Q3Simulation(t_run, rng=random.Random(SEED + tid))
        summary, logs = sim.run()
        official_results[f"test_{tid}"] = summary
        
        print(f"Official Test {tid} (N={n}): Cleared={summary['cleared_targets']}/{summary['true_targets']}, "
              f"Stations={summary['station_count']}, Measures={summary['channel_measure_count']}, "
              f"Clears={summary['clear_action_count']}, VirtTime={summary['virtual_time']}s, "
              f"Cert={summary['certificate']}")
        
        with open(os.path.join(log_dir_1, f"q3_official_test{tid}_log.json"), "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
        with open(os.path.join(log_dir_2, f"q3_official_test{tid}_log.json"), "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

    with open(os.path.join(log_dir_1, "q3_official_summary.json"), "w", encoding="utf-8") as f:
        json.dump(official_results, f, indent=2)
    with open(os.path.join(log_dir_2, "q3_official_summary.json"), "w", encoding="utf-8") as f:
        json.dump(official_results, f, indent=2)

    # -------------------------------------------------------------
    # 2. 5 Extreme Stress Test Scenarios (50 Monte Carlo runs each)
    # -------------------------------------------------------------
    print("\n--- 2. Running 5 Stress Test Scenarios (50 runs each) ---")
    stress_results = {}
    stress_configs = [
        ("outer_ring", {"r_range": (1500.0, 1780.0), "cluster": False, "comm_fault": 0.0, "force_grid": False, "fixed_radius": None}),
        ("dense_cluster", {"r_range": (0.0, 900.0), "cluster": True, "comm_fault": 0.0, "force_grid": False, "fixed_radius": None}),
        ("min_radius", {"r_range": (0.0, 1780.0), "cluster": False, "comm_fault": 0.0, "force_grid": False, "fixed_radius": 1000.0}),
        ("comm_fault", {"r_range": (0.0, 1780.0), "cluster": False, "comm_fault": 0.05, "force_grid": False, "fixed_radius": None}),
        ("forced_grid", {"r_range": (0.0, 1780.0), "cluster": False, "comm_fault": 0.0, "force_grid": True, "fixed_radius": None}),
    ]

    for name, cfg in stress_configs:
        v_times = []
        c_rates = []
        heal_rates = []
        grid_trigs = 0
        healed_sum = 0
        raw_runs = []
        
        for run_idx in range(50):
            r_seed = SEED + 1000 + run_idx
            r_rng = random.Random(r_seed)
            n_tgt = r_rng.randint(10, 16)
            t_conf = generate_targets(r_rng, n_tgt, r_range=cfg["r_range"], cluster=cfg["cluster"])
            if cfg["fixed_radius"]:
                for c in t_conf:
                    t_conf[c]["radius"] = cfg["fixed_radius"]
            
            sim = Q3Simulation(t_conf, comm_fault_rate=cfg["comm_fault"], force_grid=cfg["force_grid"], rng=r_rng)
            summ, _ = sim.run()
            v_times.append(summ["virtual_time"])
            c_rates.append(summ["clear_rate"])
            heal_rates.append(summ["self_heal_success"])
            grid_trigs += summ["grid_triggered"]
            healed_sum += summ["healed_tx"]
            raw_runs.append({
                "run": run_idx + 1,
                "targets": summ["true_targets"],
                "cleared": summ["cleared_targets"],
                "virtual_time": summ["virtual_time"],
                "self_heal_success": summ["self_heal_success"],
                "healed_tx": summ["healed_tx"],
                "grid_triggered": summ["grid_triggered"]
            })
            
        stress_results[name] = {
            "clear_rate": round(float(np.mean(c_rates)), 4),
            "time_mean": round(float(np.mean(v_times)), 1),
            "time_std": round(float(np.std(v_times)), 1),
            "time_max": round(float(np.max(v_times)), 1),
            "grid_triggers": grid_trigs,
            "self_heal_success": round(float(np.mean(heal_rates)), 4),
            "healed_tx": healed_sum,
            "raw_runs": raw_runs
        }
        print(f"Stress [{name}]: ClearRate={stress_results[name]['clear_rate']*100}%, MeanTime={stress_results[name]['time_mean']}s, Std={stress_results[name]['time_std']}s, GridTriggers={grid_trigs}, HealedTx={healed_sum}, SelfHealRate={stress_results[name]['self_heal_success']*100}%")

    with open(os.path.join(log_dir_1, "q3_stress_test_summary.json"), "w", encoding="utf-8") as f:
        json.dump(stress_results, f, indent=2)
    with open(os.path.join(log_dir_2, "q3_stress_test_summary.json"), "w", encoding="utf-8") as f:
        json.dump(stress_results, f, indent=2)

    # -------------------------------------------------------------
    # 3. 100 Baseline & Ablation Comparison Runs
    # -------------------------------------------------------------
    print("\n--- 3. Running 100 Baseline & Ablation Runs ---")
    ablation_stats = {
        "full_scheme": {"times": [], "cleared": 0, "total": 0, "comp_times": [], "raw": []},
        "variant_a_no_loc": {"times": [], "cleared": 0, "total": 0, "comp_times": [], "raw": []},
        "variant_b_no_interleave": {"times": [], "cleared": 0, "total": 0, "comp_times": [], "raw": []},
        "baseline_c_greedy": {"times": [], "cleared": 0, "total": 0, "comp_times": [], "raw": [], "fully_cleared": 0}
    }

    abl_rng = random.Random(SEED + 5000)
    for run_idx in range(100):
        n_tgt = abl_rng.randint(10, 16)
        t_base = generate_targets(abl_rng, n_tgt)
        
        # 1) Full scheme
        t_run1 = {c: dict(t_base[c]) for c in t_base}
        s1, _ = Q3Simulation(t_run1, rng=random.Random(SEED + run_idx)).run()
        ablation_stats["full_scheme"]["times"].append(s1["virtual_time"])
        ablation_stats["full_scheme"]["cleared"] += s1["cleared_targets"]
        ablation_stats["full_scheme"]["total"] += s1["true_targets"]
        ablation_stats["full_scheme"]["comp_times"].append(s1["compute_time"])
        ablation_stats["full_scheme"]["raw"].append({"run": run_idx + 1, "time": s1["virtual_time"], "cleared": s1["cleared_targets"]})

        # 2) Variant A (no active loc)
        t_run2 = {c: dict(t_base[c]) for c in t_base}
        s2, _ = Q3Simulation(t_run2, no_active_loc=True, rng=random.Random(SEED + run_idx)).run()
        ablation_stats["variant_a_no_loc"]["times"].append(s2["virtual_time"])
        ablation_stats["variant_a_no_loc"]["cleared"] += s2["cleared_targets"]
        ablation_stats["variant_a_no_loc"]["total"] += s2["true_targets"]
        ablation_stats["variant_a_no_loc"]["comp_times"].append(s2["compute_time"])
        ablation_stats["variant_a_no_loc"]["raw"].append({"run": run_idx + 1, "time": s2["virtual_time"], "cleared": s2["cleared_targets"]})

        # 3) Variant B (no interleaving)
        t_run3 = {c: dict(t_base[c]) for c in t_base}
        s3, _ = Q3Simulation(t_run3, no_interleave=True, rng=random.Random(SEED + run_idx)).run()
        ablation_stats["variant_b_no_interleave"]["times"].append(s3["virtual_time"])
        ablation_stats["variant_b_no_interleave"]["cleared"] += s3["cleared_targets"]
        ablation_stats["variant_b_no_interleave"]["total"] += s3["true_targets"]
        ablation_stats["variant_b_no_interleave"]["comp_times"].append(s3["compute_time"])
        ablation_stats["variant_b_no_interleave"]["raw"].append({"run": run_idx + 1, "time": s3["virtual_time"], "cleared": s3["cleared_targets"]})

        # 4) Baseline C (physical cross cruise greedy)
        t_run4 = {c: dict(t_base[c]) for c in t_base}
        s4 = run_baseline_c_dynamic(t_run4, rng=random.Random(SEED + run_idx))
        ablation_stats["baseline_c_greedy"]["times"].append(s4["virtual_time"])
        ablation_stats["baseline_c_greedy"]["cleared"] += s4["cleared_targets"]
        ablation_stats["baseline_c_greedy"]["total"] += s4["true_targets"]
        ablation_stats["baseline_c_greedy"]["comp_times"].append(s4["compute_time"])
        ablation_stats["baseline_c_greedy"]["raw"].append({"run": run_idx + 1, "time": s4["virtual_time"], "cleared": s4["cleared_targets"]})
        if s4["cleared_targets"] == s4["true_targets"]:
            ablation_stats["baseline_c_greedy"]["fully_cleared"] += 1

    total_targets_gen = ablation_stats["full_scheme"]["total"]
    ablation_summary = {
        "total_scenarios": 100,
        "total_targets_generated": total_targets_gen,
        "full_scheme": {
            "clear_rate": round(ablation_stats["full_scheme"]["cleared"] / total_targets_gen, 4),
            "cleared_targets": ablation_stats["full_scheme"]["cleared"],
            "mean_time": round(float(np.mean(ablation_stats["full_scheme"]["times"])), 1),
            "median_time": round(float(np.median(ablation_stats["full_scheme"]["times"])), 1),
            "p95_time": round(float(np.percentile(ablation_stats["full_scheme"]["times"], 95)), 1),
            "max_time": round(float(np.max(ablation_stats["full_scheme"]["times"])), 1),
            "compute_time": round(float(np.mean(ablation_stats["full_scheme"]["comp_times"])), 3),
            "raw_runs": ablation_stats["full_scheme"]["raw"]
        },
        "variant_a_no_q2": {
            "clear_rate": round(ablation_stats["variant_a_no_loc"]["cleared"] / total_targets_gen, 4),
            "cleared_targets": ablation_stats["variant_a_no_loc"]["cleared"],
            "mean_time": round(float(np.mean(ablation_stats["variant_a_no_loc"]["times"])), 1),
            "median_time": round(float(np.median(ablation_stats["variant_a_no_loc"]["times"])), 1),
            "p95_time": round(float(np.percentile(ablation_stats["variant_a_no_loc"]["times"], 95)), 1),
            "max_time": round(float(np.max(ablation_stats["variant_a_no_loc"]["times"])), 1),
            "compute_time": round(float(np.mean(ablation_stats["variant_a_no_loc"]["comp_times"])), 3),
            "raw_runs": ablation_stats["variant_a_no_loc"]["raw"]
        },
        "variant_b_no_interleave": {
            "clear_rate": round(ablation_stats["variant_b_no_interleave"]["cleared"] / total_targets_gen, 4),
            "cleared_targets": ablation_stats["variant_b_no_interleave"]["cleared"],
            "mean_time": round(float(np.mean(ablation_stats["variant_b_no_interleave"]["times"])), 1),
            "median_time": round(float(np.median(ablation_stats["variant_b_no_interleave"]["times"])), 1),
            "p95_time": round(float(np.percentile(ablation_stats["variant_b_no_interleave"]["times"], 95)), 1),
            "max_time": round(float(np.max(ablation_stats["variant_b_no_interleave"]["times"])), 1),
            "compute_time": round(float(np.mean(ablation_stats["variant_b_no_interleave"]["comp_times"])), 3),
            "raw_runs": ablation_stats["variant_b_no_interleave"]["raw"]
        },
        "baseline_c_greedy": {
            "clear_rate": round(ablation_stats["baseline_c_greedy"]["cleared"] / total_targets_gen, 4),
            "cleared_targets": ablation_stats["baseline_c_greedy"]["cleared"],
            "missed_targets": total_targets_gen - ablation_stats["baseline_c_greedy"]["cleared"],
            "whole_field_success_rate": round(ablation_stats["baseline_c_greedy"]["fully_cleared"] / 100.0, 2),
            "mean_time": round(float(np.mean(ablation_stats["baseline_c_greedy"]["times"])), 1),
            "median_time": round(float(np.median(ablation_stats["baseline_c_greedy"]["times"])), 1),
            "p95_time": round(float(np.percentile(ablation_stats["baseline_c_greedy"]["times"], 95)), 1),
            "max_time": round(float(np.max(ablation_stats["baseline_c_greedy"]["times"])), 1),
            "compute_time": round(float(np.mean(ablation_stats["baseline_c_greedy"]["comp_times"])), 3),
            "raw_runs": ablation_stats["baseline_c_greedy"]["raw"]
        }
    }

    print(f"Ablation Results Summary: TotalTargets={total_targets_gen}")
    for k, v in ablation_summary.items():
        if isinstance(v, dict):
            print(f"  {k}: ClearRate={v.get('clear_rate')}, MeanTime={v.get('mean_time')}s, P95={v.get('p95_time')}s")

    with open(os.path.join(log_dir_1, "q3_ablation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(ablation_summary, f, indent=2)
    with open(os.path.join(log_dir_2, "q3_ablation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(ablation_summary, f, indent=2)

    # -------------------------------------------------------------
    # 4. Multi-parameter Sensitivity Analysis
    # -------------------------------------------------------------
    print("\n--- 4. Running Parameter Sensitivity Analysis ---")
    sensitivity_results = {}
    
    # 4.1 Budget N_loc_max in [1, 2, 3, 4]
    budget_stats = {}
    for b in [1, 2, 3, 4]:
        b_times = []
        b_meb_conv = []
        for run_idx in range(30):
            r_rng = random.Random(SEED + 8000 + run_idx)
            n_tgt = r_rng.randint(10, 16)
            t_conf = generate_targets(r_rng, n_tgt)
            sim = Q3Simulation(t_conf, n_loc_max=b, rng=r_rng)
            summ, _ = sim.run()
            b_times.append(summ["virtual_time"])
            b_meb_conv.append(1.0 if summ["grid_triggered"] == 0 else 0.0)
        budget_stats[f"budget_{b}"] = {
            "meb_conv_rate": round(float(np.mean(b_meb_conv)), 3),
            "mean_time": round(float(np.mean(b_times)), 1)
        }
    sensitivity_results["loc_budget"] = budget_stats
    print(f"Sensitivity LocBudget: {budget_stats}")

    # 4.2 MEB threshold in [18.0, 19.0, 19.5, 20.0]
    meb_stats = {}
    for r_th in [18.0, 19.0, 19.5, 20.0]:
        th_times = []
        for run_idx in range(30):
            r_rng = random.Random(SEED + 9000 + run_idx)
            n_tgt = r_rng.randint(10, 16)
            t_conf = generate_targets(r_rng, n_tgt)
            sim = Q3Simulation(t_conf, r_meb_thresh=r_th, rng=r_rng)
            summ, _ = sim.run()
            th_times.append(summ["virtual_time"])
        meb_stats[f"thresh_{r_th}"] = {
            "mean_time": round(float(np.mean(th_times)), 1)
        }
    sensitivity_results["meb_thresh"] = meb_stats
    print(f"Sensitivity MEBThresh: {meb_stats}")

    # 4.3 Grid step delta_g in [20.0, 26.0, 28.0]
    grid_stats = {}
    for dg in [20.0, 26.0, 28.0]:
        dg_times = []
        for run_idx in range(30):
            r_rng = random.Random(SEED + 9500 + run_idx)
            n_tgt = r_rng.randint(10, 16)
            t_conf = generate_targets(r_rng, n_tgt)
            sim = Q3Simulation(t_conf, force_grid=True, delta_g=dg, rng=r_rng)
            summ, _ = sim.run()
            dg_times.append(summ["virtual_time"])
        grid_stats[f"delta_g_{dg}"] = {
            "mean_time": round(float(np.mean(dg_times)), 1)
        }
    sensitivity_results["grid_step"] = grid_stats
    print(f"Sensitivity GridStep: {grid_stats}")

    with open(os.path.join(log_dir_1, "q3_sensitivity_summary.json"), "w", encoding="utf-8") as f:
        json.dump(sensitivity_results, f, indent=2)
    with open(os.path.join(log_dir_2, "q3_sensitivity_summary.json"), "w", encoding="utf-8") as f:
        json.dump(sensitivity_results, f, indent=2)

    total_suite_time = round(time.time() - t_suite_start, 2)
    print(f"\n=== Full Benchmark Suite Completed in {total_suite_time} s ===")

if __name__ == "__main__":
    main()
