import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import numpy as np

def generate_q4_flowchart():
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(19, 7.5), dpi=300)
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # Matching color palette from Q2/Q3
    c_yellow_fill = '#FFF1B8'
    c_yellow_border = '#C99A00'
    c_purple_fill = '#E8D9F5'
    c_purple_border = '#7A52A3'
    c_green_fill = '#D9EFD8'
    c_green_border = '#4D8B55'
    
    line_color = '#374151'
    text_color = '#111827'
    
    nodes = {}
    
    def draw_node(key, text, cx, cy, w=1.5, h=0.72, ntype='yellow', is_oval=False, fsize=10.5):
        if ntype == 'yellow':
            fill_c, border_c = c_yellow_fill, c_yellow_border
        elif ntype == 'purple':
            fill_c, border_c = c_purple_fill, c_purple_border
        else:
            fill_c, border_c = c_green_fill, c_green_border
            
        boxstyle = f'round,pad=0.15,rounding_size={0.36 if is_oval else 0.12}'
        rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                              boxstyle=boxstyle,
                              facecolor=fill_c, edgecolor=border_c,
                              linewidth=2.0, zorder=3)
        ax.add_patch(rect)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=fsize, fontweight='bold', color=text_color, zorder=4, linespacing=1.25)
        nodes[key] = {'cx': cx, 'cy': cy, 'w': w, 'h': h, 'left': cx-w/2, 'right': cx+w/2, 'top': cy+h/2, 'bottom': cy-h/2}

    def draw_arrow(start, end, label=None, label_offset=(0, 0.18)):
        arrow = FancyArrowPatch(start, end,
                                arrowstyle='-|>,head_length=6,head_width=4',
                                color=line_color, linewidth=1.7, zorder=2)
        ax.add_patch(arrow)
        if label:
            lx = (start[0] + end[0])/2 + label_offset[0]
            ly = (start[1] + end[1])/2 + label_offset[1]
            bbox_props = dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#D1D5DB', linewidth=0.8, alpha=0.96)
            ax.text(lx, ly, label, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1F2937', zorder=5, bbox=bbox_props)

    def draw_poly_arrow(points, label=None, label_idx=0, label_offset=(0, 0.18)):
        for i in range(len(points)-1):
            is_last = (i == len(points)-2)
            arrowstyle = '-|>,head_length=6,head_width=4' if is_last else '-'
            arrow = FancyArrowPatch(points[i], points[i+1],
                                    arrowstyle=arrowstyle,
                                    color=line_color, linewidth=1.7, zorder=2)
            ax.add_patch(arrow)
        if label:
            p1 = points[label_idx]
            p2 = points[label_idx+1]
            lx = (p1[0] + p2[0])/2 + label_offset[0]
            ly = (p1[1] + p2[1])/2 + label_offset[1]
            bbox_props = dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#D1D5DB', linewidth=0.8, alpha=0.96)
            ax.text(lx, ly, label, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1F2937', zorder=5, bbox=bbox_props)

    # 1. Legend
    ax.text(0.8, 7.0, '图例规范：', fontsize=11.5, fontweight='bold', color='#374151', va='center')
    
    leg_y = FancyBboxPatch((2.2, 6.8), 0.38, 0.38, boxstyle='round,pad=0.05,rounding_size=0.08', facecolor=c_yellow_fill, edgecolor=c_yellow_border, linewidth=1.8)
    ax.add_patch(leg_y)
    ax.text(2.7, 7.0, '输入 / 观测 / 分支判定', fontsize=10.5, fontweight='bold', va='center', color='#1F2937')

    leg_p = FancyBboxPatch((6.0, 6.8), 0.38, 0.38, boxstyle='round,pad=0.05,rounding_size=0.08', facecolor=c_purple_fill, edgecolor=c_purple_border, linewidth=1.8)
    ax.add_patch(leg_p)
    ax.text(6.5, 7.0, '计算 / 定位 / 状态更新', fontsize=10.5, fontweight='bold', va='center', color='#1F2937')

    leg_g = FancyBboxPatch((9.8, 6.8), 0.38, 0.38, boxstyle='round,pad=0.05,rounding_size=0.08', facecolor=c_green_fill, edgecolor=c_green_border, linewidth=1.8)
    ax.add_patch(leg_g)
    ax.text(10.3, 7.0, '物理清除 / 任务退出', fontsize=10.5, fontweight='bold', va='center', color='#1F2937')

    # 2. Main workflow nodes
    draw_node('A', '25点基准搜索', cx=1.2, cy=4.5, w=1.6, h=0.72, ntype='purple')
    draw_node('O', '初始观测结果', cx=3.4, cy=4.5, w=1.6, h=0.72, ntype='yellow')
    draw_node('C', '实施物理清除', cx=3.4, cy=2.2, w=1.6, h=0.72, ntype='green')
    
    draw_node('R', '目标可能区域', cx=5.7, cy=4.5, w=1.6, h=0.72, ntype='purple')
    draw_node('K', '满足清除条件?', cx=8.0, cy=4.5, w=1.7, h=0.72, ntype='yellow')
    
    draw_node('M', '常规测向机动\n(最多2次)', cx=10.4, cy=4.5, w=1.8, h=0.75, ntype='purple')
    draw_node('O2', '常规观测结果', cx=12.7, cy=4.5, w=1.6, h=0.72, ntype='yellow')
    
    draw_node('MI', '存在安全\n镜像测点?', cx=12.7, cy=6.0, w=1.6, h=0.75, ntype='yellow')
    draw_node('MP', '对称镜像探测', cx=15.1, cy=6.0, w=1.6, h=0.72, ntype='purple')
    
    draw_node('T', '尾部探测\n值得执行?', cx=15.1, cy=4.5, w=1.6, h=0.75, ntype='yellow')
    draw_node('TP', '自适应尾部探测', cx=17.5, cy=4.5, w=1.7, h=0.72, ntype='purple')
    
    draw_node('G', '26m网格\n遍历清除', cx=15.1, cy=2.2, w=1.6, h=0.75, ntype='green')
    
    draw_node('CL', '目标确认清除', cx=9.0, cy=2.2, w=1.6, h=0.72, ntype='green')
    draw_node('U', '更新信道账本', cx=9.0, cy=0.8, w=1.8, h=0.72, ntype='purple')
    
    draw_node('D', '全场目标\n清剿完成?', cx=5.7, cy=0.8, w=1.7, h=0.75, ntype='yellow')
    draw_node('Z', '安全退出测试', cx=2.5, cy=0.8, w=1.7, h=0.72, ntype='green', is_oval=True)

    # 3. Connect arrows
    draw_arrow((nodes['A']['right'], 4.5), (nodes['O']['left'], 4.5))
    draw_arrow((nodes['O']['bottom'], nodes['O']['cy']), (nodes['C']['top'], nodes['C']['cy']), label='≤20m', label_offset=(0.35, 0))
    draw_arrow((nodes['O']['right'], 4.5), (nodes['R']['left'], 4.5), label='测向角', label_offset=(0, 0.2))
    
    draw_arrow((nodes['R']['right'], 4.5), (nodes['K']['left'], 4.5))
    draw_poly_arrow([(nodes['K']['bottom'], nodes['K']['cy']), (8.0, 2.2), (nodes['C']['right'], 2.2)], label='是', label_offset=(0, 0.2))
    draw_arrow((nodes['K']['right'], 4.5), (nodes['M']['left'], 4.5), label='否', label_offset=(0, 0.2))
    
    draw_arrow((nodes['M']['right'], 4.5), (nodes['O2']['left'], 4.5))
    draw_poly_arrow([(nodes['O2']['bottom'], nodes['O2']['cy']), (12.7, 3.4), (5.7, 3.4), (nodes['R']['bottom'], nodes['R']['cy'])], label='测向角更新', label_offset=(-1.5, 0.18))
    
    draw_arrow((nodes['O2']['top'], nodes['O2']['cy']), (nodes['MI']['bottom'], nodes['MI']['cy']), label='盲侧失联', label_offset=(0.5, 0))
    draw_arrow((nodes['MI']['right'], 6.0), (nodes['MP']['left'], 6.0), label='是', label_offset=(0, 0.2))
    draw_arrow((nodes['MI']['bottom'], nodes['MI']['cy']), (nodes['T']['top'], nodes['T']['cy']), label='否', label_offset=(0.25, 0))
    
    draw_poly_arrow([(nodes['MP']['right'], 6.0), (16.5, 6.0), (16.5, 5.4), (nodes['T']['right'], 5.4)], label='无信号', label_offset=(0.35, 0))
    
    draw_arrow((nodes['T']['right'], 4.5), (nodes['TP']['left'], 4.5), label='是', label_offset=(0, 0.2))
    draw_arrow((nodes['T']['bottom'], nodes['T']['cy']), (nodes['G']['top'], nodes['G']['cy']), label='否', label_offset=(0.25, 0))
    
    draw_poly_arrow([(nodes['TP']['bottom'], nodes['TP']['cy']), (17.5, 2.2), (nodes['G']['right'], 2.2)], label='最终网格兜底', label_offset=(0, 0.2))
    
    draw_arrow((nodes['C']['right'], 2.2), (nodes['CL']['left'], 2.2))
    draw_arrow((nodes['G']['left'], 2.2), (nodes['CL']['right'], 2.2))
    
    draw_arrow((nodes['CL']['bottom'], nodes['CL']['cy']), (nodes['U']['top'], nodes['U']['cy']))
    draw_arrow((nodes['U']['left'], 0.8), (nodes['D']['right'], 0.8))
    
    draw_arrow((nodes['D']['left'], 0.8), (nodes['Z']['right'], 0.8), label='是', label_offset=(0, 0.2))
    draw_poly_arrow([(nodes['D']['bottom'], nodes['D']['cy']), (5.7, 0.2), (1.2, 0.2), (nodes['A']['bottom'], nodes['A']['cy'])], label='否 / 下一频段', label_offset=(-1.5, 0.2))

    plt.tight_layout(pad=0.2)
    os.makedirs('images', exist_ok=True)
    pdf_path = os.path.join('images', 'fig_q4_flowchart.pdf')
    png_path = os.path.join('images', 'fig_q4_flowchart.png')
    
    plt.savefig(pdf_path, bbox_inches='tight', dpi=300)
    plt.savefig(png_path, bbox_inches='tight', dpi=300)
    plt.close()
    print('Generated Q4 flowchart successfully!')

if __name__ == '__main__':
    generate_q4_flowchart()
