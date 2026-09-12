import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle

# Configure fonts safely
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)

# ==================== Panel A ====================
target = np.array([500.0, 500.0])
P1 = np.array([120.0, 150.0])
P2 = np.array([880.0, 180.0])
P3 = np.array([480.0, 920.0])
stations = [P1, P2, P3]
station_names = ['检测基站 P1', '检测基站 P2', '检测基站 P3']
colors = ['#1f77b4', '#2ca02c', '#9467bd']

ax1.set_title('(a) 多站测向角域交会生成定位多边形', fontsize=13, fontweight='bold', pad=14)
eps_deg = 4.5
ray_len = 1000.0

halfplanes = []
for i, (P, name, col) in enumerate(zip(stations, station_names, colors)):
    angle = np.arctan2(target[1] - P[1], target[0] - P[0])
    a_min = angle - np.radians(eps_deg)
    a_max = angle + np.radians(eps_deg)
    
    p_left = P + ray_len * np.array([np.cos(a_max), np.sin(a_max)])
    p_right = P + ray_len * np.array([np.cos(a_min), np.sin(a_min)])
    
    wedge_coords = [P, p_left, p_right]
    poly_wedge = Polygon(wedge_coords, closed=True, facecolor=col, alpha=0.15, edgecolor=col, linestyle='--', linewidth=1.2)
    ax1.add_patch(poly_wedge)
    
    u_max = np.array([np.cos(a_max), np.sin(a_max)])
    u_min = np.array([np.cos(a_min), np.sin(a_min)])
    n_l = np.array([u_max[1], -u_max[0]])
    n_r = np.array([-u_min[1], u_min[0]])
    halfplanes.append((n_l, np.dot(n_l, P)))
    halfplanes.append((n_r, np.dot(n_r, P)))
    
    ax1.plot([P[0], target[0]], [P[1], target[1]], color=col, linestyle=':', alpha=0.7)
    ax1.plot(P[0], P[1], 'o', color=col, markersize=8)
    offset = np.array([-65, -35]) if i != 2 else np.array([15, 15])
    ax1.text(P[0] + offset[0], P[1] + offset[1], name, fontsize=10.5, fontweight='bold', color=col)

lines = halfplanes
candidate_pts = []
for i in range(len(lines)):
    for j in range(i+1, len(lines)):
        A_mat = np.array([lines[i][0], lines[j][0]])
        b_vec = np.array([lines[i][1], lines[j][1]])
        if np.abs(np.linalg.det(A_mat)) > 1e-5:
            pt = np.linalg.solve(A_mat, b_vec)
            feasible = True
            for n_k, c_k in lines:
                if np.dot(n_k, pt) < c_k - 1e-4:
                    feasible = False
                    break
            if feasible:
                candidate_pts.append(pt)

candidate_pts = np.array(candidate_pts)
centroid = np.mean(candidate_pts, axis=0)
angles = np.arctan2(candidate_pts[:, 1] - centroid[1], candidate_pts[:, 0] - centroid[0])
poly_R = candidate_pts[np.argsort(angles)]

poly_patch_A = Polygon(poly_R, closed=True, facecolor='#e6550d', alpha=0.6, edgecolor='darkred', linewidth=2.2, label='交会定位多边形 R')
ax1.add_patch(poly_patch_A)
ax1.plot(target[0], target[1], 'r*', markersize=14, label='真实目标源 s')

ax1.set_xlim(0, 1000)
ax1.set_ylim(0, 1000)
ax1.set_xlabel('X 坐标 / m', fontsize=11)
ax1.set_ylabel('Y 坐标 / m', fontsize=11)
ax1.grid(True, linestyle='--', alpha=0.4)
ax1.legend(loc='lower left', fontsize=10, framealpha=0.9)

# ==================== Panel B ====================
ax2.set_title('(b) 旋转卡壳提取直径与圆盘覆盖判定', fontsize=13, fontweight='bold', pad=14)

poly_B = np.array([
    [2.2, 2.0],
    [5.8, 1.2],
    [8.0, 3.5],
    [7.2, 6.6],
    [3.8, 7.6],
    [1.5, 5.0]
])

poly_patch_B = Polygon(poly_B, closed=True, facecolor='#fee6ce', edgecolor='#e6550d', linewidth=2.2, label='定位凸多边形 R')
ax2.add_patch(poly_patch_B)

a_star = poly_B[1] # (5.8, 1.2)
b_star = poly_B[4] # (3.8, 7.6)
center = (a_star + b_star) / 2.0
D = np.linalg.norm(b_star - a_star)
R = D / 2.0

circle = Circle(center, R, facecolor='#c6dbef', alpha=0.32, edgecolor='#3182bd', linestyle='-', linewidth=2, label='直径圆盘 C* (半径 R=D/2)')
ax2.add_patch(circle)

# Diameter segment
ax2.plot([a_star[0], b_star[0]], [a_star[1], b_star[1]], 'r--', linewidth=2.2, label='区域直径 D (最远点对)')
ax2.plot([a_star[0], b_star[0]], [a_star[1], b_star[1]], 'ro', markersize=8)
ax2.plot(center[0], center[1], 'kx', markersize=9, markeredgewidth=2.2)
ax2.text(center[0]+0.2, center[1], '圆心 c*', fontsize=10.5, fontweight='bold')

# Rotating calipers lines
dir_tangent = (b_star - a_star) / D
dir_perp = np.array([-dir_tangent[1], dir_tangent[0]])
line_len = 3.6
l1_start = a_star - line_len * dir_perp
l1_end = a_star + line_len * dir_perp
l2_start = b_star - line_len * dir_perp
l2_end = b_star + line_len * dir_perp

ax2.plot([l1_start[0], l1_end[0]], [l1_start[1], l1_end[1]], color='#756bb1', linestyle='-.', linewidth=1.6, label='平行外切支撑线')
ax2.plot([l2_start[0], l2_end[0]], [l2_start[1], l2_end[1]], color='#756bb1', linestyle='-.', linewidth=1.6)

# Labels
ax2.text(b_star[0]-1.4, b_star[1]+0.25, 'b* (顶点 v4)', fontsize=10.5, color='red', fontweight='bold')
ax2.text(a_star[0]+0.25, a_star[1]-0.25, 'a* (顶点 v1)', fontsize=10.5, color='red', fontweight='bold')

ax2.text(poly_B[0][0]+0.15, poly_B[0][1]-0.3, 'v0', fontsize=10, color='#333333')
ax2.text(poly_B[2][0]+0.2, poly_B[2][1]-0.15, 'v2', fontsize=10, color='#333333')
ax2.text(poly_B[3][0]+0.2, poly_B[3][1]+0.1, 'v3', fontsize=10, color='#333333')
ax2.text(poly_B[5][0]-0.45, poly_B[5][1]-0.1, 'v5', fontsize=10, color='#333333')

for v in poly_B:
    ax2.plot(v[0], v[1], 'o', color='#3182bd', markersize=6)

ax2.set_xlim(0, 10)
ax2.set_ylim(0, 9.2)
ax2.set_xlabel('相对 X 坐标', fontsize=11)
ax2.set_ylabel('相对 Y 坐标', fontsize=11)
ax2.grid(True, linestyle='--', alpha=0.4)
ax2.legend(loc='lower left', fontsize=9.2, framealpha=0.9)

# ==================== Panel C ====================
ax3.set_title('(c) 理论反例：正三角形无法被直径圆覆盖', fontsize=13, fontweight='bold', pad=14)

side = 4.0
A = np.array([1.0, 1.5])
B = np.array([1.0 + side, 1.5])
h = np.sqrt(3)/2.0 * side
C = np.array([1.0 + side/2.0, 1.5 + h])
tri = np.vstack([A, B, C])

tri_patch = Polygon(tri, closed=True, facecolor='#fcbba1', alpha=0.6, edgecolor='#cb181d', linewidth=2.2, label='正三角形 ABC (边长 D)')
ax3.add_patch(tri_patch)

c_tri = (A + B) / 2.0
r_tri = side / 2.0
circle_tri = Circle(c_tri, r_tri, facecolor='#c6dbef', alpha=0.35, edgecolor='#2171b5', linestyle='--', linewidth=2, label='底边直径闭圆盘 (半径 R=0.5D)')
ax3.add_patch(circle_tri)

ax3.plot([A[0], B[0]], [A[1], B[1]], 'ko', markersize=7)
ax3.text(A[0]-0.55, A[1]-0.35, '端点 A(a*)', fontsize=10.5, fontweight='bold')
ax3.text(B[0]+0.1, B[1]-0.35, '端点 B(b*)', fontsize=10.5, fontweight='bold')

ax3.plot(C[0], C[1], 'ro', markersize=9)
ax3.text(C[0]-0.8, C[1]+0.3, '顶点 C (违规见证点)', fontsize=11, fontweight='bold', color='darkred')

ax3.plot(c_tri[0], c_tri[1], 'kx', markersize=9, markeredgewidth=2.2)
ax3.text(c_tri[0]-0.25, c_tri[1]-0.4, '圆心 c*', fontsize=10.5, fontweight='bold')

ax3.plot([C[0], c_tri[0]], [C[1], c_tri[1]], 'r:', linewidth=2, label='中心高 h = 0.866 D')

top_of_circle = c_tri + np.array([0, r_tri])
ax3.plot(top_of_circle[0], top_of_circle[1], 'b_', markersize=14, markeredgewidth=2.5)

ax3.annotate('外突越界量\nΔ = 0.366 D', 
             xy=(C[0], (C[1]+top_of_circle[1])/2.0), 
             xytext=(C[0]+0.75, (C[1]+top_of_circle[1])/2.0 - 0.2),
             arrowprops=dict(arrowstyle='->', color='red', lw=1.8),
             fontsize=10.5, color='darkred', fontweight='bold')

ax3.set_xlim(0, 6)
ax3.set_ylim(0, 6)
ax3.set_aspect('equal')
ax3.set_xlabel('几何横坐标', fontsize=11)
ax3.set_ylabel('几何纵坐标', fontsize=11)
ax3.grid(True, linestyle='--', alpha=0.4)
ax3.legend(loc='lower left', fontsize=9.5, framealpha=0.9)

plt.tight_layout()
plt.savefig('images/fig_q1_dual_panel.png', dpi=300, bbox_inches='tight')
print('Figure saved to images/fig_q1_dual_panel.png')
