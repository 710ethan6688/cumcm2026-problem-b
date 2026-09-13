import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyArrowPatch, Wedge
import matplotlib.patheffects as pe

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

def generate_25point_coverage_figure():
    fig, ax = plt.subplots(figsize=(9.2, 8.8), dpi=300)
    ax.set_aspect('equal')

    R_target = 1800.0
    R_inner = 950.0
    R_outer = 1870.0
    N_ring = 12

    # Target disk
    disk_target = Circle((0, 0), R_target, facecolor='#F7FAFC', edgecolor='#2B6CB0',
                         linestyle='--', linewidth=2.0, label='目标总区域 (半径 1800 m)', zorder=1)
    ax.add_patch(disk_target)

    # Inradius circle of outer 12-gon
    R_inradius = R_outer * math.cos(math.pi / 12.0)
    disk_inradius = Circle((0, 0), R_inradius, facecolor='none', edgecolor='#4A5568',
                           linestyle=':', linewidth=1.2, label=f'外十二边形内切圆 (半径 {R_inradius:.1f} m)', zorder=2)
    ax.add_patch(disk_inradius)

    # 25 points
    center = (0.0, 0.0)
    inner_pts = []
    for i in range(N_ring):
        ang = math.radians(30.0 * i)
        inner_pts.append((R_inner * math.cos(ang), R_inner * math.sin(ang)))
    outer_pts = []
    for i in range(N_ring):
        ang = math.radians(30.0 * i + 15.0)
        outer_pts.append((R_outer * math.cos(ang), R_outer * math.sin(ang)))

    # Outer 12-gon boundary
    poly_outer = Polygon(outer_pts, facecolor='none', edgecolor='#319795', linewidth=1.5, linestyle='-', zorder=3, label='外环十二边形凸包边界')
    ax.add_patch(poly_outer)

    # 36 Triangles
    triangles = []
    for i in range(N_ring):
        ni = (i + 1) % N_ring
        pi = (i - 1) % N_ring
        # Type A: Center - Inner[i] - Inner[ni]
        triangles.append((center, inner_pts[i], inner_pts[ni], '#EBF8FF', '#3182CE'))
        # Type B: Inner[i] - Outer[pi] - Outer[i]
        triangles.append((inner_pts[i], outer_pts[pi], outer_pts[i], '#E6FFFA', '#319795'))
        # Type C: Inner[i] - Inner[ni] - Outer[i]
        triangles.append((inner_pts[i], inner_pts[ni], outer_pts[i], '#FEFCBF', '#D69E2E'))

    for tri, p1, p2, fcol, ecol in [(t[:3], t[0], t[1], t[3], t[4]) for t in triangles]:
        pts = np.array([tri[0], tri[1], tri[2]])
        poly = Polygon(pts, facecolor=fcol, alpha=0.35, edgecolor=ecol, linewidth=0.8, linestyle='-', zorder=2)
        ax.add_patch(poly)

    # Highlight max edge
    max_d = 0.0
    max_p1, max_p2 = None, None
    for p1, p2 in [
        (inner_pts[0], outer_pts[0]),
        (inner_pts[0], outer_pts[-1]),
        (outer_pts[0], outer_pts[1]),
        (inner_pts[0], inner_pts[1]),
        (center, inner_pts[0])
    ]:
        d = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
        if d > max_d:
            max_d = d
            max_p1, max_p2 = p1, p2

    # Draw maximum edge
    ax.plot([max_p1[0], max_p2[0]], [max_p1[1], max_p2[1]], color='#E53E3E', linewidth=2.8, zorder=6)
    mid_x = (max_p1[0] + max_p2[0]) / 2.0
    mid_y = (max_p1[1] + max_p2[1]) / 2.0
    ax.text(mid_x + 60, mid_y - 30, f'最大边长 d_max = 983.60 m < 1000 m\n(严格保证局部多站凸包可观测)',
            fontsize=9.5, fontweight='bold', color='#C53030',
            bbox=dict(boxstyle="round,pad=0.35", facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.2), zorder=8)

    # Plot Stations
    ax.scatter(0, 0, color='#805AD5', s=120, marker='o', edgecolor='#1A202C', linewidth=1.5, zorder=7, label='中心原点基准测站 (1点)')
    in_x = [p[0] for p in inner_pts]
    in_y = [p[1] for p in inner_pts]
    ax.scatter(in_x, in_y, color='#3182CE', s=75, marker='s', edgecolor='#1A202C', linewidth=1.2, zorder=7, label='内环等角基准测站 (12点, 半径950m)')
    out_x = [p[0] for p in outer_pts]
    out_y = [p[1] for p in outer_pts]
    ax.scatter(out_x, out_y, color='#DD6B20', s=75, marker='^', edgecolor='#1A202C', linewidth=1.2, zorder=7, label='外环错位基准测站 (12点, 半径1870m)')

    ax.set_title('问题四：25点双环拓扑剖分与多视角凸包方向完备覆盖构型', fontsize=13.0, fontweight='bold', pad=14)
    ax.set_xlabel('X 坐标 (米)', fontsize=10.5)
    ax.set_ylabel('Y 坐标 (米)', fontsize=10.5)
    ax.set_xlim(-2200, 2200)
    ax.set_ylim(-2200, 2200)
    ax.grid(True, linestyle='--', alpha=0.35, zorder=0)
    ax.legend(loc='upper right', frameon=True, framealpha=0.92, fontsize=8.5)

    plt.tight_layout()
    plt.savefig('C:/Users/23066/Desktop/mathmode/images/fig_q4_25point_coverage.png', dpi=300)
    plt.close()
    print("fig_q4_25point_coverage.png generated.")

def generate_mechanism_figure():
    fig, ax = plt.subplots(figsize=(10.0, 5.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    box_blue = dict(boxstyle="round,pad=0.5", facecolor="#EBF8FF", edgecolor="#3182CE", linewidth=1.6)
    box_green = dict(boxstyle="round,pad=0.5", facecolor="#F0FFF4", edgecolor="#38A169", linewidth=1.6)
    box_orange = dict(boxstyle="round,pad=0.5", facecolor="#FFFAF0", edgecolor="#DD6B20", linewidth=1.6)
    box_purple = dict(boxstyle="round,pad=0.5", facecolor="#FAF5FF", edgecolor="#805AD5", linewidth=1.6)
    box_red = dict(boxstyle="round,pad=0.5", facecolor="#FFF5F5", edgecolor="#E53E3E", linewidth=1.6)

    ax.text(50, 56, "全向—定向混合干扰源自主协同搜索与保证清除系统架构 (V3)",
            fontsize=13.5, fontweight='bold', ha='center', va='center', color='#1A202C')

    ax.text(50, 48, "【理论保证主链（承担完备发现与终局兜底清除责任）】", fontsize=10.5, fontweight='bold', ha='center', va='center', color='#2B6CB0')
    
    ax.text(12, 38, "25点双环覆盖\n方向完备全局搜索\n(命题 5 & 推论 1)", ha='center', va='center', fontsize=9.0, bbox=box_blue)
    ax.text(37, 38, "示向角域交会\n凸外包包含真值\n(引理 1)", ha='center', va='center', fontsize=9.0, bbox=box_blue)
    ax.text(63, 38, "19.5m/20m直接清除\n26m相交网格遍历\n(判据 2 & 引理 2)", ha='center', va='center', fontsize=9.0, bbox=box_green)
    ax.text(88, 38, "双条件退出认证\n有限步完备终止\n(准则 3 & 命题 6)", ha='center', va='center', fontsize=9.0, bbox=box_purple)

    arrow_style = dict(arrowstyle="->", color="#2B6CB0", lw=2.0, mutation_scale=15)
    ax.annotate("", xy=(24.5, 38), xytext=(19.5, 38), arrowprops=arrow_style)
    ax.annotate("", xy=(50.5, 38), xytext=(45.5, 38), arrowprops=arrow_style)
    ax.annotate("", xy=(76.0, 38), xytext=(71.0, 38), arrowprops=arrow_style)

    ax.text(50, 26, "【启发式效率支路（压缩长尾搜索与减少无效清除耗时）】", fontsize=10.5, fontweight='bold', ha='center', va='center', color='#C05621')

    ax.text(25, 14, "距离安全Q2主动探测\n(有限采样与GDOP几何退化最小)", ha='center', va='center', fontsize=8.8, bbox=box_orange)
    ax.text(50, 14, "对称镜像重捕获\n(沿法向中轴对侧二次探测)", ha='center', va='center', fontsize=8.8, bbox=box_orange)
    ax.text(75, 14, "自适应尾部前瞻判据\n(几何相容代理与时间增益判据 3)", ha='center', va='center', fontsize=8.8, bbox=box_red)

    arrow_orange = dict(arrowstyle="->", color="#DD6B20", lw=1.8, mutation_scale=13)
    ax.annotate("", xy=(37.5, 14), xytext=(32.5, 14), arrowprops=arrow_orange)
    ax.annotate("", xy=(62.5, 14), xytext=(57.5, 14), arrowprops=arrow_orange)

    arrow_dashed = dict(arrowstyle="<->", color="#718096", lw=1.5, linestyle="--", mutation_scale=12)
    ax.annotate("", xy=(37, 32.5), xytext=(28, 19.5), arrowprops=arrow_dashed)
    ax.annotate("", xy=(63, 32.5), xytext=(75, 19.5), arrowprops=arrow_dashed)
    ax.text(29, 26, "正示向触发", fontsize=8.0, color="#4A5568", ha='center', va='center')
    ax.text(72, 26, "提前收敛", fontsize=8.0, color="#4A5568", ha='center', va='center')

    ax.text(50, 3, "核心特征：理论主链与启发支路严格分权；非必要不引入高维黑盒；以确定性几何外包保障100%清除完备率",
            fontsize=8.8, color="#4A5568", ha='center', va='center',
            bbox=dict(boxstyle="square,pad=0.4", facecolor="#EDF2F7", edgecolor="none"))

    plt.tight_layout()
    plt.savefig('C:/Users/23066/Desktop/mathmode/images/fig_q4_system_architecture.png', dpi=300)
    plt.close()
    print("fig_q4_system_architecture.png generated.")

if __name__ == '__main__':
    generate_25point_coverage_figure()
    generate_mechanism_figure()
