import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Configure fonts safely
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.5)
ax.axis('off')

# Color palette (Academic clean)
c_env_bg = '#F0F4F8'
c_env_border = '#334E68'

c_state_bg = '#EBF8FF'
c_state_border = '#2B6CB0'

c_auth_bg = '#FEFCBF'
c_auth_border = '#B7791F'

c_cert_bg = '#FEEBC8'
c_cert_border = '#C05621'

c_eff_bg = '#E6FFFA'
c_eff_border = '#234E52'

c_action_bg = '#FAF5FF'
c_action_border = '#6B46C1'

def add_box(ax, xy, width, height, title, items, bg_color, border_color, title_color=None, title_size=11, text_size=9.5):
    if title_color is None:
        title_color = border_color
    box = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.08,rounding_size=0.15",
                         facecolor=bg_color, edgecolor=border_color, linewidth=1.8)
    ax.add_patch(box)
    
    # Title
    ax.text(xy[0] + width/2, xy[1] + height - 0.28, title, 
            ha='center', va='center', fontsize=title_size, fontweight='bold', color=title_color)
    
    # Divider line
    ax.plot([xy[0] + 0.15, xy[0] + width - 0.15], [xy[1] + height - 0.52, xy[1] + height - 0.52],
            color=border_color, linewidth=0.9, alpha=0.6)
    
    # Items
    y_start = xy[1] + height - 0.8
    y_step = (height - 0.95) / max(len(items), 1)
    for i, item in enumerate(items):
        ax.text(xy[0] + 0.25, y_start - i * y_step, item,
                ha='left', va='center', fontsize=text_size, color='#2D3748')

# 1. Physical Environment & Robot Platform (Bottom Left)
add_box(ax, (0.5, 0.6), 4.2, 3.2, 
        "物理运行环境与机动平台", 
        ["• 20 独立频段正交子空间 (10~16 目标)",
         "• 有效接收半径 1000~1500 m (未知)",
         "• 测向仪确界角度误差 [-1°, 1°]",
         "• 机器狗: 直线机动 (5 m/s) 与调谐切换",
         "• 动作集: 测向 / 激光清除 / 异常恢复",
         "• 多模态物理反馈: 方向角 / 近场 / 成功 / 失败"],
        c_env_bg, c_env_border, title_size=11.5)

# 2. Immutable Authoritative History (Top Left)
add_box(ax, (0.5, 4.7), 4.2, 3.2,
        "不可变权威历史序列 H_auth",
        ["• 绝对真理源: 时间严格有序追加序列",
         "• 完整记录: (动作 a_k, 物理反馈 y_k)",
         "• 事务一致性与幂等恢复保障机制",
         "• 单向因果驱动: 支撑硬约束确定性重构",
         "• 杜绝决策层直接篡改历史反馈数据",
         "• 提供全流程可审计、可验证数学凭据"],
        c_auth_bg, c_auth_border, title_size=11.5)

# 3. Hybrid Information State Center (Middle)
add_box(ax, (5.4, 1.8), 4.4, 5.0,
        "混合信息状态中心 Z_k",
        ["【20 频道独立状态空间解耦】",
         "• 离散生命周期状态机:",
         "  未知 (UNKNOWN) -> 存活 (ALIVE)",
         "  已清除 (CLEARED) / 空置 (ABSENT)",
         "• 连续几何状态与相容外包凸多边形 K+",
         "  角楔相交约束: K_{c,k+1}+ = K_{c,k}+ ∩ W",
         "  近场约束: 进入 5 m 核心圆盘",
         "  负观测硬排除: 剔除 1000 m 感知圆",
         "• 状态转移严格单向不可逆",
         "• 归纳保证目标真实位置真值包含性"],
        c_state_bg, c_state_border, title_size=12)

# 4. Certification Layer (Top Right)
add_box(ax, (10.5, 4.7), 4.0, 3.2,
        "完备性底座认证层 (管正确)",
        ["• 核心责任: 保证 100% 清除，一票否决",
         "• 七点蜂窝覆盖: 保证全域目标无遗漏",
         "• 最小外接圆判定: r* <= 19.5 m 保证清除",
         "• 有限网格兜底: 26 m 网格有限步收敛",
         "• 全局完成证书: 16 个清空或全频道结案",
         "• 严禁启发式模块提前终止或跳过认证"],
        c_cert_bg, c_cert_border, title_size=11.5)

# 5. Efficiency Layer (Bottom Right)
add_box(ax, (10.5, 0.6), 4.0, 3.2,
        "滚动调度效率层 (管提速)",
        ["• 核心职责: 在认证约束内极小化总耗时",
         "• Q2 极小极大下一测点推荐与快速收敛",
         "• 四类动态任务池: 搜索/定位/清除/网格",
         "• 综合代价值评估: 移动/调谐/几何压缩",
         "• 滚动时域更新: 适应动态认知与空间变化",
         "• 仅决定动作次序，无权更改状态或判定"],
        c_eff_bg, c_eff_border, title_size=11.5)

# Add Arrows showing the closed-loop flow
arrow_kw = dict(arrowstyle="-|>", mutation_scale=18, linewidth=2.0)

# Arrow 1: Env to History (Feedback y_k)
ax.annotate("", xy=(2.6, 4.65), xytext=(2.6, 3.85),
            arrowprops=dict(facecolor=c_auth_border, edgecolor=c_auth_border, **arrow_kw))
ax.text(2.7, 4.25, "物理反馈序列 y_k\n(确界误差/离散响应)", fontsize=9.5, fontweight='bold', color=c_auth_border, va='center')

# Arrow 2: History to State Center
ax.annotate("", xy=(5.35, 5.8), xytext=(4.75, 5.8),
            arrowprops=dict(facecolor=c_state_border, edgecolor=c_state_border, **arrow_kw))
ax.text(4.75, 6.15, "硬约束确定性重构\n(包含性归纳维护)", fontsize=9, fontweight='bold', color=c_state_border, ha='center')

# Arrow 3: State Center to Certification Layer
ax.annotate("", xy=(10.45, 6.3), xytext=(9.85, 6.3),
            arrowprops=dict(facecolor=c_cert_border, edgecolor=c_cert_border, **arrow_kw))
ax.text(10.15, 6.65, "提交认证请求\n(覆盖/清除/终止)", fontsize=9, fontweight='bold', color=c_cert_border, ha='center')

# Arrow 4: Certification to Efficiency (Constrained Action Space)
ax.annotate("", xy=(12.5, 3.85), xytext=(12.5, 4.65),
            arrowprops=dict(facecolor=c_cert_border, edgecolor=c_cert_border, **arrow_kw))
ax.text(12.65, 4.25, "合法候选动作空间\n(过滤不可行与危险动作)", fontsize=9, fontweight='bold', color=c_cert_border, va='center')

# Arrow 5: Efficiency Layer to Robot (Next Action a_k)
path_eff_to_env = FancyArrowPatch((10.45, 1.8), (4.75, 1.8),
                                  connectionstyle="arc3,rad=-0.15",
                                  arrowstyle="-|>", mutation_scale=20,
                                  linewidth=2.2, facecolor=c_action_border, edgecolor=c_action_border)
ax.add_patch(path_eff_to_env)
ax.text(7.6, 1.05, "执行最优决策动作 a_k (机动测向 / 激光清除 / 异常重发)", 
        fontsize=10.5, fontweight='bold', color=c_action_border, ha='center')

# Header text
ax.text(7.5, 8.05, "未知多干扰源在线协同搜索、定位与清除闭环控制系统架构",
        ha='center', va='center', fontsize=14.5, fontweight='bold', color='#1A365D')

plt.tight_layout()
plt.savefig('C:/Users/23066/Desktop/mathmode/images/fig_q3_system_architecture.png', dpi=300)
print("System architecture figure re-generated clean.")
