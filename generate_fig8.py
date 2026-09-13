import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# Compact aspect ratio so font sizes are prominent and large
fig, ax = plt.subplots(figsize=(10.2, 4.8), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis('off')

def draw_card(x, y, w, h, title, items, border_color='#1f497d', header_color='#1f497d', fill_color='#ffffff'):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle='square,pad=0',
                                  linewidth=1.3, edgecolor=border_color, facecolor=fill_color, zorder=3)
    ax.add_patch(rect)
    ax.plot([x, x + w], [y + h - 3.8, y + h - 3.8], color=border_color, linewidth=1.1, zorder=4)
    ax.text(x + w/2, y + h - 1.9, title, ha='center', va='center',
            fontsize=12.5, fontweight='bold', color=header_color, zorder=4)
    for i, it in enumerate(items):
        ax.text(x + 1.0, y + h - 6.2 - i * 3.0, it, ha='left', va='center',
                fontsize=11.0, color='#111111', zorder=4)

# Upper Area
rect_main = patches.Rectangle((1.2, 26.2), 97.6, 22.6, linewidth=1.2,
                              edgecolor='#2f5597', facecolor='#f4f7fb', linestyle='--', zorder=1)
ax.add_patch(rect_main)
ax.text(3.0, 46.4, '【理论保证主链】 负责无盲区发现、真值几何包含与有限步收敛兜底',
        fontsize=13.0, fontweight='bold', color='#1f497d', zorder=2)

draw_card(3.0, 28.0, 21.8, 16.0, '25点双环拓扑巡航',
          ['- 命题5: 凸包全向可测',
           '- 外环内切圆 R=1806 m',
           '- 保证未知朝向首次捕获'],
          border_color='#2f5597', header_color='#1f497d')

draw_card(27.4, 28.0, 21.8, 16.0, '示向角楔半平面交会',
          ['- 引理1: 误差确界 ±1°',
           '- 凸集包含真值 s∈K_{c,k}^+',
           '- 旋转卡壳在线算几何直径'],
          border_color='#2f5597', header_color='#1f497d')

draw_card(51.8, 28.0, 21.8, 16.0, 'MEB判据与网格兜底',
          ['- 判据2: MEB≤19.5m 清除',
           '- 引理2: Δg=26m 网格剖分',
           '- 保证有限步 M_c 必然清除'],
          border_color='#2f5597', header_color='#1f497d')

draw_card(76.2, 28.0, 21.8, 16.0, '双条件完备终止认证',
          ['- 准则3: 有效频道清除完毕',
           '- 命题6: 全网确认为负退出',
           '- 证明系统有限步内必终止'],
          border_color='#2f5597', header_color='#1f497d')

for xs in [24.8, 49.2, 73.6]:
    ax.annotate('', xy=(xs + 2.5, 36.0), xytext=(xs, 36.0),
                arrowprops=dict(arrowstyle='->,head_width=0.42,head_length=0.6', lw=1.6, color='#2f5597'), zorder=5)

# Lower Area
rect_heur = patches.Rectangle((1.2, 1.2), 97.6, 22.6, linewidth=1.2,
                              edgecolor='#c55a11', facecolor='#fdf8f4', linestyle='--', zorder=1)
ax.add_patch(rect_heur)
ax.text(3.0, 21.4, '【启发式效率支路】 负责压缩长尾路径、抑制盲侧往复与降低任务耗时',
        fontsize=13.0, fontweight='bold', color='#833c0c', zorder=2)

draw_card(5.5, 3.0, 27.5, 16.0, '主动 Minimax 选址机动',
          ['- 问题二序贯优化选点准则迁移',
           '- 优化 GDOP 视角并抑制径向拉伸',
           '- 引入机器狗机动安全边界约束'],
          border_color='#c55a11', header_color='#833c0c')

draw_card(36.2, 3.0, 27.5, 16.0, '对称镜像重捕获机动',
          ['- 遭遇负观测时沿中轴对称探测',
           '- 快速判定定向源辐射主瓣方向',
           '- 消除盲侧长距离往复无效移动'],
          border_color='#c55a11', header_color='#833c0c')

draw_card(67.0, 3.0, 27.5, 16.0, '自适应尾部前瞻探测',
          ['- 判据3: 几何相容代理时延增益',
           '- 提前触发高置信度收敛判定',
           '- 100组对照实验减少40.2%尝试'],
          border_color='#c55a11', header_color='#833c0c')

for xs in [33.0, 63.7]:
    ax.annotate('', xy=(xs + 3.1, 11.0), xytext=(xs, 11.0),
                arrowprops=dict(arrowstyle='->,head_width=0.42,head_length=0.6', lw=1.6, color='#c55a11'), zorder=5)

# Inter-track feedback
ax.annotate('', xy=(19.0, 19.0), xytext=(38.0, 28.0),
            arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.5', lw=1.3, color='#444444', linestyle='--'), zorder=5)
ax.text(27.0, 23.8, '触发主动选点', fontsize=11.0, fontweight='bold', color='#222222', ha='center',
        bbox=dict(boxstyle='square,pad=0.25', fc='white', ec='#888888', lw=0.8), zorder=6)

ax.annotate('', xy=(62.5, 28.0), xytext=(80.5, 19.0),
            arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.5', lw=1.3, color='#444444', linestyle='--'), zorder=5)
ax.text(73.0, 23.8, '提前收敛清除', fontsize=11.0, fontweight='bold', color='#222222', ha='center',
        bbox=dict(boxstyle='square,pad=0.25', fc='white', ec='#888888', lw=0.8), zorder=6)

plt.tight_layout()
plt.savefig(r'images/fig_q4_system_architecture.png', bbox_inches='tight', pad_inches=0.03)
plt.close()
print('Success!')
