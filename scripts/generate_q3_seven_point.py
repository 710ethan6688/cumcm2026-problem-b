import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Polygon, FancyArrowPatch
import numpy as np

# Configure fonts safely
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(9.5, 9.0), dpi=300)
ax.set_aspect('equal')

# Target Area Circle
R_target = 1800.0
circle_target = Circle((0, 0), R_target, facecolor='#EDF2F7', edgecolor='#2B6CB0', 
                       linestyle='--', linewidth=2.2, label='目标总区域 (半径 1800 m)', zorder=1)
ax.add_patch(circle_target)

# Seven Stations
R_ring = 1140.0
R_min = 1000.0

stations = [(0.0, 0.0)]
station_names = ['Q0 (中心基准站)']
for m in range(6):
    angle = m * np.pi / 3.0
    x = R_ring * np.cos(angle)
    y = R_ring * np.sin(angle)
    stations.append((x, y))
    station_names.append(f'Q{m+1}')

colors = ['#E2E8F0', '#BEE3F8', '#C6F6D5', '#FED7D7', '#E9D8FD', '#FEEBC8', '#FEFCBF']
edge_colors = ['#718096', '#3182CE', '#38A169', '#E53E3E', '#805AD5', '#DD6B20', '#D69E2E']

# Plot coverage disks
for i, (P, col, ecol) in enumerate(zip(stations, colors, edge_colors)):
    disk = Circle(P, R_min, facecolor=col, alpha=0.35, edgecolor=ecol, linewidth=1.4, linestyle='-', zorder=2)
    ax.add_patch(disk)

# Plot station markers
for i, (P, name, ecol) in enumerate(zip(stations, station_names, edge_colors)):
    ax.scatter(P[0], P[1], color=ecol, s=90, edgecolor='#1A202C', linewidth=1.2, zorder=5)
    offset = (35, 35) if i != 0 else (35, -45)
    ax.text(P[0] + offset[0], P[1] + offset[1], name, fontsize=10, fontweight='bold', color='#1A202C', zorder=6)

# Worst-case point on outer boundary (at 30 degrees)
theta_worst = np.pi / 6.0
x_worst = R_target * np.cos(theta_worst)
y_worst = R_target * np.sin(theta_worst)

ax.scatter([x_worst], [y_worst], color='#C53030', s=130, marker='*', edgecolor='#1A202C', linewidth=1.5, zorder=7, label='最劣极值点 (边界 30° 角点)')

# Line from Q1 to worst-case point
Q1 = stations[1]
ax.plot([Q1[0], x_worst], [Q1[1], y_worst], color='#C53030', linestyle='-', linewidth=2.0, zorder=6)

# Annotation for worst-case distance
d_max = np.sqrt((x_worst - Q1[0])**2 + (y_worst - Q1[1])**2)
mid_x = (Q1[0] + x_worst) / 2.0
mid_y = (Q1[1] + y_worst) / 2.0
ax.text(mid_x + 30, mid_y - 70, f'最远间距 d_max = {d_max:.2f} m < 1000 m', 
        fontsize=10.5, fontweight='bold', color='#C53030', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFF5F5', edgecolor='#C53030', linewidth=1.2), zorder=8)

# Sector boundary dashed lines
ax.plot([0, R_target], [0, 0], color='#718096', linestyle=':', linewidth=1.2, zorder=3)
ax.plot([0, R_target * np.cos(np.pi/3)], [0, R_target * np.sin(np.pi/3)], color='#718096', linestyle=':', linewidth=1.2, zorder=3)
ax.plot([0, R_target * np.cos(np.pi/6)], [0, R_target * np.sin(np.pi/6)], color='#E53E3E', linestyle='-.', linewidth=1.2, alpha=0.7, zorder=3)

# Add title and labels
ax.set_title('七点正六边形对称蜂窝覆盖几何构型与最劣边界完备性验证', fontsize=13.5, fontweight='bold', pad=15)
ax.set_xlabel('X 坐标 (米)', fontsize=11)
ax.set_ylabel('Y 坐标 (米)', fontsize=11)
ax.set_xlim(-2150, 2150)
ax.set_ylim(-2150, 2150)
ax.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9.5)

plt.tight_layout()
plt.savefig('C:/Users/23066/Desktop/mathmode/images/fig_q3_seven_point_coverage.png', dpi=300)
print("Seven point coverage figure generated successfully.")
