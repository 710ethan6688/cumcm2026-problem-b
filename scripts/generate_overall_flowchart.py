import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def generate_overall_flowchart():
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(15, 2.8), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 2.8)
    ax.axis('off')
    
    # Unified color scheme: Soft purple/lavender from user specification
    bg_color = '#E8D9F5'
    border_color = '#7A52A3'
    text_color = '#2B2B2B'
    line_color = '#5F6368'
    
    boxes = [
        {'title': '问题一', 'lines': ['定位区域求解', '直径与覆盖判定'], 'cx': 1.8, 'cy': 1.4, 'w': 2.6, 'h': 1.8},
        {'title': '问题二', 'lines': ['第二测点选择', '安全区域与效果优化'], 'cx': 5.6, 'cy': 1.4, 'w': 2.6, 'h': 1.8},
        {'title': '问题三', 'lines': ['全向源搜索', '在线定位与清除'], 'cx': 9.4, 'cy': 1.4, 'w': 2.6, 'h': 1.8},
        {'title': '问题四', 'lines': ['混合源搜索', '定向盲侧处理'], 'cx': 13.2, 'cy': 1.4, 'w': 2.6, 'h': 1.8}
    ]
    
    arrow_labels = ['几何评价', '主动定位', '定向扩展']
    
    for b in boxes:
        x0 = b['cx'] - b['w'] / 2
        y0 = b['cy'] - b['h'] / 2
        patch = FancyBboxPatch((x0, y0), b['w'], b['h'],
                               boxstyle='round,pad=0.0,rounding_size=0.10',
                               facecolor=bg_color, edgecolor=border_color,
                               linewidth=1.8, zorder=3)
        ax.add_patch(patch)
        
        ax.text(b['cx'], b['cy'] + 0.38, b['title'],
                ha='center', va='center', fontsize=12.5, fontweight='bold',
                color=text_color, zorder=4)
        
        content = '\n'.join(b['lines'])
        ax.text(b['cx'], b['cy'] - 0.28, content,
                ha='center', va='center', fontsize=10.5,
                color=text_color, zorder=4, linespacing=1.35)
        
    for i in range(3):
        b1 = boxes[i]
        b2 = boxes[i+1]
        x_start = b1['cx'] + b1['w'] / 2
        x_end = b2['cx'] - b2['w'] / 2
        y_mid = b1['cy']
        
        arrow = FancyArrowPatch((x_start, y_mid), (x_end, y_mid),
                                arrowstyle='-|>,head_length=6.0,head_width=4.0',
                                color=line_color, linewidth=1.6, zorder=2)
        ax.add_patch(arrow)
        
        badge_x = (x_start + x_end) / 2
        badge_y = y_mid
        badge_text = arrow_labels[i]
        
        ax.text(badge_x, badge_y, badge_text,
                ha='center', va='center', fontsize=9.5, fontweight='normal',
                color='#2B2B2B', zorder=5,
                bbox=dict(boxstyle='square,pad=0.3',
                          facecolor='#FFFFFF', edgecolor='#D9D9D9',
                          linewidth=0.8, alpha=0.98))
        
    plt.tight_layout(pad=0.1)
    
    os.makedirs('images', exist_ok=True)
    pdf_path = os.path.join('images', 'fig_overall_flowchart.pdf')
    png_path = os.path.join('images', 'fig_overall_flowchart.png')
    
    plt.savefig(pdf_path, bbox_inches='tight', dpi=300)
    plt.savefig(png_path, bbox_inches='tight', dpi=300)
    plt.close()
    print('Flowchart generated successfully!')

generate_overall_flowchart()
