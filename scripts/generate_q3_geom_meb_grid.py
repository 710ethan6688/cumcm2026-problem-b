import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Polygon, Rectangle
import numpy as np

# Configure fonts safely
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5.2), dpi=300)

# ----------------- Panel 1: Angular Wedges Intersection -----------------
ax1.set_title('(a) 有界误差测向角楔求交与相容外包收缩', fontsize=11.5, fontweight='bold', pad=12)
P1 = np.array([0.0, 0.0])
P2 = np.array([300.0, 50.0])
P3 = np.array([120.0, 320.0])
target = np.array([160.0, 180.0])

stations = [P1, P2, P3]
s_names = ['测站 1', '测站 2', '测站 3']
colors = ['#3182CE', '#38A169', '#805AD5']

for P, name, col in zip(stations, s_names, colors):
    ang = np.arctan2(target[1] - P[1], target[0] - P[0])
    a_min = ang - np.radians(4.0)
    a_max = ang + np.radians(4.0)
    ray_len = 380.0
    p_l = P + ray_len * np.array([np.cos(a_max), np.sin(a_max)])
    p_r = P + ray_len * np.array([np.cos(a_min), np.sin(a_min)])
    wedge = Polygon([P, p_l, p_r], closed=True, facecolor=col, alpha=0.18, edgecolor=col, linestyle='--', linewidth=1.2)
    ax1.add_patch(wedge)
    ax1.scatter(P[0], P[1], color=col, s=70, zorder=5)
    ax1.text(P[0] - 15, P[1] - 25, name, fontsize=9.5, fontweight='bold', color=col)

# Intersected Polygon
poly_pts = np.array([[152, 172], [168, 171], [172, 186], [158, 192], [149, 182]])
poly_patch = Polygon(poly_pts, closed=True, facecolor='#E53E3E', alpha=0.6, edgecolor='#9B2C2C', linewidth=1.8, zorder=6, label='相容外包凸多边形 K+')
ax1.add_patch(poly_patch)
ax1.scatter([target[0]], [target[1]], color='#1A202C', s=60, marker='x', linewidth=2.0, zorder=7, label='真实目标位置 s_c')

ax1.set_xlim(-50, 380)
ax1.set_ylim(-40, 360)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.5)
ax1.legend(loc='upper right', fontsize=8.5)

# ----------------- Panel 2: Minimal Enclosing Ball (MEB) -----------------
ax2.set_title('(b) 最小外接圆判定与圆心清除保证 (r* <= 19.5 m)', fontsize=11.5, fontweight='bold', pad=12)

# Zoom in on polygon
poly_local = np.array([[10, 5], [28, 8], [34, 25], [18, 35], [5, 22]])
center_meb = np.array([19.2, 19.8])
r_meb = 18.2

poly_patch2 = Polygon(poly_local, closed=True, facecolor='#BEE3F8', alpha=0.5, edgecolor='#2B6CB0', linewidth=1.8, zorder=3, label='认证外包区域 K+')
ax2.add_patch(poly_patch2)

# MEB Circle
meb_circle = Circle(center_meb, r_meb, facecolor='#FEFCBF', alpha=0.3, edgecolor='#D69E2E', linestyle='-', linewidth=2.0, zorder=2, label=f'最小外接圆 (r* = {r_meb:.1f} m)')
ax2.add_patch(meb_circle)

# 20m Physical clear range from center
clear_circle = Circle(center_meb, 20.0, facecolor='none', edgecolor='#38A169', linestyle='--', linewidth=1.8, zorder=2, label='物理清除边界 (R_clear = 20 m)')
ax2.add_patch(clear_circle)

# Center and target
ax2.scatter(center_meb[0], center_meb[1], color='#D69E2E', s=90, marker='o', edgecolor='#744210', linewidth=1.5, zorder=6, label='推荐清除点 (MEB 圆心)')
target_local = np.array([16.0, 16.5])
ax2.scatter(target_local[0], target_local[1], color='#C53030', s=70, marker='x', linewidth=2.0, zorder=7, label='目标真值 (严格落入圆内)')

ax2.annotate(f'r* = {r_meb:.1f} m <= 19.5 m\n一次清除必然成功', xy=(center_meb[0], center_meb[1]), xytext=(center_meb[0] + 8, center_meb[1] - 16),
             arrowprops=dict(arrowstyle="->", color='#744210', linewidth=1.5),
             fontsize=9.5, fontweight='bold', color='#744210',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#FFFFF0', edgecolor='#D69E2E'))

ax2.set_xlim(-5, 45)
ax2.set_ylim(-5, 45)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.5)
ax2.legend(loc='upper left', fontsize=8.2)

# ----------------- Panel 3: 26m Grid Fallback -----------------
ax3.set_title('(c) 26 m 离散有限网格全覆盖兜底清除机制', fontsize=11.5, fontweight='bold', pad=12)

# 2x2 grid demonstration
step = 26.0
grid_origins = [(0, 0), (26, 0), (0, 26), (26, 26)]
for ox, oy in grid_origins:
    rect = Rectangle((ox, oy), step, step, facecolor='#EDF2F7', edgecolor='#4A5568', linestyle='-', linewidth=1.4, zorder=1)
    ax3.add_patch(rect)
    cx, cy = ox + step/2, oy + step/2
    ax3.scatter(cx, cy, color='#4A5568', s=60, marker='s', zorder=4)
    # Circle of radius 20m from center
    c_cov = Circle((cx, cy), 20.0, facecolor='#C6F6D5', alpha=0.25, edgecolor='#38A169', linestyle=':', linewidth=1.2, zorder=2)
    ax3.add_patch(c_cov)

# Highlight active grid cell (bottom left)
active_cx, active_cy = 13.0, 13.0
corner = np.array([26.0, 26.0])
d_corner = np.sqrt((corner[0] - active_cx)**2 + (corner[1] - active_cy)**2)
ax3.plot([active_cx, corner[0]], [active_cy, corner[1]], color='#E53E3E', linestyle='--', linewidth=1.6, zorder=5)
ax3.text(14.0, 21.0, f'最远角点距 d = {d_corner:.2f} m < 20 m', fontsize=9, fontweight='bold', color='#C53030')

# Target in cell
t_grid = np.array([22.0, 20.0])
ax3.scatter(t_grid[0], t_grid[1], color='#C53030', s=70, marker='x', linewidth=2.0, zorder=6, label='单元内任意目标真值')

# Bounding polygon
poly_fallback = np.array([[8, 12], [32, 10], [38, 38], [15, 42]])
poly_fb_patch = Polygon(poly_fallback, closed=True, facecolor='none', edgecolor='#805AD5', linestyle='-', linewidth=2.0, zorder=3, label='宽幅外包多边形')
ax3.add_patch(poly_fb_patch)

ax3.set_xlim(-6, 58)
ax3.set_ylim(-6, 58)
ax3.set_aspect('equal')
ax3.grid(True, linestyle=':', alpha=0.5)
ax3.legend(loc='upper right', fontsize=8.2)

plt.tight_layout()
plt.savefig('C:/Users/23066/Desktop/mathmode/images/fig_q3_geom_meb_grid.png', dpi=300)
print("Geometry MEB and Grid figure generated successfully.")
