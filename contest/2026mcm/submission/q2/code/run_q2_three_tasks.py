from __future__ import annotations

import json
import math
from pathlib import Path
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.ndimage import label

from q2_fast import (
    build_position_outer_polygon,
    conservative_safety_margin,
    evaluate_candidate,
    solve_fast_q2,
    _representative_sources,
    _error_grid,
    FastOptions,
)
from q2_state import FirstObservation, Q2Config, build_state_domain
from run_q2_validation import SCENARIOS

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none'

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_task1_candidate_region_scan(
    step_m: float = 25.0,
    coarse_sources: int = 24,
    coarse_errors: int = 3,
    save_plot: bool = True,
) -> dict[str, object]:
    """任务 1：对圆心场景的保守安全区域 U 进行栅格扫描。"""
    print("Running Task 1: Near-optimal candidate region grid scan")
    first = FirstObservation((0.0, 0.0), 0.0)
    config = Q2Config()
    opts = FastOptions()
    
    poly = build_position_outer_polygon(first, config, opts.circle_sides)
    domain = build_state_domain(first, config)
    sources = _representative_sources(domain, coarse_sources)
    errors = _error_grid(config.error_deg, coarse_errors)
    
    radius = config.receive_min
    x_min_raw = max(vertex[0] - radius for vertex in poly)
    x_max_raw = min(vertex[0] + radius for vertex in poly)
    y_min_raw = max(vertex[1] - radius for vertex in poly)
    y_max_raw = min(vertex[1] + radius for vertex in poly)
    x_min = math.ceil(x_min_raw / step_m) * step_m
    x_max = math.floor(x_max_raw / step_m) * step_m
    y_min = math.ceil(y_min_raw / step_m) * step_m
    y_max = math.floor(y_max_raw / step_m) * step_m
    
    xs = np.arange(x_min, x_max + step_m * 0.5, step_m)
    ys = np.arange(y_min, y_max + step_m * 0.5, step_m)
    X, Y = np.meshgrid(xs, ys)
    
    Z = np.full(X.shape, np.nan)
    safe_mask = np.zeros(X.shape, dtype=bool)
    
    safe_points = []
    t0 = time.perf_counter()
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            pt = (float(X[i, j]), float(Y[i, j]))
            margin = conservative_safety_margin(pt, poly, config.receive_min)
            if margin >= 0:
                safe_mask[i, j] = True
                score = evaluate_candidate(pt, "grid_scan", first, config, poly, sources, errors)
                Z[i, j] = score.worst_posterior_diameter_m
                safe_points.append((pt, score.worst_posterior_diameter_m))
                
    elapsed_scan = time.perf_counter() - t0
    safe_count = len(safe_points)
    j_star = float(np.nanmin(Z))
    best_idx = np.unravel_index(np.nanargmin(Z), Z.shape)
    best_pt = (float(X[best_idx]), float(Y[best_idx]))
    
    print(f"    Grid points in U: {safe_count}, min diameter J* = {j_star:.2f} m at {best_pt}, scan time: {elapsed_scan:.2f}s")
    
    # 计算 tau = 1%、3%、5% 时的指标。
    cell_area_m2 = step_m * step_m
    tau_results = {}
    structure = np.ones((3, 3), dtype=int)
    
    for tau in [0.01, 0.03, 0.05]:
        threshold = (1.0 + tau) * j_star
        in_tau = safe_mask & (Z <= threshold)
        cell_count = int(np.sum(in_tau))
        area_m2 = cell_count * cell_area_m2
        area_km2 = area_m2 / 1e6
        
        labeled_arr, num_features = label(in_tau, structure=structure)
        
        tau_xs = X[in_tau]
        tau_ys = Y[in_tau]
        if len(tau_xs) > 0:
            bbox = {
                "x_min": float(np.min(tau_xs)),
                "x_max": float(np.max(tau_xs)),
                "y_min": float(np.min(tau_ys)),
                "y_max": float(np.max(tau_ys)),
            }
        else:
            bbox = None
            
        tau_results[f"tau_{int(tau*100)}pct"] = {
            "tau": tau,
            "threshold_diameter_m": float(threshold),
            "cell_count": cell_count,
            "area_m2": float(area_m2),
            "area_km2": float(area_km2),
            "connected_components": int(num_features),
            "bounding_box": bbox,
        }
        print(f"    tau = {int(tau*100)}%: Area = {area_km2:.4f} km2, {num_features} connected components, BBox X=[{bbox['x_min']:.0f}, {bbox['x_max']:.0f}], Y=[{bbox['y_min']:.0f}, {bbox['y_max']:.0f}]")
        
    plot_path = None
    if save_plot:
        fig, axes = plt.subplots(
            2, 1, figsize=(7.2, 5.4), dpi=300, sharex=True,
            constrained_layout=True, facecolor="white"
        )
        levels = np.linspace(j_star, j_star * 1.08, 17)
        colors = ["#1e40af", "#047857", "#b45309"]
        styles = ["-", "--", ":"]
        panel_limits = [(360, 660), (-660, -360)]
        recommended = [(839.64, 538.75), (839.64, -538.75)]
        for ax, ylim, point in zip(axes, panel_limits, recommended):
            ax.set_facecolor("white")
            cf = ax.contourf(X, Y, Z, levels=levels, cmap="YlOrRd_r", alpha=0.9)
            for idx, tau in enumerate([0.01, 0.03, 0.05]):
                threshold = (1.0 + tau) * j_star
                ax.contour(
                    X, Y, Z, levels=[threshold], colors=[colors[idx]],
                    linewidths=1.6, linestyles=styles[idx]
                )
            ax.plot(
                point[0], point[1], marker='*', color='#dc2626',
                linestyle='none', markersize=11, zorder=10
            )
            ax.set_xlim(720, 930)
            ax.set_ylim(*ylim)
            ax.set_ylabel('Y 坐标 (m)', fontsize=8)
            ax.tick_params(labelsize=7)
            ax.grid(True, linestyle=':', alpha=0.45, color='#cbd5e1')

        axes[-1].set_xlabel('X 坐标 (m)', fontsize=8)
        legend_handles = []
        for idx, tau in enumerate([0.01, 0.03, 0.05]):
            threshold = (1.0 + tau) * j_star
            handle, = axes[0].plot(
                [], [], color=colors[idx], lw=1.6, linestyle=styles[idx],
                label=f"$\\mathcal{{C}}_{{{int(tau*100)}\\%}}$ ($\\leq {threshold:.1f}$ m)"
            )
            legend_handles.append(handle)
        star, = axes[0].plot(
            [], [], marker='*', color='#dc2626', linestyle='none', markersize=9,
            label='推荐测点'
        )
        legend_handles.append(star)
        axes[0].legend(
            handles=legend_handles, loc='upper right', frameon=False,
            fontsize=7, ncol=2
        )
        cbar = fig.colorbar(cf, ax=axes, shrink=0.92, pad=0.02)
        cbar.set_label(r"最坏后验直径 $\widehat{J}(\mathbf{p})$ (m)", fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        fig.suptitle(
            r'近优候选域 $\mathcal{C}_{\tau}$ 的双侧结构与目标等值线',
            fontsize=10, fontweight='bold'
        )

        plot_path = OUTPUT_DIR / "fig_q2_candidate_contour.png"
        fig.savefig(plot_path, dpi=300)
        fig.savefig(OUTPUT_DIR / "fig_q2_candidate_contour.pdf")
        fig.savefig(OUTPUT_DIR / "fig_q2_candidate_contour.svg")
        fig.savefig(OUTPUT_DIR / "fig_q2_candidate_contour.tiff", dpi=600)
        plt.close(fig)
        print(f"    Saved contour plot to: {plot_path}")
        
    return {
        "step_m": step_m,
        "j_star_m": j_star,
        "best_grid_point_m": best_pt,
        "evaluated_safe_points": safe_count,
        "grid_scan_bounds_m": {
            "x_min": float(x_min), "x_max": float(x_max),
            "y_min": float(y_min), "y_max": float(y_max),
        },
        "elapsed_seconds": elapsed_scan,
        "tau_metrics": tau_results,
        "plot_path": str(plot_path) if plot_path else None,
    }


def run_task2_benchmark(repetitions: int = 20) -> dict[str, object]:
    """任务 2：在全部六个验证场景中对 solve_fast_q2 进行 20 次基准测试。"""
    print(f"Running Task 2: Multi-run benchmark ({repetitions} repetitions per scenario)")
    results = {}
    for sc in SCENARIOS:
        times = []
        best_point = None
        worst_diam = None
        for r in range(repetitions):
            res = solve_fast_q2(sc.first)
            times.append(res["elapsed_seconds"])
            if r == 0:
                rec = res["recommendations"][0]
                best_point = rec["point_m"]
                worst_diam = rec["worst_posterior_diameter_m"]
                
        arr = np.array(times)
        stats = {
            "scenario": sc.name,
            "repetitions": repetitions,
            "mean_s": float(np.mean(arr)),
            "std_s": float(np.std(arr)),
            "median_s": float(np.median(arr)),
            "min_s": float(np.min(arr)),
            "max_s": float(np.max(arr)),
            "p95_s": float(np.percentile(arr, 95)),
            "best_point_m": best_point,
            "worst_posterior_diameter_m": worst_diam,
        }
        results[sc.name] = stats
        print(f"    Scenario '{sc.name}': Mean={stats['mean_s']:.3f}s, Std={stats['std_s']:.3f}s, Median={stats['median_s']:.3f}s, Max={stats['max_s']:.3f}s")
        
    return results


def run_task3_safety_buffer_sensitivity() -> dict[str, object]:
    """任务 3：物理安全缓冲参数（b > 0）的敏感性分析。"""
    
    center_first = FirstObservation((0.0, 0.0), 0.0)
    center_buffers = [0.0, 1.0, 2.0, 5.0, 10.0, 20.0]
    center_results = []
    
    for b in center_buffers:
        res = solve_fast_q2(center_first, safety_buffer_m=b)
        if res["result_status"] == "FAST_NUMERICAL_SOLUTION":
            rec = res["recommendations"][0]
            true_margin = rec["conservative_safety_margin_m"] + b
            center_results.append({
                "buffer_b_m": b,
                "status": "FEASIBLE",
                "point_m": rec["point_m"],
                "movement_m": rec["movement_m"],
                "true_safety_margin_m": float(true_margin),
                "margin_slack_above_buffer_m": float(rec["conservative_safety_margin_m"]),
                "worst_posterior_diameter_m": rec["worst_posterior_diameter_m"],
            })
            print(f"    Center (b={b}m): pt=({rec['point_m'][0]:.1f}, {rec['point_m'][1]:.1f}), move={rec['movement_m']:.1f}m, true_margin={true_margin:.2f}m, D2={rec['worst_posterior_diameter_m']:.2f}m")
        else:
            center_results.append({
                "buffer_b_m": b,
                "status": res["result_status"],
                "point_m": None,
                "movement_m": None,
                "true_safety_margin_m": None,
                "margin_slack_above_buffer_m": None,
                "worst_posterior_diameter_m": None,
            })
            print(f"    Center (b={b}m): INFEASIBLE (U is empty)")
            
    outside_first = FirstObservation((2000.0, 0.0), 180.0)
    outside_buffers = [0.0, 1.0, 10.0, 100.0, 300.0, 340.0, 349.0, 350.0]
    outside_results = []
    
    for b in outside_buffers:
        res = solve_fast_q2(outside_first, safety_buffer_m=b)
        if res["result_status"] == "FAST_NUMERICAL_SOLUTION":
            rec = res["recommendations"][0]
            true_margin = rec["conservative_safety_margin_m"] + b
            outside_results.append({
                "buffer_b_m": b,
                "status": "FEASIBLE",
                "point_m": rec["point_m"],
                "movement_m": rec["movement_m"],
                "true_safety_margin_m": float(true_margin),
                "margin_slack_above_buffer_m": float(rec["conservative_safety_margin_m"]),
                "worst_posterior_diameter_m": rec["worst_posterior_diameter_m"],
            })
            print(f"    Outside (b={b}m): pt=({rec['point_m'][0]:.1f}, {rec['point_m'][1]:.1f}), move={rec['movement_m']:.1f}m, true_margin={true_margin:.2f}m, D2={rec['worst_posterior_diameter_m']:.2f}m")
        else:
            outside_results.append({
                "buffer_b_m": b,
                "status": res["result_status"],
                "point_m": None,
                "movement_m": None,
                "true_safety_margin_m": None,
                "margin_slack_above_buffer_m": None,
                "worst_posterior_diameter_m": None,
            })
            print(f"    Outside (b={b}m): INFEASIBLE (U is empty)")
            
    return {
        "center_scenario": center_results,
        "outside_inward_scenario": outside_results,
    }


def main():
    print("Starting Q2 Deep Enhancement Suite (Tasks 1, 2, 3)")
    
    task1 = run_task1_candidate_region_scan(step_m=25.0, save_plot=True)
    task2 = run_task2_benchmark(repetitions=20)
    task3 = run_task3_safety_buffer_sensitivity()
    
    full_output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "task1_candidate_regions": task1,
        "task2_runtime_benchmark": task2,
        "task3_safety_buffer_sensitivity": task3,
    }
    
    json_path = OUTPUT_DIR / "q2_deep_enhancement_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, ensure_ascii=False, indent=2)
    print(f"\nAll results successfully exported to: {json_path}")


if __name__ == "__main__":
    main()
