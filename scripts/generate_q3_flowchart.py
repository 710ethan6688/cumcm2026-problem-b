import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def generate_q3_flowchart():
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(22, 10), dpi=300)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Exact colors from user specification
    c_yellow_fill = '#FFF1B8'
    c_yellow_border = '#C99A00'
    c_purple_fill = '#E8D9F5'
    c_purple_border = '#7A52A3'
    c_green_fill = '#D9EFD8'
    c_green_border = '#4D8B55'
    
    line_color = '#374151'
    text_color = '#111827'

    nodes = {}
    
    def draw_node(key, text, cx, cy, w=1.5, h=0.72, ntype='yellow', is_oval=False, fsize=13):
        if ntype == 'yellow':
            fill_c, border_c = c_yellow_fill, c_yellow_border
        elif ntype == 'purple':
            fill_c, border_c = c_purple_fill, c_purple_border
        else:
            fill_c, border_c = c_green_fill, c_green_border
            
        boxstyle = f"round,pad=0.2,rounding_size={0.36 if is_oval else 0.12}"
        rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                              boxstyle=boxstyle,
                              facecolor=fill_c,
                              edgecolor=border_c,
                              linewidth=2.4,
                              zorder=3)
        ax.add_patch(rect)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=fsize, fontweight='bold', color=text_color, zorder=4)
        nodes[key] = {'cx': cx, 'cy': cy, 'w': w, 'h': h, 'left': cx-w/2, 'right': cx+w/2, 'top': cy+h/2, 'bottom': cy-h/2}

    def draw_arrow(start, end, label=None, label_offset=(0, 0.18)):
        arrow = FancyArrowPatch(start, end,
                                arrowstyle='-|>,head_length=7,head_width=4.5',
                                color=line_color,
                                linewidth=2.0,
                                zorder=2)
        ax.add_patch(arrow)
        if label:
            lx = (start[0] + end[0])/2 + label_offset[0]
            ly = (start[1] + end[1])/2 + label_offset[1]
            bbox_props = dict(boxstyle='round,pad=0.25', facecolor='#F3F4F6', edgecolor='#9CA3AF', linewidth=0.8, alpha=0.95)
            ax.text(lx, ly, label, ha='center', va='center', fontsize=11, fontweight='bold', color='#1F2937', zorder=5, bbox=bbox_props)

    def draw_poly_arrow(points, label=None, label_idx=0, label_offset=(0, 0.18)):
        for i in range(len(points)-1):
            is_last = (i == len(points)-2)
            arr_style = '-|>,head_length=7,head_width=4.5' if is_last else '-'
            arrow = FancyArrowPatch(points[i], points[i+1],
                                    arrowstyle=arr_style,
                                    color=line_color,
                                    linewidth=2.0,
                                    zorder=2)
            ax.add_patch(arrow)
        if label:
            p1 = points[label_idx]
            p2 = points[label_idx+1]
            lx = (p1[0] + p2[0])/2 + label_offset[0]
            ly = (p1[1] + p2[1])/2 + label_offset[1]
            bbox_props = dict(boxstyle='round,pad=0.25', facecolor='#F3F4F6', edgecolor='#9CA3AF', linewidth=0.8, alpha=0.95)
            ax.text(lx, ly, label, ha='center', va='center', fontsize=11, fontweight='bold', color='#1F2937', zorder=5, bbox=bbox_props)

    # 1. Legend
    ax.text(1.0, 9.4, "图例规范：", fontsize=13, fontweight='bold', color='#374151', va='center')
    
    leg_y = FancyBboxPatch((2.6, 9.15), 0.45, 0.45, boxstyle="round,pad=0.05,rounding_size=0.1", facecolor=c_yellow_fill, edgecolor=c_yellow_border, linewidth=2.2)
    ax.add_patch(leg_y)
    ax.text(3.2, 9.38, "输入 / 观测 / 判断条件", fontsize=12, fontweight='bold', va='center', color='#1F2937')

    leg_p = FancyBboxPatch((6.8, 9.15), 0.45, 0.45, boxstyle="round,pad=0.05,rounding_size=0.1", facecolor=c_purple_fill, edgecolor=c_purple_border, linewidth=2.2)
    ax.add_patch(leg_p)
    ax.text(7.4, 9.38, "计算 / 定位 / 状态更新", fontsize=12, fontweight='bold', va='center', color='#1F2937')

    leg_g = FancyBboxPatch((11.0, 9.15), 0.45, 0.45, boxstyle="round,pad=0.05,rounding_size=0.1", facecolor=c_green_fill, edgecolor=c_green_border, linewidth=2.2)
    ax.add_patch(leg_g)
    ax.text(11.6, 9.38, "清除 / 认证 / 输出退出", fontsize=12, fontweight='bold', va='center', color='#1F2937')

    # 2. Main Nodes
    draw_node('A', '进入测试', cx=1.2, cy=5.5, w=1.5, h=0.72, ntype='yellow', is_oval=True)
    draw_node('B', '初始化状态', cx=3.2, cy=5.5, w=1.6, h=0.72, ntype='purple')
    draw_node('D', '任务完成?', cx=5.3, cy=5.5, w=1.6, h=0.72, ntype='yellow')
    draw_node('Z', '退出测试', cx=5.3, cy=7.8, w=1.6, h=0.72, ntype='green', is_oval=True)
    draw_node('T', '选择任务', cx=7.4, cy=5.5, w=1.5, h=0.72, ntype='yellow')

    draw_node('S', '七点巡检', cx=9.4, cy=6.8, w=1.5, h=0.72, ntype='purple')
    draw_node('L', '目标定位', cx=9.4, cy=4.2, w=1.5, h=0.72, ntype='purple')

    draw_node('P', '存在 pending?', cx=11.6, cy=5.5, w=1.8, h=0.72, ntype='yellow')
    draw_node('PR', '重发原请求', cx=11.6, cy=7.8, w=1.6, h=0.72, ntype='purple')
    draw_node('M', '执行测向', cx=13.9, cy=5.5, w=1.5, h=0.72, ntype='yellow')
    draw_node('O', '观测结果', cx=15.9, cy=5.5, w=1.5, h=0.72, ntype='yellow')

    draw_node('C', '立即清除', cx=19.2, cy=7.0, w=1.6, h=0.72, ntype='green')
    draw_node('NS', '定位阶段?', cx=19.2, cy=4.5, w=1.6, h=0.72, ntype='yellow')
    draw_node('G', '网格清除', cx=19.2, cy=2.4, w=1.6, h=0.72, ntype='green')

    draw_node('R', '更新可能区域', cx=15.9, cy=2.4, w=1.8, h=0.72, ntype='purple')
    draw_node('K', '满足清除条件?', cx=13.1, cy=2.4, w=1.9, h=0.72, ntype='yellow')
    draw_node('Q', '测向次数用尽?', cx=10.3, cy=2.4, w=1.9, h=0.72, ntype='yellow')

    draw_node('U', '更新频道状态', cx=11.6, cy=0.9, w=2.0, h=0.72, ntype='purple')

    # 3. Routing Arrows
    draw_arrow((nodes['A']['right'], 5.5), (nodes['B']['left'], 5.5))
    draw_arrow((nodes['B']['right'], 5.5), (nodes['D']['left'], 5.5))

    draw_arrow((5.3, nodes['D']['top']), (5.3, nodes['Z']['bottom']), label='是', label_offset=(0.28, 0))
    draw_arrow((nodes['D']['right'], 5.5), (nodes['T']['left'], 5.5), label='否', label_offset=(0, 0.22))

    draw_poly_arrow([(nodes['T']['right'], 5.5), (8.3, 6.8), (nodes['S']['left'], 6.8)], label='基准点', label_offset=(-0.1, 0.28))
    draw_poly_arrow([(nodes['T']['right'], 5.5), (8.3, 4.2), (nodes['L']['left'], 4.2)], label='已发现目标', label_offset=(-0.1, -0.28))

    draw_poly_arrow([(nodes['S']['right'], 6.8), (10.4, 6.8), (nodes['P']['left'], 5.7)])
    draw_poly_arrow([(nodes['L']['right'], 4.2), (10.4, 4.2), (nodes['P']['left'], 5.3)])

    draw_arrow((11.6, nodes['P']['top']), (11.6, nodes['PR']['bottom']), label='是', label_offset=(0.28, 0))
    draw_arrow((nodes['P']['right'], 5.5), (nodes['M']['left'], 5.5), label='否', label_offset=(0, 0.22))

    draw_arrow((nodes['M']['right'], 5.5), (nodes['O']['left'], 5.5))

    draw_poly_arrow([(nodes['O']['right'], 5.5), (17.3, 7.0), (nodes['C']['left'], 7.0)], label='near', label_offset=(-0.15, 0.28))
    draw_arrow((15.9, nodes['O']['bottom']), (15.9, nodes['R']['top']), label='direction', label_offset=(0.65, 0))
    draw_poly_arrow([(nodes['O']['right'], 5.5), (17.3, 4.5), (nodes['NS']['left'], 4.5)], label='no_signal', label_offset=(-0.15, -0.28))

    draw_arrow((nodes['R']['left'], 2.4), (nodes['K']['right'], 2.4))

    draw_poly_arrow([(nodes['K']['cx'], nodes['K']['top']), (13.1, 3.4), (17.3, 3.4), (17.3, 6.7), (nodes['C']['left'], 6.7)], label='是', label_idx=0, label_offset=(0.3, 0.35))

    draw_arrow((nodes['K']['left'], 2.4), (nodes['Q']['right'], 2.4), label='否', label_offset=(0, 0.22))

    draw_poly_arrow([(nodes['Q']['left'], 2.4), (8.2, 2.4), (8.2, 4.2), (nodes['L']['left'], 4.2)], label='否 (继续定位)', label_idx=0, label_offset=(-0.1, -0.28))

    draw_poly_arrow([(nodes['Q']['cx'], nodes['Q']['bottom']), (10.3, 1.6), (19.2, 1.6), (nodes['G']['cx'], nodes['G']['bottom'])], label='是', label_idx=1, label_offset=(-3.5, 0.22))

    draw_arrow((nodes['NS']['cx'], nodes['NS']['bottom']), (nodes['G']['cx'], nodes['G']['top']), label='是', label_offset=(0.28, 0))

    bus_x = 20.8
    draw_poly_arrow([(nodes['PR']['right'], 7.8), (bus_x, 7.8), (bus_x, 0.9), (nodes['U']['right'], 0.9)])
    draw_arrow((nodes['C']['right'], 7.0), (bus_x, 7.0))
    draw_arrow((nodes['NS']['right'], 4.5), (bus_x, 4.5), label='否', label_offset=(-0.35, 0.22))
    draw_arrow((nodes['G']['right'], 2.4), (bus_x, 2.4))

    draw_poly_arrow([(nodes['U']['left'], 0.9), (5.3, 0.9), (nodes['D']['cx'], nodes['D']['bottom'])])

    plt.tight_layout()
    
    img_dir = r"c:\Users\23066\Desktop\mathmode\images"
    os.makedirs(img_dir, exist_ok=True)
    out_png = os.path.join(img_dir, "fig_q3_flowchart.png")
    out_pdf = os.path.join(img_dir, "fig_q3_flowchart.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(out_pdf, bbox_inches='tight', facecolor='white')
    print(f"Generated {out_png} and {out_pdf}")

if __name__ == '__main__':
    generate_q3_flowchart()
