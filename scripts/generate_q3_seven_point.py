import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Polygon, FancyArrowPatch
import numpy as np
import json
import random

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simulation_q3_benchmark import generate_targets

# Configure fonts safely for Chinese rendering
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Create 1x2 side-by-side dual panel figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.2, 7.6), dpi=300)

R_target = 1800.0
R_ring = 1140.0
R_min = 1000.0

# 7 Base Stations coordinates
stations = [(0.0, 0.0)]
station_names = ['Q0 (中心基准站)', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6']
for m in range(6):
    angle = m * np.pi / 3.0
    x = R_ring * np.cos(angle)
    y = R_ring * np.sin(angle)
    stations.append((x, y))

# =========================================================================
# PANEL (A): 七点正六边形蜂窝全域覆盖几何构型与完备性证明
# =========================================================================
ax1.set_aspect('equal')

# Target Area Circle
circle_target1 = Circle((0, 0), R_target, facecolor='#F8FAFC', edgecolor='#2B6CB0', 
                        linestyle='--', linewidth=2.2, label='目标总区域 ($R=1800\\text{ m}$)', zorder=1)
ax1.add_patch(circle_target1)

# Seven coverage disks
colors = ['#E2E8F0', '#BEE3F8', '#C6F6D5', '#FED7D7', '#E9D8FD', '#FEEBC8', '#FEFCBF']
edge_colors = ['#718096', '#3182CE', '#38A169', '#E53E3E', '#805AD5', '#DD6B20', '#D69E2E']

for i, (P, col, ecol) in enumerate(zip(stations, colors, edge_colors)):
    lbl = '基准测站感知圆盘 ($R_{\\min}=1000\\text{ m}$)' if i == 0 else None
    disk = Circle(P, R_min, facecolor=col, alpha=0.45, edgecolor=ecol, linewidth=1.4, linestyle='-', zorder=2, label=lbl)
    ax1.add_patch(disk)

# Station markers & custom offsets
offsets = [
    (35, -55),   # Q0
    (35, 30),    # Q1
    (35, 30),    # Q2
    (35, 30),    # Q3
    (35, 25),    # Q4
    (35, 25),    # Q5
    (35, 25)     # Q6
]

for i, (P, name, ecol, off) in enumerate(zip(stations, station_names, edge_colors, offsets)):
    ax1.scatter(P[0], P[1], color=ecol, s=95, edgecolor='#1A202C', linewidth=1.2, zorder=5)
    ax1.text(P[0] + off[0], P[1] + off[1], name, fontsize=9.5, fontweight='bold', color='#1A202C', zorder=6)

# Worst-case point on outer boundary (at 30 degrees)
theta_worst = np.pi / 6.0
x_worst = R_target * np.cos(theta_worst)
y_worst = R_target * np.sin(theta_worst)

ax1.scatter([x_worst], [y_worst], color='#C53030', s=140, marker='*', edgecolor='#1A202C', linewidth=1.5, zorder=7, label='最劣边界极值点 ($30^\\circ$ 方向)')

# Line from Q1 to worst-case point
Q1 = stations[1]
ax1.plot([Q1[0], x_worst], [Q1[1], y_worst], color='#C53030', linestyle='-', linewidth=2.2, zorder=6)

# Annotation for worst-case distance with nice callout box
d_max = np.sqrt((x_worst - Q1[0])**2 + (y_worst - Q1[1])**2)
mid_x = (Q1[0] + x_worst) / 2.0
mid_y = (Q1[1] + y_worst) / 2.0
ax1.annotate(
    f'最远间距 $d_{{\\max}} = {d_max:.2f}\\text{{ m}} < 1000\\text{{ m}}$\n(全场无盲区覆盖严格成立)',
    xy=(mid_x, mid_y),
    xytext=(mid_x - 180, mid_y - 170),
    fontsize=9.2,
    fontweight='bold',
    color='#C53030',
    bbox=dict(boxstyle="round,pad=0.38", facecolor='#FFF5F5', edgecolor='#C53030', linewidth=1.2),
    arrowprops=dict(arrowstyle="->", color='#C53030', lw=1.2, shrinkA=3, shrinkB=3),
    zorder=8
)

# Sector boundary dashed lines
ax1.plot([0, R_target], [0, 0], color='#718096', linestyle=':', linewidth=1.2, zorder=3)
ax1.plot([0, R_target * np.cos(np.pi/3)], [0, R_target * np.sin(np.pi/3)], color='#718096', linestyle=':', linewidth=1.2, zorder=3)
ax1.plot([0, R_target * np.cos(np.pi/6)], [0, R_target * np.sin(np.pi/6)], color='#E53E3E', linestyle='-.', linewidth=1.2, alpha=0.7, zorder=3)

ax1.set_title('(a) 七点正六边形对称蜂窝覆盖几何构型与完备性验证', fontsize=12.5, fontweight='bold', pad=12)
ax1.set_xlabel('X 坐标 (米)', fontsize=10.5)
ax1.set_ylabel('Y 坐标 (米)', fontsize=10.5)
ax1.set_xlim(-2150, 2150)
ax1.set_ylim(-2150, 2150)
ax1.grid(True, linestyle='--', alpha=0.35, zorder=0)
ax1.legend(loc='upper right', frameon=True, framealpha=0.92, fontsize=8.8)


# =========================================================================
# PANEL (B): 机器狗巡航定位机动航线与全向干扰源清除实测轨迹
# =========================================================================
ax2.set_aspect('equal')

# Target Area Circle
circle_target2 = Circle((0, 0), R_target, facecolor='#F8FAFC', edgecolor='#2B6CB0', 
                        linestyle='--', linewidth=2.2, label='目标总区域 ($R=1800\\text{ m}$)', zorder=1)
ax2.add_patch(circle_target2)

# Load Official Test 1 Log for exact trajectory and actions
log_path = 'C:/Users/23066/Desktop/mathmode/logs/q3_official_test1_log.json'
with open(log_path, 'r', encoding='utf-8') as f:
    logs = json.load(f)

# Extract trajectory points
traj_pts = []
clears = []
for ev in logs:
    if 'robot_pos' in ev:
        p = tuple(ev['robot_pos'])
        if not traj_pts or traj_pts[-1] != p:
            traj_pts.append(p)
    if ev.get('event_type') == 'clear_attempt' and ev.get('details', {}).get('result') == 'success':
        clears.append(tuple(ev['robot_pos']))

traj_pts = np.array(traj_pts)
clears = np.array(clears)

# Plot robot trajectory
ax2.plot(traj_pts[:, 0], traj_pts[:, 1], color='#3182CE', linestyle='-', linewidth=1.8, alpha=0.9, zorder=3, label='机器狗巡航定位机动航线')

# Plot 7 base stations
st_arr = np.array(stations)
ax2.scatter(st_arr[:, 0], st_arr[:, 1], color='#ECC94B', s=90, marker='o', edgecolor='#1A202C', linewidth=1.2, zorder=4, label='七点蜂窝基准站')

# Plot Start point
ax2.scatter([0], [0], color='#E53E3E', s=160, marker='P', edgecolor='#1A202C', linewidth=1.2, zorder=6, label='任务起始点 (0, 0)')

# True target positions from Q3 master seed 2026
targets_cfg = generate_targets(random.Random(2026), 11)
tgt_pts = np.array([info['pos'] for info in targets_cfg.values()])

ax2.scatter(tgt_pts[:, 0], tgt_pts[:, 1], color='#C53030', s=120, marker='*', edgecolor='#1A202C', linewidth=1.2, zorder=5, label='全向干扰源真实物理位置')

# Laser clear execution points
ax2.scatter(clears[:, 0], clears[:, 1], color='none', edgecolor='#2E7D32', s=140, marker='o', linewidth=2.0, zorder=6, label='激光物理清除命中点')

ax2.set_title('(b) 机器狗蜂窝巡航与全向干扰源定位清除实测轨迹', fontsize=12.5, fontweight='bold', pad=12)
ax2.set_xlabel('X 坐标 (米)', fontsize=10.5)
ax2.set_ylabel('Y 坐标 (米)', fontsize=10.5)
ax2.set_xlim(-2150, 2150)
ax2.set_ylim(-2150, 2150)
ax2.grid(True, linestyle='--', alpha=0.35, zorder=0)
ax2.legend(loc='lower left', frameon=True, framealpha=0.92, fontsize=8.8)

plt.tight_layout()
output_path = 'C:/Users/23066/Desktop/mathmode/images/fig_q3_seven_point_coverage.png'
plt.savefig(output_path, dpi=300)
plt.close()
print(f"Dual-panel Figure 5 generated successfully at {output_path}")
