import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_q2_flowchart():
    fig, ax = plt.subplots(figsize=(15.6, 3.0), dpi=300)
    ax.set_xlim(0, 15.6)
    ax.set_ylim(0, 3.0)
    ax.axis('off')

    # Distinct vibrant colors matching strategy
    c_yellow_bg = '#FFE380'       # Rich warm yellow
    c_yellow_border = '#D48806'   # Deep golden border
    
    c_purple_bg = '#D3ADF7'       # Distinct rich lavender purple
    c_purple_border = '#531DAB'   # Deep violet border
    
    c_green_bg = '#95DE64'        # Fresh vibrant green
    c_green_border = '#237804'    # Deep emerald border
    
    c_neutral_bg = '#EDEDED'      # Noticeable light neutral gray
    c_neutral_border = '#595959'  # Dark slate border

    line_color = '#333333'
    text_color = '#1A1A1A'

    def draw_pill(x, y, w, h, text, bg, border, fontsize=11):
        box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.0,rounding_size=0.35',
                             facecolor=bg, edgecolor=border, linewidth=2.0, zorder=4)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=5, linespacing=1.2)

    def draw_rect(x, y, w, h, text, bg, border, fontsize=11):
        box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.0,rounding_size=0.12',
                             facecolor=bg, edgecolor=border, linewidth=2.0, zorder=4)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=5, linespacing=1.2)

    def draw_diamond(cx, cy, rx, ry, text, bg, border, fontsize=10.5):
        pts = np.array([[cx - rx, cy], [cx, cy + ry], [cx + rx, cy], [cx, cy - ry]])
        poly = Polygon(pts, closed=True, facecolor=bg, edgecolor=border, linewidth=2.0, zorder=4)
        ax.add_patch(poly)
        ax.text(cx, cy, text, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=5, linespacing=1.15)

    def draw_straight_arrow(x1, y1, x2, y2, label=None, label_offset=(0, 0.18)):
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                arrowstyle='-|>', mutation_scale=13,
                                color=line_color, linewidth=1.6, zorder=3)
        ax.add_patch(arrow)
        if label:
            ax.text((x1 + x2)/2 + label_offset[0], (y1 + y2)/2 + label_offset[1], label,
                    ha='center', va='center', fontsize=11, fontweight='bold', color='#1A1A1A', zorder=6)

    y_main = 1.95
    node_h = 0.95

    # 1. Node A (Yellow Pill)
    xA, wA = 0.35, 1.45
    draw_pill(xA, y_main - node_h/2, wA, node_h, '第一测点\n与示向度', c_yellow_bg, c_yellow_border)

    # 2. Node B (Purple Rect)
    xB, wB = 2.20, 1.35
    draw_rect(xB, y_main - node_h/2, wB, node_h, '初始可能\n区域', c_purple_bg, c_purple_border)

    # 3. Node C (Purple Rect)
    xC, wC = 3.95, 1.35
    draw_rect(xC, y_main - node_h/2, wC, node_h, '安全测点\n区域', c_purple_bg, c_purple_border)

    # 4. Node D (Yellow Diamond)
    cxD, rxD, ryD = 6.10, 0.82, 0.58
    draw_diamond(cxD, y_main, rxD, ryD, '存在安全\n测点?', c_yellow_bg, c_yellow_border)

    # 5. Node E (Purple Rect)
    xE, wE = 7.65, 1.45
    draw_rect(xE, y_main - node_h/2, wE, node_h, '候选点粗筛\n24 × 3', c_purple_bg, c_purple_border)

    # 6. Node F (Purple Rect)
    xF, wF = 9.50, 1.55
    draw_rect(xF, y_main - node_h/2, wF, node_h, '局部搜索\n3种子 · 4轮', c_purple_bg, c_purple_border)

    # 7. Node G (Purple Rect)
    xG, wG = 11.45, 1.45
    draw_rect(xG, y_main - node_h/2, wG, node_h, '精细复评\n64 × 7', c_purple_bg, c_purple_border)

    # 8. Node H (Green Pill)
    xH, wH = 13.30, 1.55
    draw_pill(xH, y_main - node_h/2, wH, node_h, '推荐第二\n检测点', c_green_bg, c_green_border)

    # 9. Node X (Neutral Pill)
    y_sub = 0.55
    xX, wX = 7.65, 1.45
    draw_pill(xX, y_sub - node_h/2, wX, node_h, '无可用测点', c_neutral_bg, c_neutral_border, fontsize=10.5)

    # Main arrows
    draw_straight_arrow(xA + wA, y_main, xB, y_main)
    draw_straight_arrow(xB + wB, y_main, xC, y_main)
    draw_straight_arrow(xC + wC, y_main, cxD - rxD, y_main)
    draw_straight_arrow(cxD + rxD, y_main, xE, y_main, label='是', label_offset=(0, 0.20))
    draw_straight_arrow(xE + wE, y_main, xF, y_main)
    draw_straight_arrow(xF + wF, y_main, xG, y_main)
    draw_straight_arrow(xG + wG, y_main, xH, y_main)

    # L-shaped branch for '否' -> Node X
    ax.plot([cxD, cxD, xX - 0.05], [y_main - ryD, y_sub, y_sub], color=line_color, linewidth=1.6, zorder=3)
    arrow_head = FancyArrowPatch((xX - 0.1, y_sub), (xX, y_sub),
                                 arrowstyle='-|>', mutation_scale=13,
                                 color=line_color, linewidth=1.6, zorder=3)
    ax.add_patch(arrow_head)
    ax.text(cxD + 0.22, (y_main - ryD + y_sub)/2, '否', fontsize=11, fontweight='bold', color='#1A1A1A', zorder=6)

    plt.tight_layout()
    os.makedirs('images', exist_ok=True)
    plt.savefig('images/fig_q2_flowchart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Flowchart script updated and executed.')

if __name__ == '__main__':
    create_q2_flowchart()
