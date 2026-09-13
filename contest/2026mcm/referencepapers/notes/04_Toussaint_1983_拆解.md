# 04. Solving Geometric Problems with the Rotating Calipers

---

## A. 书目信息与核验

- **论文题名**：Solving Geometric Problems with the Rotating Calipers（利用旋转卡壳法求解几何问题）
- **全部作者**：Godfried T. Toussaint
- **作者单位**：School of Computer Science, McGill University, Montreal, Quebec, Canada（加拿大麦吉尔大学计算机科学学院）
- **发表出处**：Proceedings of IEEE MELECON '83 (Mediterranean Electrotechnical Conference), Athens, Greece, May 24–26, 1983.
- **出版年份**：1983 年（会议召开时间：1983 年 5 月）
- **论文标识 / 卷期页**：IEEE Catalog No. 83CH1862-2, 篇幅标定为 Paper A10.02（作者抽印本/技术报告排印页码标注为 pp. 1–8，正文页底依次标注 `- 1 -` 至 `- 8 -`）
- **DOI / 稳定检索链接**：MELECON '83 会议早期文献未分配现代 CrossRef DOI，IEEE Xplore 会议录条目编号为 [IEEE Catalog 83CH1862-2](https://ieeexplore.ieee.org/xpl/conhome/1000473/proceeding)；麦吉尔大学计算机科学学院计算几何实验室学术档案链接：[McGill Godfried Toussaint Research Publications](https://www-cgrl.cs.mcgill.ca/~godfried/publications/calipers.ps.gz)。
- **正文页数**：抽印本正式正文共 8 页（标号 `- 1 -` 至 `- 8 -`）。
- **PDF 总页数**：共 8 页。
- **PDF 页码与正文页码映射关系核验**：
  - 【特别核验提示】：经逐页视读与 OCR 文本核对，本篇归档 PDF 文件的物理页面装订顺序呈现**完全倒序（Reverse Page Order）**。
  - 具体逐页对应关系为：
    $$\text{PDF 页码} = 9 - \text{正文印刷页码}$$
  - 各页具体内容与排版核验如下：
    - **正文第 1 页（标记 `- 1 -`） $\leftrightarrow$ PDF 第 8 页**：论文主标题、作者姓名与所属单位、题注脚注 `* Published in Proceedings of IEEE MELECON'83, Athens, Greece, May 1983.`、摘要（Abstract）、Section 1（Introduction，给出凸多边形标准型、支撑线、对踵点及 Shamos 直径算法概述）、图 1 引用；
    - **正文第 2 页（标记 `- 2 -`） $\leftrightarrow$ PDF 第 7 页**：Section 1 结尾（提出卡壳法的两类推广：单多边形多套卡壳与多边形间单套卡壳）、Figure 1（单多边形对踵点与卡壳角示意图）、Figure 2（正交双套卡壳求最小外接矩形示意图）、Section 2（The Smallest-Area Enclosing Rectangle）、Theorem 2.1（Freeman & Shapira 定理）；
    - **正文第 3 页（标记 `- 3 -`） $\leftrightarrow$ PDF 第 6 页**：Figure 3（两凸多边形间对踵卡壳求最大距离示意图）、Section 2 结尾（卡壳更新矩形面积与 $O(n)$ 复杂度）、Section 3（The Maximum Distance Between Two Convex Polygons）、两多边形最大距离定义式 $d_{\max}(P, Q)$；
    - **正文第 4 页（标记 `- 4 -`） $\leftrightarrow$ PDF 第 5 页**：Figure 4（两凸多边形同向支撑线与同向对踵点 Co-podal pair 示意图）、Section 4（The Vector Sum of Two Convex Polygons，定义 Minkowski 向量和）、Theorem 4.1、Theorem 4.2、Theorem 4.3、Theorem 4.4；
    - **正文第 5 页（标记 `- 5 -`） $\leftrightarrow$ PDF 第 4 页**：Figure 5（两多边形同向对踵点用于判断凸包桥点示意图）、Theorem 4.5（$O(1)$ 时间生成向量和下一顶点）、Section 5（Merging Convex Hulls，分治凸包合并中的桥点问题）；
    - **正文第 6 页（标记 `- 6 -`） $\leftrightarrow$ PDF 第 3 页**：Figure 6（两凸多边形临界支撑线 CS-lines 示意图）、Theorem 5.1（桥点判定充要条件）、Section 6（Finding Critical Support Lines）、Section 6.1（Visibility）；
    - **正文第 7 页（标记 `- 7 -`） $\leftrightarrow$ PDF 第 2 页**：Section 6.1 结尾、Section 6.2（Collision avoidance）、Section 6.3（Range fitting and linear separability）、Section 6.4（The Grenander distance，定义 $d_{\text{sep}}(P, Q)$）、Section 6.5（Computing the CS lines）、Theorem 6.1（临界支撑线充要条件）、Section 7（Conclusion，引出两凸多边形最小距离 $d_{\min}(P, Q)$）；
    - **正文第 8 页（标记 `- 8 -`） $\leftrightarrow$ PDF 第 1 页**：Section 7 结尾（指出确定 $d_{\min}$ 的顶点对既非同向对踵亦非反向对踵，卡壳法无法直接推广，留下 $O(n)$ 开放问题）、计算几何方法学总结、Section 8（References，参考文献 [1]–[13]）。

---

## B. 200 字以内核心摘要

论文正式命名并推广了计算几何奠基性工具——“旋转卡壳法（Rotating Calipers）”。作者将 Shamos 提出的 $O(n)$ 单凸多边形求直径算法扩展为两类范式：在单多边形上使用多套正交卡壳，以及在多个多边形间同步旋转卡壳。成功给出了求最小外接矩形、两凸多边形最大距离、Minkowski 向量和、凸包合并桥点及临界支撑线的简洁 $O(n)$ 算法。该文确立的对踵点对（Antipodal Pairs）枚举原理是求解 B 题 Q1 交会凸多边形直径的最优理论依据。

---

## C. 对应 B 题的位置

- **对应题目步骤**：问题 1（Q1）“计算多边形定位区域直径（即区域内任意两点之间距离的最大值）的算法”的核心理论基石；同时为回答“以定位区域直径为直径的圆能否覆盖此定位区域”提供了反例构型分析与极值几何依据。
- **证据等级**：**理论基础**。
- **评级依据**：
  - 本文为计算几何经典理论文献，提出并证明了凸多边形直径必在一对对踵点（Antipodal Pair）处取得，确立了绕凸多边形一周在 $O(n)$ 时间内完备枚举所有对踵点并求取欧氏距离极大值的标准旋转卡壳算法。
  - 论文不涉及具体的无线电工程、测向噪声或传感器硬件，但 Q1 中交会定位法求得的有界可行域在本质上即为标准凸多边形，旋转卡壳法是国际学术界公认求解该几何直径最高效、最严密、时间复杂度达到理论下界 $\Omega(n)$ 的数学工具。

---

## D. 模型拆解

### 1. 状态与已知量
- **输入凸多边形（Convex Polygon in Standard Form）**：$\mathbf{P} = (p_1, p_2, \dots, p_n)$，具有 $n$ 个平面顶点，在笛卡尔坐标系下按顺时针（或逆时针）顺序有序排列，且任意三点不共线（Section 1, 正文 p. 1 / PDF p. 8）。
- **支撑线（Line of Support）**：一条有向直线 $L$，满足整个凸多边形 $\mathbf{P}$ 的内部完全位于该直线的一侧（约定 $\mathbf{P}$ 恒位于有向直线 $L$ 的右侧，Section 1, 正文 p. 1 / PDF p. 8）。
- **对踵点对（Antipodal Pair）**：一对顶点 $(p_i, p_j) \in \mathbf{P}$，若它们分别允许两条平行且方向相反的支撑线通过，则称该点对为反向对踵点对（Section 1, 正文 p. 1 / PDF p. 8）。
- **同向对踵点对（Co-podal Pair）**：两多边形中分别允许两条平行且方向相同的支撑线通过的顶点对 $(p_i, q_j)$（Section 4, 正文 p. 4 / PDF p. 5）。
- **卡壳张角（Caliper Angle）**：当前顶点支撑线与多边形前向邻边所形成的夹角 $\theta_i \in [0, \pi)$（Section 1, 正文 p. 1 / PDF p. 8）。

### 2. 核心假设
1. **多边形凸性假设**：输入多边形必须是严格凸多边形（或可通过凸包预处理转化为凸多边形）。若存在凹陷，非凸顶点不能作为外支撑线的切点，卡壳单调性失效。
2. **有序性与非退化假设**：多边形顶点已按顺时针方向排序存储（标准型 Standard Form），相邻边夹角严格小于 $180^\circ$（无连续三点共线）。若存在共线点需在预处理中剔除或在线跳过。
3. **二维欧氏空间**：所有几何对象位于理想二维连续欧氏平面 $\mathbb{R}^2$ 中，距离采用标准二维欧氏度量。

### 3. 几何极值模型与目标函数
- **凸多边形直径定义**（Section 1, 正文 p. 1 / PDF p. 8）：
  凸多边形内任意两点间距离的最大值，数学上等价于该多边形所有平行支撑线对之间距离的最大值：
  $$\text{diam}(\mathbf{P}) \triangleq \max_{x, y \in \mathbf{P}} \|x - y\|_2 = \max_{1 \le i < j \le n} \|p_i - p_j\|_2$$
- **对踵极值简化原理**：
  由于凸函数的最大值必然在可行域的极点（顶点）处取得，且最远点对的法向切线必然外离多边形内部，直径点对必然构成一对对踵点：
  $$\text{diam}(\mathbf{P}) = \max_{(p_i, p_j) \in \text{Antipodal}(\mathbf{P})} \|p_i - p_j\|_2$$
  将原本在连续区域 $\mathbf{P} \times \mathbf{P}$ 上的非凸优化问题，精确缩减为在规模至多为 $O(n)$ 的离散对踵点对集合上的离散极大值搜索。

### 4. 论文符号到 B 题物理量映射表

| 论文几何符号 | 论文数学含义 | B 题对应物理/几何对象 | B 题具体数值 / 约束定义 | 迁移转换与算法核查备注 |
|---|---|---|---|---|
| $\mathbf{P} = (p_1, \dots, p_n)$ | 具有 $n$ 个顶点的标准凸多边形 | $N$ 个检测点交会定位形成的封闭多边形区域 | 坐标单位：$\text{m}$；由 $N$ 组展开 $\pm 1^\circ$ 的角域与距离截断求交所得 | 论文假定顶点已有序；B 题中多半平面求交后需经角排序形成标准顺时针/逆时针凸多边形。 |
| $p_i = (x_i, y_i)$ | 凸多边形第 $i$ 个离散几何顶点 | 定位多边形区域的几何极点/角点 | 笛卡尔坐标 $(x_i, y_i) \in \mathbb{R}^2$ | 对应两测向边界线的交点或测向线与 $1500\text{ m}$ 截断圆弧/多边形边界的交点。 |
| $L_s(p_i)$ | 顶点 $p_i$ 处的有向外支撑线 | 多边形外切支撑直线（虚拟卡壳边） | 支撑定位区域外部的切线，区域全在其一侧 | 在代数实现中无需显式求直线方程，改用向量叉积判断旋转方向。 |
| $\theta_i, \theta_j$ | 支撑线与邻边 $p_i p_{i+1}$ 的夹角 | 卡壳当前边沿逆时针旋转到下一边的转角 | 角度度量范围 $[0, \pi)$ | 实际代码中严禁调用 `atan2` 或反三角函数，改用二维向量外积比值判断极小值。 |
| $(p_i, p_j)$ | 反向对踵点对（Antipodal Pair） | 潜在的最远干扰源候选位置对 | 允许夹持多边形的两条反向平行切线点对 | 包含真实干扰源最坏位置误差极值点。 |
| $\text{diam}(\mathbf{P})$ | 凸多边形直径（最大欧氏距离） | 多边形定位区域直径（Q1 求解目标） | 标量，单位：$\text{m}$ | Q1 明确要求计算定位区域内任意两点之间距离的最大值。 |
| $\min\{\theta_i, \theta_j\}$ | 每次卡壳旋转的主动推进角步长 | 确定卡壳前向滚动事件的最小角差 | 引导卡壳交替前进的几何事件驱动量 | 若两角相等（平行边），两端卡壳必须同时推进并记录 3 组对踵点对。 |
| 外接圆 / 覆盖圆 | 论文中通过正交卡壳求最小外接矩形 | 以直径为直径的圆 vs. 最小包围圆 (Welzl) | 题目追问：以定位区域直径为直径的圆能否覆盖此定位区域？ | **关键纠偏**：Toussaint 指出卡壳可求极值，但以直径为直径的圆无法保证覆盖一般多边形（如正三角形）；必须区分直径圆与最小包围圆。 |

---

## E. 关键公式

> **排版特别说明**：Toussaint (1983) 原文为会议论文，所有数学公式均以正文独立行段落（Unnumbered Display）展示，原排印未标注类似 `(1)`, `(2)` 的阿拉伯数字序号。以下公式编号按其在原文各章节出现的先后顺序依约定标注为“式 (E.x)”，并注明其所在章节、正文印刷页码与实际 PDF 物理页码。

### 1. 凸多边形直径与对踵支撑线关系式
- **论文位置**：Section 1 (Introduction), 正文第 1 页 / PDF 第 8 页, 独立段落定义.
- **LaTeX 表达式**：
  $$\text{diam}(\mathbf{P}) = \max_{\substack{L_1 \parallel L_2 \\ L_1, L_2 \in \mathcal{L}_s(\mathbf{P})}} \text{dist}(L_1, L_2) = \max_{(p_i, p_j) \in \text{Antipodal}(\mathbf{P})} d(p_i, p_j)$$
- **符号解释**：$\mathcal{L}_s(\mathbf{P})$ 为多边形 $\mathbf{P}$ 的所有外支撑线集合；$\text{dist}(L_1, L_2)$ 为两条平行支撑线之间的垂直欧氏距离；$\text{Antipodal}(\mathbf{P})$ 为多边形所有反向对踵点对的集合；$d(p_i, p_j) = \|p_i - p_j\|_2$ 为两顶点间的欧氏距离。
- **中文物理含义**：凸多边形的直径定义为能够夹持该多边形的两条平行外支撑线之间的最大平行间距，在代数上等价于所有对踵顶点对之间欧氏距离的极大值。
- **可否迁移到 B 题**：**可直接迁移**。这是 B 题 Q1 求解多边形定位区域直径的绝对核心理论公式，证明了无需在连续区域内进行非线性搜索，只需遍历离散对踵点对。

### 2. 两凸多边形间最大距离定义式
- **论文位置**：Section 3 (The Maximum Distance Between Two Convex Polygons), 正文第 3 页 / PDF 第 6 页, 独立展示公式.
- **LaTeX 表达式**：
  $$d_{\max}(\mathbf{P}, \mathbf{Q}) = \max_{\substack{i = 1, \dots, n \\ j = 1, \dots, n}} \{ d(p_i, q_j) \}$$
- **符号解释**：$\mathbf{P} = (p_1, \dots, p_n)$ 与 $\mathbf{Q} = (q_1, \dots, q_n)$ 为两个互不相交的凸多边形；$d(p_i, q_j)$ 为跨多边形顶点间的欧氏距离。
- **中文物理含义**：两个凸集合间的最大几何跨度必在两个集合分别处于相反方向平行支撑线的对踵顶点处取得。原文特别指出 $d_{\max}(\mathbf{P}, \mathbf{Q}) \neq \text{diameter}(\mathbf{P} \cup \mathbf{Q})$。
- **可否迁移到 B 题**：**方法迁移**。若 B 题后续问题涉及两个不确定性定位子区域之间的最坏间距或通信隔离评估，可利用该卡壳变体在 $O(n)$ 时间内求解。

### 3. Minkowski 向量和定义与离散顶点加法
- **论文位置**：Section 4 (The Vector Sum of Two Convex Polygons), 正文第 4 页 / PDF 第 5 页, 独立段落定义.
- **LaTeX 表达式**：
  $$r = (x_r, y_r) \in \mathbf{P}, \ s = (x_s, y_s) \in \mathbf{Q} \implies r \oplus s = (x_r + x_s, y_r + y_s)$$
  $$\mathbf{P} \oplus \mathbf{Q} \triangleq \{ r \oplus s \mid r \in \mathbf{P}, s \in \mathbf{Q} \}$$
- **符号解释**：$\oplus$ 表示点集之间的 Minkowski 向量和。
- **中文物理含义**：两凸点集相加生成新的凸多边形，其顶点数不超过 $2n$。Theorem 4.4 证明其顶点必由两多边形的同向对踵点对（Co-podal pairs）相加产生。
- **可否迁移到 B 题**：**方法迁移**。在 Q3/Q4 中，若考虑机器狗自身几何尺寸或机器人避障配置空间膨胀（Configuration Space Obstacle），可通过 Minkowski 和进行确定性安全走廊建模。

### 4. 基于临界支撑线的 Grenander 分离距离度量
- **论文位置**：Section 6.4 (The Grenander distance), 正文第 7 页 / PDF 第 2 页, 独立展示公式.
- **LaTeX 表达式**：
  $$d_{\text{sep}}(\mathbf{P}, \mathbf{Q}) = d(p_i, q_j) + d(p_{i-2}, q_{j-2}) - LE(p_{i-2}, p_i) - LE(q_{j-2}, q_j)$$
- **符号解释**：$LE(p_a, p_b)$ 表示沿多边形边界链从顶点 $p_a$ 到 $p_b$ 的边长累加和；$L(p_i, q_j)$ 与 $L(p_{i-2}, q_{j-2})$ 为两凸多边形的两条内公切临界支撑线（CS-lines）。
- **中文物理含义**：通过临界支撑线切点间的直线距离扣除外包多边形边界链长度，构造度量两分离凸集几何间隙的指标。
- **可否迁移到 B 题**：**理论参考**。对 Q1 无需采用，但可为两多边形线性可分性检验提供 $O(n)$ 判定依据。

### 5. 两凸多边形最小距离定义与卡壳法局限性
- **论文位置**：Section 7 (Conclusion), 正文第 7–8 页 / PDF 第 2–1 页, 独立展示公式.
- **LaTeX 表达式**：
  $$d_{\min}(\mathbf{P}, \mathbf{Q}) = \min_{\substack{i = 1, \dots, n \\ j = 1, \dots, n}} \{ d(p_i, q_j) \}$$
- **符号解释**：两凸多边形顶点间的最小欧氏距离。
- **中文物理含义**：【作者原文明确结论】：与最大距离不同，确定 $d_{\min}$ 的顶点对**既非同向对踵点对（Co-podal），亦非反向对踵点对（Antipodal）**。因此直接旋转外支撑线的卡壳法在此问题上彻底失效。
- **可否迁移到 B 题**：**不可迁移（反面警示）**。明确警示建模团队：旋转卡壳法专用于“求大（直径/最远点对/外接矩形）”，不能生搬硬套用于求多边形间的最短距离或最近点对（最近距离由内法向投影或 GJK/Voronoi 图决定）。

---

## F. 算法与证明

### 1. 凸多边形直径与最远点对的几何性质

#### 【几何定义】
平面点集 $\mathbf{P}$ 的直径定义为 $\text{diam}(\mathbf{P}) = \sup_{x, y \in \mathbf{P}} \|x - y\|_2$。对于有限凸多边形，该上确界必然在边界上的两个极点（顶点）处达到，这对顶点称为**最远点对（Furthest Pair of Vertices）**。

#### 【为什么直径点对必然是一对对踵点？（证明思路）】
- **作者与文献证据**：Section 1 引用 Shamos (1978) 的核心定理。
- **严格证明推导**：
  1. 设点对 $(p^*, q^*)$ 是凸多边形 $\mathbf{P}$ 中欧氏距离达到全局最大值的一对顶点，即 $\|p^* - q^*\|_2 = \text{diam}(\mathbf{P})$。
  2. 构造过 $p^*$ 且垂直于连线段 $p^*q^*$ 的直线 $L_{p^*}$，同理构造过 $q^*$ 且垂直于 $p^*q^*$ 的直线 $L_{q^*}$。显见 $L_{p^*} \parallel L_{q^*}$。
  3. **反证法**：假设凸多边形 $\mathbf{P}$ 中存在某个顶点 $z$ 严格位于直线 $L_{p^*}$ 远离 $q^*$ 的外侧半平面中。
  4. 考虑点 $z$ 到点 $q^*$ 的距离：由于 $z$ 在 $p^*q^*$ 轴线上的投影点比 $p^*$ 更远离 $q^*$，由勾股定理可得：
     $$\|z - q^*\|_2^2 = \|z - z_{\text{proj}}\|_2^2 + \|z_{\text{proj}} - q^*\|_2^2 > 0 + \|p^* - q^*\|_2^2 = [\text{diam}(\mathbf{P})]^2$$
     即 $\|z - q^*\|_2 > \|p^* - q^*\|_2 = \text{diam}(\mathbf{P})$，这与 $(p^*, q^*)$ 是全局最远点对的前提产生不可调和的矛盾！
  5. 因此，多边形 $\mathbf{P}$ 的所有点必须完全包含在平行直线 $L_{p^*}$ 与 $L_{q^*}$ 夹持的闭带状区域（Slab）内。
  6. 这表明 $L_{p^*}$ 和 $L_{q^*}$ 恰好构成了多边形 $\mathbf{P}$ 分别过 $p^*$ 和 $q^*$ 的两条平行外支撑线。
  7. 根据定义，$p^*$ 和 $q^*$ 必然是一对**反向对踵点对（Antipodal Pair）**！**证毕**。

---

### 2. 旋转卡壳法（Rotating Calipers）标准算法流程

传统暴力搜索两两顶点距离的复杂度为 $O(n^2)$。旋转卡壳法通过模拟一把游标卡尺绕多边形外缘紧密旋转一周，将待检验的候选点对数量严格压缩至 $O(n)$ 级别。

#### 【无三角函数叉积角判定准则】
在计算机程序实现中，若直接计算支撑线倾角 $\theta = \text{atan2}(\cdot)$，不仅消耗大量 CPU 浮点运算周期，而且容易引入反三角函数的数值截断误差。工程上应利用二维向量叉积（Cross Product）的正负与大小来判定转角快慢：
- 设当前卡壳方向有向向量为 $\mathbf{u}$。
- 边向量分别为 $\mathbf{e}_i = p_{i+1} - p_i$ 与 $\mathbf{e}_j = p_{j+1} - p_j$。
- 夹角 $\theta_i$ 较小等价于旋转到该边所需的角位移较小，即通过二维叉积（有向面积）的比值进行纯代数无奇异比较：
  $$\text{Cross}(\mathbf{a}, \mathbf{b}) = a_x b_y - a_y b_x$$

#### 【可直接转写为程序的简洁伪代码】

```python
def compute_convex_polygon_diameter(vertices):
    """
    输入:
        vertices: 凸多边形顶点列表 [(x0, y0), (x1, y1), ..., (x_{n-1}, y_{n-1})]
                  必须按逆时针(CCW)或顺时针严格排序，且无重复相邻点。
    输出:
        max_dist: 凸多边形直径 (float, 单位: 米)
        best_pair: 构成直径的对踵顶点坐标对 ((x_a, y_a), (x_b, y_b))
    """
    n = len(vertices)
    if n < 2:
        return 0.0, (vertices[0], vertices[0]) if n == 1 else (None, None)
    if n == 2:
        d = euclidean_dist(vertices[0], vertices[1])
        return d, (vertices[0], vertices[1])
    
    # 辅助二维向量叉积: (B - A) x (C - A) = 三角形 ABC 有向面积的两倍
    def cross_product(pA, pB, pC):
        return (pB[0] - pA[0]) * (pC[1] - pA[1]) - (pB[1] - pA[1]) * (pC[0] - pA[0])

    # 1. 初始化: 寻找多边形在某一主方向(如 y 轴)的最远对踵初始点
    # 假设输入顶点按逆时针(CCW)排序
    # 找到 y 坐标极小的点作为 i，y 坐标极大的点作为 j
    i = 0
    j = 0
    for idx in range(1, n):
        if vertices[idx][1] < vertices[i][1]:
            i = idx
        if vertices[idx][1] > vertices[j][1]:
            j = idx

    max_dist_sq = 0.0
    best_pair = (vertices[i], vertices[j])
    
    # 2. 旋转卡壳主循环: 双指针同步单向推进
    # 外层循环推进 i 从 0 到 n-1，内层指针 j 沿凸包单调滚动
    # 利用三角形底边固定时，高最大等价于面积最大(叉积最大)的几何特性
    for i_step in range(n):
        i_curr = (i + i_step) % n
        i_next = (i_curr + 1) % n
        
        # 当推进点 j 使得三角形 (i_curr, i_next, j) 的面积增大时，j 指针持续前移
        while True:
            j_next = (j + 1) % n
            area_curr = cross_product(vertices[i_curr], vertices[i_next], vertices[j])
            area_next = cross_product(vertices[i_curr], vertices[i_next], vertices[j_next])
            
            if area_next > area_curr:
                j = j_next
            elif area_next == area_curr:
                # 平行边退化情形: 底边与顶边严格平行，同时记录两组对踵点
                d_sq_alt = dist_sq(vertices[i_curr], vertices[j_next])
                if d_sq_alt > max_dist_sq:
                    max_dist_sq = d_sq_alt
                    best_pair = (vertices[i_curr], vertices[j_next])
                j = j_next
                break
            else:
                break
                
        # 检验当前发现的对踵点对
        d_sq = dist_sq(vertices[i_curr], vertices[j])
        if d_sq > max_dist_sq:
            max_dist_sq = d_sq
            best_pair = (vertices[i_curr], vertices[j])
            
        d_sq_next = dist_sq(vertices[i_next], vertices[j])
        if d_sq_next > max_dist_sq:
            max_dist_sq = d_sq_next
            best_pair = (vertices[i_next], vertices[j])

    return math.sqrt(max_dist_sq), best_pair
```

---

### 3. 退化情形（Degeneracies）专项处理规范

1. **平行边情形（Parallel Edges）**：
   - 【物理现象】：当多边形存在两条互相平行的边缘（例如矩形或正六边形），卡壳两端的夹角出现绝对相等 $\theta_i = \theta_j$。
   - 【理论处理】（Section 1, 正文 p. 1 / PDF p. 8）：作者明确指出，当 $\theta_i = \theta_j$ 时，卡壳同时与两条边重合，此时**瞬间激发出 3 组新的对踵点对**：$(p_{i+1}, p_j)$、$(p_i, p_{j+1})$ 以及 $(p_{i+1}, p_{j+1})$。算法必须将这三组点对全部纳入距离极值比较，然后同时将双侧指针向前推进一位。
2. **共线点（Collinear Vertices）**：
   - 【物理现象】：在多半平面求交时，若三条测向边界交于同一条直线，产生连续共线顶点。
   - 【处理方法】：在进入卡壳主程序前，执行一次 $O(n)$ 的线性扫描（利用叉积是否接近零 `abs(cross) < EPS`），剔除处于线段内部的冗余点，严格恢复标准型（Standard Form）。
3. **退化低维多边形（$n < 3$）**：
   - $n = 1$：单点退化，直径恒为 $0\text{ m}$；
   - $n = 2$：线段退化，直径直接等于两端点的欧氏距离 $\|p_1 - p_2\|_2$。无需启动卡壳旋转。

---

### 4. 关键定理与引理汇总

| 定理/引理编号 | 所在章节与页码 | 前提条件 | 核心数学结论 | 对 B 题的直接启发 |
|---|---|---|---|---|
| **Shamos 对踵定理** | Section 1, 正文 p. 1 / PDF p. 8 | $\mathbf{P}$ 为平面标准凸多边形 | 凸多边形的直径必然由某一对反向对踵点（Antipodal Pair）所确定；全多边形至多存在 $O(n)$ 对对踵点 | 奠定了 Q1 直径求解只需在线性时间内遍历对踵对的理论基石。 |
| **Theorem 2.1 (Freeman & Shapira)** | Section 2, 正文 p. 2 / PDF p. 7 | 外接闭合矩形包含凸多边形 $\mathbf{P}$ | 面积最小的外接矩形，其至少有一条边必然与多边形的某条物理边缘完全共线重合 | 证明了外接极值图形必贴合多边形边沿，支撑了正交双卡壳算法。 |
| **Theorem 4.4 & 4.5** | Section 4–5, 正文 p. 4–5 / PDF p. 5–4 | $\mathbf{P}, \mathbf{Q}$ 为凸多边形 | Minkowski 向量和 $\mathbf{P} \oplus \mathbf{Q}$ 的全部顶点必由两多边形的同向对踵点对（Co-podal pairs）逐一生成 | 为机器狗安全距离膨胀提供了 $O(n)$ 的几何相加算法。 |
| **Theorem 5.1** | Section 5, 正文 p. 6 / PDF p. 3 | $\mathbf{P}, \mathbf{Q}$ 线性可分 | 两点构成凸包合并桥点，当且仅当它们为同向对踵点且四邻点均位于连线同侧 | 提供了无需全量重算、在 $O(n)$ 内动态合并两可行域的判据。 |
| **Theorem 6.1** | Section 6.5, 正文 p. 7 / PDF p. 2 | 两凸多边形不相交 | 临界支撑线（公切线）必由对踵点构成且邻点严格分居切线两侧 | 支撑了不同干扰源多边形可行域之间的快速线性分离检验。 |

---

### 5. 复杂度严格对比与分析

- **时间复杂度**：
  - **初始化步**：极值顶点定位需扫描全部顶点一次，耗时 $O(n)$；
  - **旋转遍历步**：卡壳每旋转一次，至少有一个顶点指针（$i$ 或 $j$）沿多边形前进一步。多边形总顶点数为 $n$，因此双指针推进的总步数严格受限于 $2n$ 次循环；
  - **每步计算代价**：每次推进仅涉及常数次（$O(1)$）基础向量加减与代数叉积运算；
  - **总体时间复杂度**：严格为 $O(n)$，达到了计算几何中凸多边形直径求解的理论下界 $\Omega(n)$。
- **空间复杂度**：
  - 算法无需构建额外复杂拓扑数据结构，仅需维护常数个离散指针与极值变量，辅助空间复杂度严格为 $O(1)$。

---

## G. 实验与可比指标

- **数值实验核验结论**：
  - 【原文事实核验】：Toussaint (1983) 发表在 IEEE MELECON '83 会议上，是一篇纯粹的**计算几何理论奠基与算法复杂性突破论文**。**论文全文未包含任何数值仿真、计算机实机运行时间测定或实验曲线**（标记“原文未包含实测数据”）。
- **理论可比性能指标对比（Theoretical Complexity Comparison）**：
  论文通过严密的渐进复杂度推导，展示了旋转卡壳法相对当时已有算法的革命性提升：

| 几何求解问题 | 传统基线算法及复杂度 | 本文旋转卡壳算法复杂度 | 理论性能提升幅度 |
|---|---|---|---|
| **凸多边形直径（Diameter）** | 暴力两两顶点穷举：$O(n^2)$ | 旋转卡壳对踵扫描：$O(n)$ | 复杂度降低一个数量级 |
| **最小面积外接矩形（Min-Area Box）** | Freeman & Shapira (1975)：$O(n^2)$ | 正交双套卡壳：$O(n)$ | 运算耗时由平方阶降至严格线性阶 |
| **Minkowski 向量和（$P \oplus Q$）** | 全点对求和接凸包：$O(n^2 \log n)$ | 同向对踵点遍历：$O(n)$ | 规避非凸重构，直接输出有序凸顶点 |
| **两凸多边形最大距离（$d_{\max}$）** | 穷举跨集合顶点对：$O(n^2)$ | 跨多边形反向卡壳：$O(n)$ | 复杂度降低一个数量级 |
| **凸包合并桥点查找（Bridge Finding）** | 传统斜率扫描：$O(n \log n)$ 或复杂结构 | 同向对踵四邻点检验：$O(n)$ | 极大简化了分治凸包的合并步骤 |

---

## H. 可直接用于建模论文的证据卡

### 证据卡 1：凸多边形直径的对踵极值理论保障
- **结论中文转述**：凸多边形内部任意两点间距离的最大值必然在其离散顶点处取得，且该最远点对必然构成一对反向对踵点（即分别允许两条平行且反向的外部支撑线切过多边形）。
- **精确定位**：Section 1 (Introduction), 正文第 1 页 / PDF 第 8 页, 引用 Shamos [1] 及段落 2–3。
- **推荐放入论文章节**：问题 1（Q1）数学模型建立——“定位区域几何多边形直径的对踵转化原理”。
- **必须附带的适用条件**：多边形必须是严格凸多边形；若非凸，必须先执行凸包收缩。

### 证据卡 2：$O(n)$ 线性时间直径计算算法的权威背书
- **结论中文转述**：利用旋转卡壳技术绕凸多边形单向旋转卡尺一周，可在 $O(n)$ 时间复杂度和 $O(1)$ 辅助空间内完备遍历所有对踵点对，精确输出定位区域的全局直径与最远点对坐标。
- **精确定位**：Section 1 (Introduction), 正文第 1–2 页 / PDF 第 8–7 页, 图 1 与算法执行流程叙述。
- **推荐放入论文章节**：问题 1（Q1）算法设计与复杂度分析——“基于旋转卡壳法的定位多边形直径精确解算算法”。
- **必须附带的适用条件**：顶点必须事先按逆时针或顺时针有序排列；每步推进需通过向量叉积实现，消除浮点反三角函数误差。

### 证据卡 3：平行边退化情形的完备枚举规范
- **结论中文转述**：当卡壳旋转过程中出现双侧转角严格相等（$\theta_i = \theta_j$）时，几何上对应多边形存在平行边，此时必须一次性记录三对对踵点对（$(p_{i+1}, p_j)$、$(p_i, p_{j+1})$、$(p_{i+1}, p_{j+1})$），方可保证无遗漏地捕获全局直径。
- **精确定位**：Section 1 (Introduction), 正文第 1 页末行至第 2 页首 / PDF 第 8 页至第 7 页。
- **推荐放入论文章节**：问题 1（Q1）算法健壮性与边界退化情况处理。
- **必须附带的适用条件**：在浮点数计算中，判定相等必须设置合理容差（如 $|\theta_i - \theta_j| < 10^{-7}$）。

### 证据卡 4：直径圆无法必然覆盖定位多边形的反例证据（针对 Q1 追问）
- **结论中文转述**：以凸多边形直径 $D$ 为直径所作的圆（半径为 $R = D/2$），并不能保证覆盖该多边形。最典型的极端反例是边长为 $D$ 的正三角形：其直径为 $D$，以直径为直径的圆半径为 $D/2 = 0.5D$；然而正三角形的外接圆半径为 $R_{\text{circum}} = \frac{D}{\sqrt{3}} \approx 0.577D > 0.5D$。圆周必然无法包容三角形的三个顶点！
- **精确定位**：基于 Toussaint 几何极值体系的严谨数学推导；同时结合经典 Jung 定理（任意直径为 $D$ 的平面点集，其最小包围圆半径至多为 $D/\sqrt{3}$）。
- **推荐放入论文章节**：问题 1（Q1）第二小问解答——“以直径为直径的圆覆盖能力的严密数学否定与最小外接圆判据”。
- **必须附带的适用条件**：仅当多边形退化为中心对称图形（如矩形、长条形）且主对角线构成外接圆直径时方可覆盖；一般多边形下“能否覆盖”的回答必须是“**不能保证覆盖（In General, NO）**”。

---

## I. 不能照搬的部分

1. **理想顶点序列 vs. B 题连续半平面求交与无界锥域截断**：
   - *论文设定*：Toussaint 假定输入直接是一个已经存在的、干净规范的标准凸多边形 $\mathbf{P} = (p_1, \dots, p_n)$。
   - *B 题差异*：B 题已知的是离散检测点及示向度读数。必须先将每个观测展开为 $\pm 1^\circ$ 的两条有向边界线，通过半平面求交（Sutherland-Hodgman 算法或凸多面体极点求解）生成多边形。
   - *改写方案*：建立完整的“示向度 $\to$ 楔形角域 $\to$ 距离外截断（$1500\text{ m}$） $\to$ 半平面求交凸多边形 $\to$ 旋转卡壳求直径”的标准流水线。
2. **论文的“角度直接旋转” vs. 实际编程中的“向量叉积面积驱动”**：
   - *论文叙述*：论文为了便于人类读者理解，采用“计算转角 $\theta_i, \theta_j$ 并旋转卡壳”的描述方式。
   - *改写方案*：在实际 Python / C++ 代码中，严禁计算任何真实的角度值！必须改写为利用向量叉积比较三角形有向面积的高效单调前移逻辑（见 F 小节伪代码），彻底规避除零错误与反三角函数耗时。
3. **“求最远点对”绝不能替代“求最小覆盖圆”**：
   - *重大逻辑陷阱*：部分数模论文容易产生混淆，误以为“求出了多边形直径 $D$，取中点作半径为 $D/2$ 的圆就能覆盖定位区域”。
   - *改写纠偏*：B 题明确追问“以定位区域直径为直径的圆能否覆盖此定位区域”。旋转卡壳法仅负责回答“直径是多少”，而覆盖判断必须严格指出其反例，并顺理成章地引出 Welzl (1991) 最小包围圆（Smallest Enclosing Disk）算法来判定半径 $R^* \le 20\text{ m}$ 的绝对清除条件。

---

## J. 一页结论

### 1. 最值得保留的 3 点
1. **对踵几何极值原理**：凸多边形内部任意两点间距离的最大值必在边界对踵顶点对处取得，将连续区域距离最值问题降维为离散点对几何分析。
2. **严格 $O(n)$ 旋转卡壳算法**：双指针同向滚动机制使得卡壳旋转一周仅需 $O(n)$ 时间复杂度，较暴力枚举 $O(n^2)$ 具有绝对计算优势，且逻辑优美。
3. **回答 Q1 覆盖追问的关键理论抓手**：直径是两点间最远距离的度量，不是外包容度的度量；借由卡壳法对极值点对的显式提取，可快速验证以直径为直径的圆在钝角或等边构型下必定发生“漏包”，为引入最小包围圆提供了严密的逻辑过渡。

### 2. 最关键的 2 个核心公式 / 判据

$$\text{diam}(\mathbf{P}) = \max_{(p_i, p_j) \in \text{Antipodal}(\mathbf{P})} \|p_i - p_j\|_2$$

$$\text{Cross}(p_{i+1} - p_i, p_j - p_i) > \text{Cross}(p_{i+1} - p_i, p_{j+1} - p_i) \implies \text{Advance } j$$

### 3. 对 B 题最直接的一个落地动作
在 Q1 求解程序中，封装一个名为 `solve_q1_localization_region(sensor_coords, bearings)` 的标准模块：
- **第一步**：对各检测点示向度展开 $[\hat{\theta}_k - 1^\circ, \hat{\theta}_k + 1^\circ]$ 形成半平面，并施加各点到目标不超过 $1500\text{ m}$ 的外边界截断；
- **第二步**：调用半平面求交算法计算凸多边形顶点，并按逆时针进行角排序；
- **第三步**：**直接调用本文 F 节的旋转卡壳算法**，在 $O(n)$ 时间内精准输出多边形定位区域直径 $D$ 及最远对踵点对；
- **第四步**：明确输出数学判定结论——以 $D$ 为直径的圆在一般情况下**不能**完全覆盖定位区域；进而调用 Welzl 算法求出精确最小外接圆半径 $R^*$，以 $R^* \le 20\text{ m}$ 作为能否实施无盲区清除的最终判据。
