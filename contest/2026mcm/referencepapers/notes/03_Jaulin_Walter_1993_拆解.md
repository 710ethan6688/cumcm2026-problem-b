# 03. Set Inversion via Interval Analysis for Nonlinear Bounded-error Estimation

---

## A. 书目信息与核验

- **论文题名**：Set Inversion via Interval Analysis for Nonlinear Bounded-error Estimation
- **全部作者**：Luc Jaulin, Éric Walter
- **作者单位**：Laboratoire des Signaux et Systèmes, CNRS / École Supérieure d'Électricité (LSS-ESE), Plateau de Moulon, 91192 Gif-sur-Yvette Cedex, France
- **发表出处**：*Automatica* (An International Journal of IFAC, the International Federation of Automatic Control), Pergamon Press
- **卷期页码**：Vol. 29, No. 4, pp. 1053–1064
- **出版年份**：1993 年（收稿时间：1992 年 1 月 13 日；修订时间：1992 年 8 月 24 日；录用时间：1992 年 11 月 25 日）
- **DOI / 检索链接**：[10.1016/0005-1098(93)90106-4](https://doi.org/10.1016/0005-1098(93)90106-4)
- **ISSN / 识别号**：0005-1098/93; PII: 0005-1098(93)90106-4
- **PDF 总页数**：共 12 页
- **正文页码与 PDF 页码映射关系**：
  - 本文为 IFAC 会刊 *Automatica* 的正式印刷出版物，正文印刷页码为 pp. 1053–1064，与 PDF 对应页码具有全局恒定的线性映射关系：
    $$\text{正文印刷页码} = \text{PDF 页码} + 1052$$
  - 各页内容及主要结构核验对应如下：
    - **正文 p. 1053 $\leftrightarrow$ PDF p. 1**：论文标题、作者信息、摘要（Abstract）、关键词、Section 1（Introduction to Bounded-Error Estimation）、式 (1)–(3)；
    - **正文 p. 1054 $\leftrightarrow$ PDF p. 2**：Section 1 结尾（式 (4) 集合反演定义、线性与非线性有界误差估计现状综述）、Section 2（Test Cases）、Test Case 1 形式化式 (5)–(8)；
    - **正文 p. 1055 $\leftrightarrow$ PDF p. 3**：Test Case 1 结束式 (9)、Test Case 2 形式化式 (10)–(15)、Figure 1（带误差棒的时域观测数据图）、Section 3（Interval Analysis）、Section 3.1（Boxes）、Definition 1–4、式 (16)；
    - **正文 p. 1056 $\leftrightarrow$ PDF p. 4**：Section 3.2（Minimal Inclusion Functions）、Definition 5、Example 1–3、式 (17)–(21)、Section 3.3（Inclusion Functions）、Definition 6、Remark 2；
    - **正文 p. 1057 $\leftrightarrow$ PDF p. 5**：Figure 2（包含函数几何示意图）、Example 4 式 (22)–(23)、Section 3.4（Subpavings）、Definition 7–9、Remark 3、Section 4（Set Inversion and Set Enclosure）问题表述；
    - **正文 p. 1058 $\leftrightarrow$ PDF p. 6**：Figure 3（集合反演与子铺砌包络示意图）、Table 1（集合反演与有界误差估计物理概念对应表）、Section 4.1（Distances）、4.1.1（Hausdorff Distance）、式 (24)–(34)、Definition 10；
    - **正文 p. 1059 $\leftrightarrow$ PDF p. 7**：Section 4.1.2（Complementary Hausdorff Distance）、Definition 11、Proposition 1；Section 4.1.3（Generalized Hausdorff Distance）、Definition 12、Proposition 2；Section 4.2（Compact Enclosure Between Two Subpavings）、Definition 13、式 (35)、Proposition 3、特征量包络 $Z(\mathbb{X})$；
    - **正文 p. 1060 $\leftrightarrow$ PDF p. 8**：Section 5（Algorithm for Set Inversion）、Section 5.1（Set Inversion via Interval Analysis - SIVIA）、程序输入与初始化、Iteration $k$ 步骤 1–2、Figure 4（盒可行性判定：可行、不可行、未决）、Figure 5；
    - **正文 p. 1061 $\leftrightarrow$ PDF p. 9**：Figure 5 题注（$\mathbb{K}_{\mathrm{out}} = \mathbb{K}_{\mathrm{in}} \cup \mathbb{K}_{\mathrm{i}}$）、步骤 3–4、Section 5.2（Properties of SIVIA）、5.2.1（Convergence）、Lemma 1、Theorem 1 收敛定理、式 (36)–(40)、5.2.2（Computing Time）、5.2.3（Memory Used）；
    - **正文 p. 1062 $\leftrightarrow$ PDF p. 10**：堆栈深度上界式 (41)、Figure 6（Test Case 1 二维参数子铺砌反演图）、Section 6（Results Obtained on the Test Cases）、Test Case 1 实验结果式 (42)–(43)、Figure 7（可行指数函数族叠加图）、Test Case 2 实验设置与分析、Table 2 性能统计表；
    - **正文 p. 1063 $\leftrightarrow$ PDF p. 11**：Table 2 尾部、Table 3（外包矩形盒 $[\mathbb{S}]$ 与外子铺砌 $\mathbb{K}_{\mathrm{out}}$ 全面对比表）、Remark 4（误差容限摄动敏感性分析）、Section 7（Conclusions）、致谢、参考文献 [1]–[8]；
    - **正文 p. 1064 $\leftrightarrow$ PDF p. 12**：参考文献 [9]–[25]、Appendix（Notation，符号表与数学算子汇总定义）。

---

## B. 200 字以内核心摘要

针对非线性有界误差参数估计长期缺乏全局保证解的难题，论文首次将该问题严密形式化为集合反演问题 $\mathbb{S} = \mathbf{f}^{-1}(\mathbb{Y})$，开创性提出了基于区间分析的集合反演算法（SIVIA）。利用包含函数与区间算术，结合轴对齐盒分支二分与堆栈搜索，将未知可行集严格夹逼在外子铺砌 $\mathbb{K}_{\mathrm{out}}$ 与内子铺砌 $\mathbb{K}_{\mathrm{in}}$ 之间。在广义 Hausdorff 距离下证明了算法收敛性，并证明其堆栈内存仅随精度呈对数级增长。为有界示向误差下的确定性集合定位与内/外近似判据奠定了公认的理论基石。

---

## C. 对应 B 题的位置

- **对应题目步骤**：
  - **Q1**：交会定位法中“有界示向误差形成多边形定位区域”与“集合逆映射求可行域”的最底层数学元理论；
  - **Q1/Q2**：支撑“为什么在有界误差下不能任意套用高斯分布先验、点估计为何具有欺骗性”的方法论论证；
  - **Q1 覆盖判据**：提供集合内近似 $\mathbb{K}_{\mathrm{in}}$ 与外近似 $\mathbb{K}_{\mathrm{out}}$ 对特征量（直径、覆盖圆半径）实施双向保守夹逼的标准范式。
- **证据等级**：**理论基础**。
- **一句话说明为何属于该等级**：论文建立了非线性有界误差集合反演求可行解集 $\mathbb{S}$ 的严密理论框架、收敛性公理与内/外近似概念，但因 B 题二维直视测向线无折射时几何退化为线性半平面交，主模型采用多边形解析几何求交，因此本篇作为奠基性理论依据与非线性扩展基准，不充当本题唯一数值求解器。

---

## D. 模型拆解

### 1. 状态与物理量
- **未知待估计状态向量**：$\mathbf{p} \in \mathbb{P} \subset \mathbb{R}^{n_p}$（Section 1, 正文 p. 1053 / PDF p. 1），在系统模型中为待识别的物理参数。
- **实验观测数据向量**：$\mathbf{y} \in \mathbb{R}^{n_y}$（Section 1, 正文 p. 1053 / PDF p. 1），采集自系统在固定已知实验条件下的 $n_y$ 个测量值。
- **参数化模型输出向量**：$\mathbf{y}_m(\mathbf{p}) \in \mathbb{R}^{n_y}$（Section 1, 正文 p. 1053 / PDF p. 1），由参数 $\mathbf{p}$ 经连续且局部可辨识的系统模型映射生成的输出。
- **预测误差向量**：$\mathbf{e}_m(\mathbf{p}) = \mathbf{y} - \mathbf{y}_m(\mathbf{p}) \in \mathbb{R}^{n_y}$（Section 1 式 (1), 正文 p. 1053 / PDF p. 1）。
- **先验可行参数集**：$\mathbb{P} \subset \mathbb{R}^{n_p}$，通常为先验轴对齐大区间盒 $[\mathbf{p}]$（Section 1 式 (2), 正文 p. 1053 / PDF p. 1）。
- **先验容许误差集**：$\mathbb{E} \subset \mathbb{R}^{n_y}$，通常由一组先验物理误差上下界约束构成的区间超矩形盒（Section 1 式 (2), 正文 p. 1053 / PDF p. 1）。
- **后验可行参数集**：$\mathbb{S} \subset \mathbb{P}$，所有使模型误差落入先验容许范围 $\mathbb{E}$ 内的参数真值集合（Section 1 式 (2), 正文 p. 1053 / PDF p. 1）。

### 2. 核心假设与专项核查
- **有界误差（Bounded-error）确定性假设（Section 1, 正文 p. 1053 / PDF p. 1）**：
  - 【作者原文结论】：误差 $\mathbf{e}_m(\mathbf{p})$ 满足绝对确定性边界约束 $\mathbf{e}_m(\mathbf{p}) \in \mathbb{E}$，不需要也不应人为假设误差的特定概率分布函数（如高斯分布）。作者特别指出：虽然有界集估计属于纯确定性语境，但亦可赋予贝叶斯统计解释——若 $\mathbb{P}$ 和 $\mathbb{E}$ 分别为先验概率密度函数与似然函数的支撑集（Support），则后验可行集 $\mathbb{S}$ 严格对应后验概率密度的非零支撑集，亦即似然度非零的点集。
  - 【原文证据】（Section 1, 正文 p. 1053 / PDF p. 1）：“*Although set-membership estimation can be set in a purely deterministic context, it can also receive a stochastic interpretation... S is the set of all values of p such that the likelihood of the data is nonzero.*”
  - 【迁移推导】：B 题附录 2 明确规定“环境干扰及测向误差全局在 $[-1^\circ, 1^\circ]$ 范围内。同一地点重复检测误差不变”。这正是典型的非随机高斯、具有确定性硬边界的有界误差环境。直接套用高斯卡尔曼滤波或最小二乘不仅违背题目“硬边界”设定，且会丢失最坏情况保证。采用集合反演理论构建可行域 $\mathbb{S}$ 是最严谨且符合题意的数学基石。
- **连续性与可计算包含函数假设（Section 3.2–3.3, 正文 pp. 1056–1057 / PDF pp. 4–5）**：
  - 【作者原文结论】：系统函数 $\mathbf{f}$ 必须连续，此时必然存在满足单调收敛性质的包含函数 $\mathbb{F}$（Definition 6: $\forall [\mathbf{x}], \mathbf{f}([\mathbf{x}]) \subset \mathbb{F}([\mathbf{x}])$ 且 $w([\mathbf{x}]) \to 0 \Rightarrow w(\mathbb{F}([\mathbf{x}])) \to 0$）。
  - 【迁移推导】：B 题中，在直视视距（LOS）范围内，测向几何关系 $\theta = \mathrm{atan2}(y - y_i, x - x_i)$ 除在测点自身原点（距离为 0）处奇异外，在全探测区域内处处连续可微，因此自然满足区间包含函数构造条件。
- **有界闭集与全紧集（Full Compact）假设（Section 4.2, 正文 p. 1059 / PDF p. 7）**：
  - 【作者原文结论】：为保证内子铺砌 $\mathbb{K}_{\mathrm{in}}$ 能够收敛逼近集合 $\mathbb{X}$，要求集合 $\mathbb{X}$ 是“全紧集”（Full Compact, Definition 13），即满足 $\mathrm{clo}(\mathrm{int}(\mathbb{X})) = \mathbb{X}$（不存在孤立单点或无厚度退化线段）。
  - 【迁移推导】：在 B 题 Q1 中，只要至少两测点视线不共线且误差角严格为正（$\pm 1^\circ$ 张角为 $2^\circ > 0$），交会形成的多边形定位区域必然拥有非空内部，严格属于全紧集，保证了集合内/外逼近理论在 B 题中完全成立。

### 3. 测量与误差模型
论文给出的通用非线性测量方程与误差容许模型为（Section 1 式 (1)–(3), 正文 p. 1053 / PDF p. 1）：
$$
\mathbf{y} = \mathbf{y}_m(\mathbf{p}) + \mathbf{e}, \quad \mathbf{e} \in \mathbb{E}
$$
在测量输出空间定义容许观测集 $\mathbb{Y} = \mathbf{y} - \mathbb{E}$，则测量模型可完全等价转化为显式的集合逆映射方程（Section 1 式 (4), 正文 p. 1054 / PDF p. 2）：
$$
\mathbb{S} = \mathbf{y}_m^{-1}(\mathbb{Y}) = \left\{ \mathbf{p} \in \mathbb{P} \;\middle|\; \mathbf{y}_m(\mathbf{p}) \in \mathbb{Y} \right\}
$$

### 4. 目标函数与集合约束
- **可行集定义**：寻找所有使得模型预测与实际数据误差不超出先验边界的参数集合（式 (2) 与式 (4)）。
- **特征量单调包络模型**（Section 4.2, 正文 p. 1059 / PDF p. 7）：
  若 $Z(\mathbb{X})$ 为在偏序紧集空间上的保序单调递增泛函（例如集合体积 $\mathrm{vol}(\mathbb{X})$、最小外接矩形盒 $[\mathbb{X}]$、或凸函数的极大值），且内/外子铺砌满足 $\mathbb{K}_{\mathrm{in}} \subset \mathbb{X} \subset \mathbb{K}_{\mathrm{out}}$，则特征量严格满足确定性双向夹逼：
  $$
  Z(\mathbb{K}_{\mathrm{in}}) \le Z(\mathbb{X}) \le Z(\mathbb{K}_{\mathrm{out}})
  $$
  当子铺砌最大盒宽 $\varepsilon_r \to 0$ 时，两者极限收敛于真值 $Z(\mathbb{X})$。

### 5. 论文符号到 B 题物理量映射表

| 论文原符号 | 论文物理含义 | B 题对应对象 | B 题具体数值 / 约束定义 | 迁移转换与核查备注 |
|---|---|---|---|---|
| $\mathbf{p} \in \mathbb{R}^{n_p}$ | 待估计系统参数向量 ($n_p$ 维) | 未知无线电干扰源平面二维坐标 | $\mathbf{s} = [x, y]^T \in \mathbb{R}^2$ ($n_p = 2$) | 物理维度由通用 $n_p$ 退化为平面 2 维坐标。 |
| $\mathbb{P} \subset \mathbb{R}^{n_p}$ | 参数先验可行域超矩形盒 | 目标分布圆形区域的外接包络矩形 | $[-1800, 1800] \times [-1800, 1800]\text{ m}^2$ | 论文为先验盒，B 题目标圆域半径 $1800\text{ m}$，初始搜索盒宽 $w=3600\text{ m}$。 |
| $\mathbf{y} \in \mathbb{R}^{n_y}$ | 采集的系统实验观测数据向量 | 测向机在各检测点测得的示向度集合 | $\mathbf{y} = [\hat{\theta}_1, \dots, \hat{\theta}_N]^T$ | 示向度 $\hat{\theta}_i \in [0^\circ, 360^\circ)$，共 $N$ 个检测点。 |
| $\mathbf{y}_m(\mathbf{p})$ | 参数化非线性模型输出函数 | 几何正向测向映射函数 | $y_{m,i}(\mathbf{s}) = \mathrm{atan2}(y - y_i, x - x_i)$ | 测点 $\mathbf{z}_i = [x_i, y_i]^T$ 到目标点的理论方位角。 |
| $\mathbf{e}_m(\mathbf{p})$ | 模型输出与观测数据残差向量 | 示向度理论方位角与实测示向度偏差 | $e_i(\mathbf{s}) = \hat{\theta}_i - y_{m,i}(\mathbf{s}) \pmod{360^\circ}$ | 角度差值需在环形拓扑模 $360^\circ$ 下计算。 |
| $\mathbb{E} \subset \mathbb{R}^{n_y}$ | 先验容许误差集 | 示向度测量综合有界误差区间积 | $\mathbb{E} = [-1^\circ, 1^\circ]^N$ | 附录 2 规定测向误差全局在 $[-1^\circ, 1^\circ]$ 内。 |
| $\mathbb{Y} = \mathbf{y} - \mathbb{E}$ | 观测数据容许输出区间盒 | 各测点包含真实方位的角扇形区间积 | $\prod_{i=1}^N [\hat{\theta}_i - 1^\circ, \hat{\theta}_i + 1^\circ]$ | 实测示向度向两侧各展开 $1^\circ$ 形成的容许角度集。 |
| $\mathbb{S} = \mathbf{y}_m^{-1}(\mathbb{Y})$ | 后验可行参数集合 (Feasible Set) | 交会定位法形成的多边形定位区域 | $\mathcal{S} = \bigcap_{i=1}^N \mathcal{S}_i$ (凸多边形) | 论文核心研究实体，B 题 Q1 求解的核心定位区域。 |
| $[\mathbf{x}]$ | 参数空间中的轴对齐区间盒 | 平面坐标的轴对齐矩形网格小单元 | $[x^-, x^+] \times [y^-, y^+]$ | SIVIA 算法在二维平面网格二分搜索的微元。 |
| $\mathbb{F}([\mathbf{x}])$ | 模型函数 $\mathbf{y}_m$ 的区间包含函数 | 矩形网格单元在测向角上的区间像集 | 方位角极值映射区间 $[\theta_{\min}, \theta_{\max}]$ | 用于三类盒可行性判定的区间评价器。 |
| $\mathbb{K}_{\mathrm{in}}$ | 确定可行的内部子铺砌并集 | 完全位于交会多边形内部的网格并集 | 满足 $\mathbb{K}_{\mathrm{in}} \subset \mathcal{S}$ 的栅格集合 | 提供定位区域的绝对内近似与保守清除范围。 |
| $\mathbb{K}_{\mathrm{i}}$ | 不确定边界子铺砌并集 | 横跨交会多边形边界的网格并集 | 包含多边形边界 $\partial \mathcal{S}$ 的细分网格带 | 决定了数值解的逼近不确定性边界宽度。 |
| $\mathbb{K}_{\mathrm{out}}$ | 包含解集的外部子铺砌并集 | 覆盖整个定位多边形的网格并集 | $\mathbb{K}_{\mathrm{out}} = \mathbb{K}_{\mathrm{in}} \cup \mathbb{K}_{\mathrm{i}} \supset \mathcal{S}$ | 提供定位区域的绝对外包含（Outer Bound）。 |
| $\varepsilon_r$ | SIVIA 算法设定的铺砌精度门限 | 二维定位网格空间分辨率阈值 | 终止盒宽（例如取 $\varepsilon_r = 0.1\text{ m}$） | 控制空间二分细化的停止粒度。 |
| $Z(\mathbb{S})$ | 可行集的单调递增特征泛函 | 定位多边形几何特征量 | 区域直径 $\mathrm{diam}(\mathcal{S})$ 或外接圆半径 | 论文证明了 $Z(\mathbb{K}_{\mathrm{in}}) \le Z(\mathbb{S}) \le Z(\mathbb{K}_{\mathrm{out}})$。 |
| $[\mathbb{S}]$ | 紧包络可行集的外包超矩形盒 | 定位多边形的外接轴对齐边界框 (AABB) | $[x_{\min}, x_{\max}] \times [y_{\min}, y_{\max}]$ | 论文指出 $[\mathbb{S}]$ 极度保守，且其中心可能不可行。 |

---

## E. 关键公式

### 公式 1：有界误差下的后验可行集形式化定义
- **原文公式编号**：式 (2)
- **章节与页码**：Section 1, 正文第 1053 页 / PDF 第 1 页
- **LaTeX 表达式**：
  $$
  \mathbb{S} = \left\{ \mathbf{p} \in \mathbb{P} \;\middle|\; \mathbf{e}_m(\mathbf{p}) \in \mathbb{E} \right\}
  $$
- **符号解释**：$\mathbf{p}$ 为未知参数；$\mathbb{P}$ 为参数先验集合；$\mathbf{e}_m(\mathbf{p}) = \mathbf{y} - \mathbf{y}_m(\mathbf{p})$ 为测量残差；$\mathbb{E}$ 为先验容许误差界限。
- **中文含义**：后验可行集包含且仅包含所有能使理论模型预测值与实际观测值之差保持在先验误差边界之内的参数点。
- **可否迁移到 B 题**：**完全可迁移且为 Q1 核心理论基石**。将 $\mathbf{p}$ 替换为干扰源坐标 $\mathbf{s}=(x,y)$，$\mathbf{e}_m(\mathbf{p}) \in \mathbb{E}$ 替换为各站测向误差在 $[-1^\circ, 1^\circ]$ 内，即严格定义了交会定位多边形集合。

### 公式 2：集合反演算子等价表达
- **原文公式编号**：式 (4)
- **章节与页码**：Section 1, 正文第 1054 页 / PDF 第 2 页
- **LaTeX 表达式**：
  $$
  \mathbb{S} = \mathbf{y}_m^{-1}(\mathbf{y} - \mathbb{E}) = \mathbf{y}_m^{-1}(\mathbb{Y}) = \mathbf{e}_m^{-1}(\mathbb{E})
  $$
- **符号解释**：$\mathbf{y}_m^{-1}$ 为集合论意义下的原像映射（Reciprocal / Pre-image Mapping）；$\mathbb{Y} = \mathbf{y} - \mathbb{E}$ 为观测数据在容许误差下的像空间集合。
- **中文含义**：将参数估计求解转化为求输出空间容许集合 $\mathbb{Y}$ 在非线性模型映射 $\mathbf{y}_m$ 下的原像集合反演问题。
- **可否迁移到 B 题**：**完全可迁移**。测向交会定位在数学本质上就是测向映射函数 $\theta_i(\mathbf{s})$ 关于角区间 $[\hat{\theta}_i - 1^\circ, \hat{\theta}_i + 1^\circ]$ 的逆像反演。

### 公式 3：区间盒与盒宽（Width）定义
- **原文公式编号**：式 (16) 与 Definition 3
- **章节与页码**：Section 3.1, 正文第 1055 页 / PDF 第 3 页
- **LaTeX 表达式**：
  $$
  [\mathbf{x}] = [x_1^-, x_1^+] \times [x_2^-, x_2^+] \times \dots \times [x_n^-, x_n^+] = [\mathbf{x}^-, \mathbf{x}^+] \in \mathbb{IR}^n
  $$
  $$
  w([\mathbf{x}]) = \max_{i=1,\dots,n} \left\{ x_i^+ - x_i^- \right\}
  $$
- **符号解释**：$[\mathbf{x}]$ 为 $n$ 维区间的笛卡尔积（超矩形盒）；$\mathbb{IR}^n$ 为 $n$ 维区间盒的集合；$w([\mathbf{x}])$ 为该盒在所有维度上的最大边长。
- **中文含义**：定义区间算术的基本处理单元为轴对齐盒，其尺寸由最长边的跨度度量。
- **可否迁移到 B 题**：**完全可迁移**。在二维平面中，$[\mathbf{x}]$ 即为 $[x^-, x^+] \times [y^-, y^+]$ 矩形，盒宽即为 $\max(x^+ - x^-, y^+ - y^-)$，是实现二维网格递归细分的基础几何结构。

### 公式 4：三类盒判据（SIVIA 核心分支测试条件）
- **原文公式编号**：Section 5.1, 正文第 1060 页 / PDF 第 8 页（非独立带编号公式，算法核心条件）
- **章节与页码**：Section 5.1, 正文第 1060 页 / PDF 第 8 页
- **LaTeX 表达式**：
  $$
  \begin{aligned}
  \mathbb{F}([\mathbf{x}]) \subset \mathbb{Y} &\implies [\mathbf{x}] \subset \mathbb{X} \quad (\text{Feasible: 确定可行，加入 } \mathbb{K}_{\mathrm{in}}) \\
  \mathbb{F}([\mathbf{x}]) \cap \mathbb{Y} = \emptyset &\implies [\mathbf{x}] \cap \mathbb{X} = \emptyset \quad (\text{Unfeasible: 确定不可行，直接剔除}) \\
  \text{otherwise} &\implies [\mathbf{x}] \text{ 为 Indeterminate (若 } w([\mathbf{x}]) \le \varepsilon_r \text{ 进 } \mathbb{K}_{\mathrm{i}} \text{，否则二分入栈)}
  \end{aligned}
  $$
- **符号解释**：$\mathbb{F}([\mathbf{x}])$ 为函数 $\mathbf{f}$ 在盒 $[\mathbf{x}]$ 上的区间包含函数扩展；$\mathbb{Y}$ 为目标测量集合；$\mathbb{X}$ 为真实可行原像集；$\varepsilon_r$ 为精度阈值。
- **中文含义**：利用区间像的包含关系实现对整个子空间区域的批量状态裁决：若区间像全在目标内，则整个空间盒百分之百属于可行集；若区间像与目标完全无交，则整个空间盒百分之百排除；仅在边界模糊处才二分细化。
- **可否迁移到 B 题**：**可迁移**。在非线性或带有近场弯曲的测向场合，此三分类判据可无缝对搜索栅格进行全局确定性剪枝；但在 Q1 直线测向中，该判据可被多边形几何求交直接解析取代。

### 公式 5：广义 Hausdorff 距离与外/内子铺砌收敛定理
- **原文公式编号**：Definition 12, 式 (36) 及 Theorem 1
- **章节与页码**：Section 4.1.3 & 5.2.1, 正文 pp. 1059, 1061 / PDF pp. 7, 9
- **LaTeX 表达式**：
  $$
  m_\infty(\mathbb{A}, \mathbb{B}) = \max\left\{ h_\infty(\mathbb{A}, \mathbb{B}), \; h_\infty(\bar{\mathbb{A}}, \bar{\mathbb{B}}) \right\}
  $$
  $$
  \mathbb{K}_{\mathrm{in}} \subset \mathbb{X} \subset \mathbb{K}_{\mathrm{out}} \triangleq \mathbb{K}_{\mathrm{in}} \cup \mathbb{K}_{\mathrm{i}}
  $$
  $$
  \lim_{\varepsilon_r \to 0} h_\infty(\mathbb{K}_{\mathrm{i}}, \partial \mathbb{X}) = 0, \quad \lim_{\varepsilon_r \to 0} h_\infty(\mathbb{K}_{\mathrm{out}}, \mathbb{X}) = 0, \quad \lim_{\varepsilon_r \to 0} h_\infty(\mathbb{X}, \mathbb{K}_{\mathrm{in}}) = 0 \; (\text{若 } \mathbb{X} \text{ 为全紧集})
  $$
- **符号解释**：$h_\infty$ 为标准 Hausdorff 距离；$\bar{\mathbb{A}}$ 为集合 $\mathbb{A}$ 的补集；$m_\infty$ 为广义 Hausdorff 距离；$\partial \mathbb{X}$ 为可行集拓扑边界。
- **中文含义**：外子铺砌与内子铺砌严格构成对真值可行集的双向夹逼包络；当网格精度 $\varepsilon_r \to 0$ 时，不确定边界集 $\mathbb{K}_{\mathrm{i}}$ 严格收缩至真实多边形边界 $\partial \mathbb{X}$，内外逼近集均在 Hausdorff 意义下严格收敛于真实集合。
- **可否迁移到 B 题**：**理论证明与收敛性分析可完全迁移**。为 B 题论文证明“随着测点增加或栅格分辨率提高，定位不确定性区域严格单调收敛于真值多边形”提供了极其高阶且严谨的拓扑学证据。

### 公式 6：SIVIA 算法堆栈内存消耗的绝对上界
- **原文公式编号**：式 (41)
- **章节与页码**：Section 5.2.3, 正文第 1062 页 / PDF 第 10 页
- **LaTeX 表达式**：
  $$
  \#\mathrm{stack} < n \cdot \operatorname{int}\left( \log_2\left(w([\mathbf{x}](0))\right) - \log_2(\varepsilon_r) + 1 \right)
  $$
- **符号解释**：$\#\mathrm{stack}$ 为算法运行期间堆栈中暂存盒的最大数量；$n$ 为参数空间维度；$w([\mathbf{x}](0))$ 为初始先验搜索盒的跨度；$\varepsilon_r$ 为设定的目标停止精度；$\operatorname{int}(\cdot)$ 为取整函数。
- **中文含义**：算法执行深度优先搜索时，内存开销并不随细分盒的总数呈指数爆炸，而是严格与空间维度 $n$ 以及分辨率精度的对数成正比（极度轻量）。
- **可否迁移到 B 题**：**可直接代入计算**。在 B 题中，参数维度 $n=2$，初始搜索区域直径 $w([\mathbf{x}](0)) = 3600\text{ m}$。若取空间网格极限分辨率 $\varepsilon_r = 0.1\text{ m}$，则：
  $$\#\mathrm{stack} < 2 \cdot \operatorname{int}(\log_2(3600) - \log_2(0.1) + 1) \approx 2 \cdot \operatorname{int}(11.81 - (-3.32) + 1) = 2 \times 16 = 32$$
  整个搜索过程中堆栈常驻矩形盒不超过 32 个，说明在二维定位场景下，哪怕进行极限精度的区间网格搜索，内存开销也极小。

---

## F. 算法与证明

### 1. SIVIA 算法流程（伪代码与步骤分解）

- **算法输入**：
  1. 连续模型函数的区间包含函数 $\mathbb{F}$；
  2. 容许观测数据集合 $\mathbb{Y}$（由实测数据 $\mathbf{y}$ 与误差带 $\mathbb{E}$ 构成）；
  3. 先验初始搜索盒 $[\mathbf{x}](0)$（覆盖整个任务区域）；
  4. 终止停止精度 $\varepsilon_r > 0$。
- **算法输出**：
  - 内子铺砌 $\mathbb{K}_{\mathrm{in}}$（全由确定可行盒构成，保证 $\mathbb{K}_{\mathrm{in}} \subset \mathbb{X}$）；
  - 不确定边界子铺砌 $\mathbb{K}_{\mathrm{i}}$（宽度均 $\le \varepsilon_r$，跨越边界 $\partial \mathbb{X}$）；
  - 外子铺砌 $\mathbb{K}_{\mathrm{out}} = \mathbb{K}_{\mathrm{in}} \cup \mathbb{K}_{\mathrm{i}}$（保证 $\mathbb{X} \subset \mathbb{K}_{\mathrm{out}}$）。
- **算法状态与初始化**：
  - 迭代计数器 $k = 0$；
  - 盒堆栈 $\mathrm{stack} = \emptyset$；
  - 输出集清空：$\mathbb{K}_{\mathrm{in}} = \emptyset, \mathbb{K}_{\mathrm{i}} = \emptyset$；
  - 将初始盒压入堆栈：将 $[\mathbf{x}](0)$ 置为当前待处理盒。
- **迭代循环执行逻辑（Iteration $k$）**：
  - **Step 1（可行性检验）**：计算区间像 $\mathbb{F}([\mathbf{x}](k))$。若 $\mathbb{F}([\mathbf{x}](k)) \subset \mathbb{Y}$，则该盒完全可行，更新 $\mathbb{K}_{\mathrm{in}} = \mathbb{K}_{\mathrm{in}} \cup [\mathbf{x}](k)$，跳转至 **Step 4**。
  - **Step 2（不可行性检验）**：若 $\mathbb{F}([\mathbf{x}](k)) \cap \mathbb{Y} = \emptyset$，则该盒完全不可行，直接抛弃（无操作），跳转至 **Step 4**。
  - **Step 3（未决盒处理与二分分支）**：
    - 若当前盒宽 $w([\mathbf{x}](k)) \le \varepsilon_r$，说明已达精度极限，将其作为边界盒归入未决集：$\mathbb{K}_{\mathrm{i}} = \mathbb{K}_{\mathrm{i}} \cup [\mathbf{x}](k)$；
    - 否则（$w([\mathbf{x}](k)) > \varepsilon_r$），选择该盒最长边所在主平面（Principal Plane）执行等分二分（Bisection），将切分生成的两个子盒压入堆栈 $\mathrm{stack}$。
  - **Step 4（堆栈调度）**：检查堆栈。若堆栈非空，则弹出栈顶盒赋给 $[\mathbf{x}](k+1)$，令 $k = k+1$，返回 **Step 1**；若堆栈为空，算法终止退出。

### 2. 复杂度分析与理论极限
- **时间复杂度（计算时间）**：
  - 最坏情况下，算法总迭代次数严格受限于 $\left( \frac{w([\mathbf{x}](0))}{\varepsilon_r} + 1 \right)^n$。计算时间随维度 $n$ 呈指数级增长（Curse of Dimensionality）。作者明确指出，这是 SIVIA 在高维参数估计时的主要局限（Section 5.2.2, 正文 p. 1061 / PDF p. 9）。
  - **在 B 题中的优势**：B 题干扰源定位仅为二维空间（$n=2$），维度极低，指数爆炸效应被抑制，二分网格总数完全在微秒至毫秒级可控范围内。
- **空间复杂度（内存消耗）**：
  - 由式 (41) 证明，栈深界限为 $\mathcal{O}\left(n \log_2\frac{w}{\varepsilon_r}\right)$。若仅需在线提取可行域特征量（如外接框、中心、面积），无需全局存储所有微元盒，内存占用少（通常仅需几十个盒的存储空间）。

### 3. 关键定理与证明要点
- **Lemma 1（未决盒逼近边界引理，Section 5.2.1, 正文 p. 1061 / PDF p. 9）**：
  - 【条件】：包含函数满足 $w([\mathbf{x}]) \to 0 \implies w(\mathbb{F}([\mathbf{x}])) \to 0$。
  - 【结论】：$\lim_{\varepsilon_r \to 0} h_\infty^0(\mathbf{f}(\mathbb{K}_{\mathrm{i}}), \partial \mathbb{Y}) = 0$。
  - 【证明要点】：所有进入 $\mathbb{K}_{\mathrm{i}}$ 的盒其宽度均 $\le \varepsilon_r$。由于其既非完全在内也非完全在外，其区间像必然贯穿观测集合的几何边界 $\partial \mathbb{Y}$，故当 $\varepsilon_r \to 0$ 时像集距离边界的邻近度趋于 0。
- **Theorem 1（子铺砌全局收敛定理，Section 5.2.1, 正文 p. 1061 / PDF p. 9）**：
  - 【条件】：逆映射 $\mathbf{f}^{-1}$ 在 $\mathbb{Y}$ 周围关于 $h_\infty$ 与补集距离 $\bar{h}_\infty$ 连续；且集合 $\mathbb{X}$ 为全紧集（Full Compact）。
  - 【结论】：当 $\varepsilon_r \to 0$ 时：
    1. 不确定子铺砌收敛至集合真实边界：$\mathbb{K}_{\mathrm{i}} \to \partial \mathbb{X}$；
    2. 外子铺砌从外侧单调逼近真值集合：$\mathbb{K}_{\mathrm{out}} \to \mathbb{X}$；
    3. 内子铺砌从内侧单调逼近真值集合：$\mathbb{K}_{\mathrm{in}} \to \mathbb{X}$。
  - 【证明要点】：由 Lemma 1 与逆映射的连续性，利用三角不等式传递，建立起原像空间中距离边界 $\partial \mathbb{X}$ 的收缩性；进而利用全紧集拓扑性质排除孤立点与裂缝，证得内铺砌的内部致密逼近。

---

## G. 实验与可比指标

### 1. 论文实验设计与基线设置
- **Test Case 1（标量非线性两参数拟合，Section 2 & 6, 正文 pp. 1054, 1062 / PDF pp. 2, 10）**：
  - 模型：$y_m(\mathbf{p}, t) = p_1 \exp(p_2 t)$，在连续区间 $t \in [0, 1]$ 上拟合数据 $y(t) = t^2 + 2t + 1$；
  - 容许误差：$|e_m(\mathbf{p}, t)| \le 1, \forall t \in [0, 1]$；
  - 搜索先验盒：$\mathbb{P} = [0, 5] \times [0, 5]$，要求精度 $\varepsilon_r = 0.01$；
  - 基准硬件：Compaq 386/33 PC。
- **Test Case 2（4 维双指数衰减模型，Section 2 & 6, 正文 pp. 1055, 1062 / PDF pp. 3, 10）**：
  - 模型：$y_m(\mathbf{p}, t) = p_1 \exp(-p_2 t) + p_3 \exp(-p_4 t)$，共 10 个采样时刻；
  - 容许误差：$\mathbf{e}_{\max} = 0.05|\mathbf{y}| + 0.1 \times \mathbf{1}$；
  - 搜索先验盒：$\mathbb{P} = [2, 60] \times [0, 1] \times [-30, -1] \times [0, 0.5]$（先验体积 $\mathrm{vol}(\mathbb{P}) = 841$）；
  - 对照基线：Milanese & Vicino (1991b) 的符号规划方法（Signomial Programming on VAX 8800）。

### 2. 关键数值结果与重要发现

1. **切比雪夫中心（点估计）的致命缺陷验证（Test Case 1，Section 6, 正文 p. 1062 / PDF p. 10）**：
   - SIVIA 在 31 秒内完成解算，内存常驻盒最多仅 12 个；
   - 给出严格的可行域外接包络盒与面积包络：
     $$[0.342, 1.992] \times [0.420, 2.646] \subset [\mathbb{S}] \subset [0.303, 2.002] \times [0.400, 2.813]$$
     $$0.76 \le \mathrm{vol}(\mathbb{S}) \le 0.84$$
   - **作者关键发现**：在外接盒 $[\mathbb{S}]$ 的几何中心（即传统有界估计中常用的切比雪夫中心点估计）处，对应生成的模型响应曲线**完全不满足**误差边界约束，该点估计本身在物理上是**不可行**的（如图 6 所示，中心点落在可行集 $\mathbb{S}$ 的凹陷空洞外部）！
2. **SIVIA 与符号规划外包盒对比（Test Case 2，Section 6, 正文 pp. 1062–1063 / PDF pp. 10–11）**：
   - 符号规划耗时 10 分钟求得外包盒 $[\mathbb{S}]$，其体积为 $1.16$；
   - SIVIA 仅运行 44 秒，得到的外子铺砌体积 $\mathrm{vol}(\mathbb{K}_{\mathrm{out}}) = 0.5$（比符号规划紧致一倍以上）；运行 2 分钟时，体积进一步压缩至 $0.08$（比符号规划体积小 10 倍以上，先验体积压缩比达 $10^4$）；
   - **Table 3 对比结论**：外接盒 $[\mathbb{S}]$ 虽然给出各个参数独立的边界，但极度悲观且包含大量与数据严重冲突的虚假模型；而 SIVIA 的子铺砌 $\mathbb{K}_{\mathrm{out}}$ 能够高度还原可行集的真实几何拓扑（包括非凸、倾斜细长条带），能反映出参数之间的强关联特征。

---

## H. 可直接用于建模论文的证据卡

### 证据卡 1：有界误差估计必须采用确定性集合表征（无需先验概率分布假设）
- **中文核心转述**：在传感器或测量环境仅给出明确物理误差边界（如 $\pm 1^\circ$）时，强行赋予其高斯分布或其他统计假设缺乏客观物理依据，会导致最坏情况下的置信失效；而集合反演给出的后验可行集 $\mathbb{S} = \mathbf{y}_m^{-1}(\mathbb{Y})$ 是贝叶斯意义下似然度非零的全部真实状态点集，具有百分之百的确凿保证。
- **精确定位**：Section 1, 正文 p. 1053 / PDF p. 1, 式 (2)–(4) 及对应正文段落。
- **推荐放入 B 题论文章节**：第 3 节“问题假设与有界误差测量模型建立”、第 4 节“Q1 几何交会模型理论推导”。
- **必须附带的适用条件**：误差存在严格物理上下界且先验已知；不适用于含有未建模野值或无限尾部噪声的场景。

### 证据卡 2：传统点估计（切比雪夫中心）的不可行风险与保留完整集合的必要性
- **中文核心转述**：在非线性有界估计中，简单采用外包框的几何中心或切比雪夫中心作为目标位置的点估计，可能得到一个物理上根本不可行的假点（点估计落在非凸可行域之外）；因此，必须保留并计算完整的定位几何区域（多边形），并基于几何极点计算直径与覆盖圆。
- **精确定位**：Section 6, 正文 p. 1062 / PDF p. 10, 段落 "The center of [S], i.e. the Tchebyshev center of S..." 及 Figure 6。
- **推荐放入 B 题论文章节**：第 4 节“Q1 干扰源定位结果与误差分析”、模型对比与鲁棒性讨论。
- **必须附带的适用条件**：可行集合呈现非凸、弯曲狭长或多测点交会夹角较小的场景。

### 证据卡 3：内近似与外近似对几何特征量（直径/覆盖圆）的双向保序夹逼
- **中文核心转述**：对于集合的保序单调递增泛函 $Z(\cdot)$（如区域体积、直径、外接圆半径），基于包含关系的内子铺砌与外子铺砌天然构成该几何指标的绝对下界与绝对上界：$Z(\mathbb{K}_{\mathrm{in}}) \le Z(\mathbb{S}) \le Z(\mathbb{K}_{\mathrm{out}})$。
- **精确定位**：Section 4.2, 正文 p. 1059 / PDF p. 7, 段落 "Enclosure of a characteristic Z(X)" 及 式 (35)–(36)。
- **推荐放入 B 题论文章节**：第 4 节“Q1 覆盖圆判定准则与安全性验证”。
- **必须附带的适用条件**：所评价的几何特征函数关于集合偏序具有单调递增性（即 $\mathbb{A} \subset \mathbb{B} \implies Z(\mathbb{A}) \le Z(\mathbb{B})$）。

### 证据卡 4：低维空间网格二分搜索的微量内存占用界限
- **中文核心转述**：基于堆栈的深度优先分支细化算法在二维平面搜索中，堆栈常驻内存与空间网格跨度对数成正比，仅需几十个数据结构即可完成厘米级精度的全局空间反演，不存在内存溢出风险。
- **精确定位**：Section 5.2.3, 正文 p. 1062 / PDF p. 10, 式 (41)。
- **推荐放入 B 题论文章节**：第 4 节或第 5 节“空间离散化算法复杂度与实时性分析”。
- **必须附带的适用条件**：采用深度优先遍历策略；参数空间维度较低（如二维定位平面 $n=2$）。

---

## I. 不能照搬的部分

### 1. 连续区间盒逼近与多边形解析几何的差异
- **差异所在**：
  - 论文面向通用的任意黑箱非线性函数（如非线性微分方程或高次多项式），无法直接求解连续边界曲线的解析交点，因此只能退而求其次，使用轴对齐的离散区间盒网格逐步逼近集合边界；
  - 在 B 题 Q1 中，尽管测向函数 $\theta_i = \mathrm{atan2}(y - y_i, x - x_i)$ 是关于坐标 $(x,y)$ 的非线性函数，但**其等值线（测向线）在二维欧几里得平面中是严格的直线射线**！$\pm 1^\circ$ 的有界误差诱导出的边界是严格的线性半平面。多次观测的交集是一个严格的凸多边形（Polytope）。
- **迁移改写方案**：
  - 在 B 题 Q1 主求解中，**绝对不要使用 SIVIA 的离散矩形盒去像素化近似交会区域**（否则会引入人为的网格阶梯误差并白白浪费算力）；
  - 应当吸收 Jaulin & Walter 关于集合反演 $\mathbb{S} = \mathbf{y}_m^{-1}(\mathbb{Y})$ 的理论定义，但将求解器替换为计算几何中的**线性半平面求交与顶点解析计算**（结合 Gholami 2015 论文方法），直接求出精确多边形顶点；
  - 只有在未来考虑复杂地形遮挡导致射线弯曲、电磁非均匀折射、或近场非线性场强定位时，才需要重新启用完整的 SIVIA 网格反演。

### 2. 角度周期性（$360^\circ$ 环形边界）的处理
- **差异所在**：
  - 论文中的输入输出均为标准欧氏实数空间 $\mathbb{R}^n$，区间算术假定标量在实数轴上单调连续；
  - B 题中的示向度定义在 $[0^\circ, 360^\circ)$ 上，存在角度环形周期性（例如当测量读数为 $0.5^\circ$ 时，展开 $\pm 1^\circ$ 得到的区间为 $[359.5^\circ, 360^\circ) \cup [0^\circ, 1.5^\circ]$，在数值上分裂为两个区间）。
- **迁移改写方案**：
  - 若在角度空间应用区间分析，必须引入**角度区间算术（Circular Interval Arithmetic）**；或更简洁地，在直角坐标系下改用二维方向向量与其正负法向量内积来表达半平面约束，从而彻底避开标量角度跨越 $0^\circ/360^\circ$ 处的周期性奇点。

### 3. 先验搜索域与外截断约束的确定
- **差异所在**：
  - 论文在测试算例中人为指定了紧致的先验盒 $\mathbb{P} = [0, 5]^2$；
  - B 题中干扰源分布在半径 $1800\text{ m}$ 的圆形区域内，初始外包盒为 $[-1800, 1800]^2$。此外，B 题附录 2 规定各干扰源有效接收半径在 $1000\text{ m}$ 到 $1500\text{ m}$ 之间。
- **迁移改写方案**：
  - 在形成交会多边形时，若两个检测点视线夹角极小，交会多边形可能沿射线方向延伸极远甚至未闭合。此时必须引入外截断；
  - 结合附录 2，保守且绝对安全的外截断距离必须取全域物理极大值 $1500\text{ m}$，**严禁错误采用 $1000\text{ m}$ 作为截断**（否则会将位于 $1200\text{ m}$ 处的真实目标错误滤除）。

---

## J. 一页结论

### 1. 最值得保留的 3 点
1. **有界误差估计的确定性集合反演本质**：摒弃不切实际的高斯分布或随机噪声假设，严格将定位问题建模为输出误差集合的原像反演问题 $\mathbb{S} = \mathbf{y}_m^{-1}(\mathbb{Y})$，赋予交会定位最严谨的数学定义。
2. **点估计不可行陷阱与完整几何集保留**：论文通过实验确凿证明，传统外接盒中心或切比雪夫点估计可能落在非凸真实可行集之外，因而在 Q1 中必须坚持求解完整的多边形可行域，以此为基础计算直径与覆盖圆。
3. **内/外子铺砌对几何特征的双向夹逼范式**：利用内近似集与外近似集构建针对物理指标（如覆盖半径、区域面积）的确定性上界与下界，为清除圆 $20\text{ m}$ 的覆盖判断提供了绝对安全裕度分析范式。

### 2. 最关键的 1–3 个公式
- **公式 A（集合反演定义式，式 (4)）**：
  $$\mathbb{S} = \mathbf{y}_m^{-1}(\mathbf{y} - \mathbb{E}) = \mathbf{y}_m^{-1}(\mathbb{Y})$$
- **公式 B（特征量双向夹逼准则，Section 4.2）**：
  $$Z(\mathbb{K}_{\mathrm{in}}) \le Z(\mathbb{S}) \le Z(\mathbb{K}_{\mathrm{out}})$$
- **公式 C（二维搜索极低堆栈消耗界限，式 (41)）**：
  $$\#\mathrm{stack} < 2 \cdot \operatorname{int}\left( \log_2(w) - \log_2(\varepsilon_r) + 1 \right)$$

### 3. 对 B 题最直接的一个落地动作
在 B 题论文第一问建模开头，引用 Jaulin & Walter (1993) 的集合反演理论，写下公式 $\mathcal{S} = \mathbf{f}^{-1}\left(\prod_{i=1}^N [\hat{\theta}_i - 1^\circ, \hat{\theta}_i + 1^\circ]\right)$，**从数学上严格确立“示向度容许角区间反演交会构成唯一可行区域”的理论合法性**；同时引用其关于切比雪夫中心不可行的证据，论证为何 Q1 必须基于多边形几何极点求解最坏情况直径，而不是草率计算平均点坐标。

---

## 自检核验与不确定项报告

1. **正文页码与 PDF 页码核验**：
   - 经全面比对，论文发表于 *Automatica* 1993 年第 29 卷第 4 期，印刷页码为 pp. 1053–1064，PDF 共 12 页。全文满足严格映射 $\text{正文页码} = \text{PDF 页码} + 1052$。
2. **转写疑似错误核验与修正**：
   - 转写文本中 Section 1 式 (2) 前后出现的乱码符号 $\bullet_m(\mathfrak{p})$ 和 $\mathbb{R}^{n_*}$，经公式推导与上下文语义核验，确定原文为残差向量 $\mathbf{e}_m(\mathbf{p})$ 与数据空间 $\mathbb{R}^{n_y}$；
   - 转写文本中 Test Case 2 采样时刻后出现的孤立字符 `7`，经对照确定为转置符号 $(\dots)^T$ 的 OCR 误识；
   - 转写文本中 Section 4.1.3 式 (33) 附近的符号混乱，经严格数学对照修正为 Hausdorff 距离的标准解析表达。
3. **不确定项报告**：
   - 原文致谢部分提及感谢 "Professor Kurzhanski and Emmanuel Delaleau"，其中 Delaleau 在正文中未作为参考文献引用，属学术讨论致谢，不影响任何数学定理与模型推导；
   - 除上述已明确修正的 OCR 笔误外，全文数学逻辑、定理条件、算法伪代码及数值实验数据均完整确凿，无未决猜测内容。
