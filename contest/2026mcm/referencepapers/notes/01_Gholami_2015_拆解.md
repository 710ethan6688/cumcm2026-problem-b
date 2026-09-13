# 01. Characterizing the Worst-Case Position Error in Bearing-Only Target Localization

---

## A. 书目信息与核验

- **论文题名**：Characterizing the Worst-Case Position Error in Bearing-Only Target Localization
- **全部作者**：Mohammad Reza Gholami, Sinan Gezici, Henk Wymeersch, Erik G. Ström, Magnus Jansson
- **作者单位**：
  - KTH – Royal Institute of Technology, Stockholm, Sweden (ACCESS Linnaeus Center, Electrical Engineering)
  - Bilkent University, Ankara, Turkey (Department of Electrical and Electronics Engineering)
  - Chalmers University of Technology, Gothenburg, Sweden (Department of Signals and Systems)
- **发表出处**：2015 12th Workshop on Positioning, Navigation and Communication (WPNC)
- **出版年份**：2015 年（会议时间：2015 年 4 月）
- **DOI / 检索链接**：DOI: [10.1109/WPNC.2015.7107455](https://doi.org/10.1109/WPNC.2015.7107455)；Chalmers 机构知识库 CPL ID: [218784](http://publications.lib.chalmers.se/publication/218784)
- **正文页码**：原文排印未标注独立印刷页码，正文共 5 页（IEEE Xplore 正式出版篇幅记为 pp. 1–5）
- **PDF 总页数**：共 6 页
- **PDF 与正文页码映射关系**：
  - PDF 第 1 页为 Chalmers Publication Library (CPL) 机构知识库归档封面页（非论文正文）；
  - 正文从 PDF 第 2 页正式排印开始；
  - 映射关系全局固定为：$$\text{PDF 页码} = \text{正文相对页码} + 1$$
  - 具体逐页内容分布核验如下：
    - **正文第 1 页 $\leftrightarrow$ PDF 第 2 页**：论文标题、作者与单位信息、摘要（Abstract）、关键词、Section I（Introduction）、论文结构导引（The remainder of the paper...）；
    - **正文第 2 页 $\leftrightarrow$ PDF 第 3 页**：Section II（System Model）、式 (1)–(14)、Assumption 1、Assumption 2、Figure 1（AOA 定位可行域与多面体示意图）；
    - **正文第 3 页 $\leftrightarrow$ PDF 第 4 页**：Figure 1 题注、Remark 1、Remark 2、Section III（An Upper Bound on a Single Position Error）、式 (15)–(19)、Section IV（Simulation Results）前半段仿真参数设定；
    - **正文第 4 页 $\leftrightarrow$ PDF 第 5 页**：Section IV（Simulation Results）后半段、Figure 2（相对紧度 CDF 曲线）、Figure 3（移动目标可行集包络轨迹图）、Section V（Conclusions）、参考文献 [1]–[12]；
    - **正文第 5 页 $\leftrightarrow$ PDF 第 6 页**：参考文献 [13]–[17]。

---

## B. 200 字以内核心摘要

论文针对无线传感器网络中仅测向（AOA）目标定位问题，在测向误差有界假设下研究最坏位置误差上界。将每次测向建模为两个半平面相交的无限楔形锥域，多测点交集形成可行凸多胞形（Polytope）。证明了以参考估计点为基准的最坏位置误差严格在凸多胞形的极点（顶点）处取得，规避了非凸连续搜索；进一步提出求解包络该多胞形的最小体积外接椭球。为 B 题 Q1 有界示向误差下定位区域多边形构建与极值几何提供了严格的代数与几何理论支撑。

---

## C. 对应 B 题的位置

- **对应题目步骤**：问题 1（Q1）“有界示向误差形成多边形定位区域”、“交会定位法”与“多边形定位区域直径计算”的核心理论支撑。
- **证据等级**：**直接对应**。
- **评级依据**：论文的物理对象（二维测向 AOA 方位角）、误差设定（有界测向误差，仿真测试了 $T = 1^\circ$）、几何结构（单测点两侧展开构成楔形半平面交、多测点交集构成凸多面体/凸多边形）、极值特性（欧氏距离在凸多胞形极点/顶点达到最大值）与 B 题 Q1 附录 2 规定的交会定位法（两侧展开 $\pm 1^\circ$ 误差角交会形成多边形区域）在数学结构上完全一致。

---

## D. 模型拆解

### 1. 状态与物理量
- **目标真实未知位置**：$\mathbf{s} = [x_s, y_s]^T \in \mathbb{R}^2$（Section II, 正文 p. 2 / PDF p. 3），为二维平面上未知待估计的真实位置坐标。
- **锚节点 / 检测点位置**：已知 $N$ 个基准坐标 $\mathbf{z}_i = [x_i, y_i]^T \in \mathbb{R}^2, i = 1, \dots, N$（Section II, 正文 p. 2 / PDF p. 3）。
- **测向角观测量**：$\hat{\theta}_i$（弧度制）（Section II 式 (1), 正文 p. 2 / PDF p. 3），为第 $i$ 个锚节点测得的目标方位角。
- **参考位置估计点**：$\hat{\mathbf{s}} \in \mathbb{R}^2$（Section II 式 (3), 正文 p. 2 / PDF p. 3），为预先给出的参考定位结果（如通过最小二乘法 LS 或凸集投影法求得）。

### 2. 核心假设与专项核查
- **Assumption 1（角度与半平面约束，Section II, 正文 p. 2 / PDF p. 3）**：
  - 【作者原文结论】：作者假设 $y_s \ge y_i$，因此真实方位角恒满足 $0 \le \theta_i \le \pi$；同时假设所有锚节点的航向基准已知且统一（Orientation is known in every anchor node），均在全局坐标系下计算。
  - 【迁移对比与推导】：作者引入 $y_s \ge y_i$ 与 $0 \le \theta_i \le \pi$ 主要是为了便于使用标量正切函数 $\tan(\theta)$ 建立点斜式直线方程。然而在 B 题中，干扰源分布在半径 $1800\text{ m}$ 的圆形区域内，目标相对于检测点可以处于任意方向，方位角范围为 $[0^\circ, 360^\circ)$。若直接套用正切形式，在 $\theta \to 90^\circ$ 或 $270^\circ$ 时会出现斜率无穷大的数值奇异，且需分象限讨论。因此迁移到 B 题时，**必须放弃论文的正切半平面表达式，改用二维单位向量外积（叉积）或外法向量内积**表示全周向无奇异的半空间约束：$\mathbf{n}_k^T(\mathbf{s} - \mathbf{z}_i) \ge 0$。
- **Assumption 2（有界测量误差假设，Section II, 正文 p. 2 / PDF p. 3）**：
  - 【作者原文结论】：假设测向误差分布在有界区间内，即 $n_i \in [L_i, U_i]$，其中上下界 $L_i, U_i$ 先验已知；若未知，作者提出可通过式 (5) 利用大量平稳采样样本的样本均值差极值来进行估计。
  - 【迁移对比与推导】：B 题附录 2 明确规定“环境干扰及测向误差全局在 $[-1^\circ, 1^\circ]$ 范围内。同一地点重复检测误差不变”。因此 B 题中 $L_i = -1^\circ, U_i = +1^\circ$ 先验已知且完全对称。但需高度注意：论文式 (5) 依靠多次测量均值估计上下界的方法**在 B 题中完全不适用**，因为 B 题明确指出了同一地点重复测量的误差保持恒定（系统偏差/静态环境干扰），无法通过重复测量消除误差或估计界限。
- **最大探测距离约束（Section III 式 (15), 正文 p. 3 / PDF p. 4）**：
  - 【作者原文结论】：式 (14) 先把测向可行集定义为纯角度半空间交集 $\mathcal S=\bigcap_i\mathcal S_i$。进入“相对单个参考估计点的最坏位置误差”问题后，作者才在式 (15) 中额外加入 $\|\mathbf{s}-\mathbf{z}_i\|\le d_{\max}$，用于在角度交集无界时保证该优化问题有界；它不是式 (14) 中多胞形定义的组成部分。
  - 【迁移对比与推导——1000 m / 1500 m】：B 题中成功获得示向度意味着真实源满足 $\|\mathbf{s}-\mathbf{z}_i\|\le R_k\le1500\text{ m}$，而 $1000\text{ m}$ 只是 $R_k$ 的可能下限，不能作为统一距离上限。Q1 已明确研究交会“多边形”且正常输入预设其非空、有界，因此主定位区域应保持为纯角度交集，不必再用接收圆盘裁剪。只有另行处理无界输入或构造增强物理可行域时，才可把 $1500\text{ m}$ 作为保守必要上界；此时结果可能含圆弧，不能继续称为纯多边形，也不能仅靠边界直线交点完整表示。

### 3. 测量与误差模型
测向机测得的角度观测模型为（Section II 式 (1), 正文 p. 2 / PDF p. 3）：
$$\hat{\theta}_i = \theta_i + n_i = \mathrm{atan}\left(\frac{y_s - y_i}{x_s - x_i}\right) + n_i, \quad i = 1, \dots, N$$
在误差有界条件 $n_i \in [L_i, U_i]$ 下，真实方位角 $\theta_i$ 严格被限制在置信角区间内（Section II 式 (6), 正文 p. 2 / PDF p. 3）：
$$m_{Li} \le \theta_i \le m_{Ui}$$
其中 $m_{Li} \triangleq \max\{\hat{\theta}_i - U_i, 0\}$，$m_{Ui} \triangleq \min\{\hat{\theta}_i - L_i, \pi\}$。

### 4. 目标函数与几何可行域
- **单测点可行集（Wedge 区域）**（Section II 式 (7)–(13), 正文 p. 2 / PDF p. 3）：
  由下界方位线和上界方位线各自诱导的两个闭半空间 $\mathcal{H}_i^L$ 与 $\mathcal{H}_i^U$ 相交形成无限延伸的闭锥形角域（Wedge）：
  $$\mathcal{S}_i = \mathcal{H}_i^L \cap \mathcal{H}_i^U$$
- **联合可行多胞形（Polytope）**（Section II 式 (14), 正文 p. 2 / PDF p. 3）：
  多测点观测的联合可行域为所有单站角域的交集：
  $$\mathcal{S} = \bigcap_{i=1}^N \mathcal{S}_i$$
  $\mathcal{S}$ 作为凸半空间的有限交集，严格为凸集合；当该角度交集本身非空且有界时，它是闭合凸多边形。式 (15) 的距离约束属于后续最坏误差优化的附加条件，不应混入式 (14) 的多边形定义。
- **最坏位置误差优化模型**（Section II 式 (4) 与 Section III 式 (15), 正文 p. 2–3 / PDF p. 3–4）：
  $$v_b = \max_{\mathbf{s} \in \mathcal{S}} \|\mathbf{s} - \hat{\mathbf{s}}\|$$

### 5. 论文符号到 B 题物理量映射表

| 论文原符号 | 论文物理含义 | B 题对应对象 | B 题具体数值 / 约束定义 | 迁移转换与核查备注 |
|---|---|---|---|---|
| $\mathbf{s} = [x_s, y_s]^T$ | 未知目标节点二维坐标 | 待定位无线电干扰源位置坐标 | 二维笛卡尔平面坐标，单位：$\text{m}$，待求解真值 | 物理概念完全一致。 |
| $\mathbf{z}_i = [x_i, y_i]^T$ | 第 $i$ 个已知锚节点坐标 | 机器狗第 $i$ 个停靠检测点坐标 | 题目给定的已知检测点坐标 $(x_i, y_i)$，单位：$\text{m}$ | 物理概念完全一致。 |
| $\hat{\theta}_i$ | 锚节点测得的目标 AOA 方位角读数 | 测向机在检测点测得的示向度 | 方位角范围 $[0^\circ, 360^\circ)$，自正东向逆时针旋转 | 论文假设 $\theta \in [0, \pi]$，B 题需拓展至全局全周向角。 |
| $n_i$ | 角度测量噪声 / 随机误差 | 环境干扰及设备测向综合误差 | 全局严格限制在 $[-1^\circ, 1^\circ]$ 范围内 | 误差数值界限与论文测试的 $T=1^\circ$ 相同；但论文仿真采用截断高斯分布，B 题为确定性有界偏差且同地点重复测量不变，不可混同。 |
| $[L_i, U_i]$ | 测量误差的先验下界与上界 | 示向度误差区间的下限与上限 | $L_i = -1^\circ, U_i = +1^\circ$（对称误差区间） | B 题严格对称，单测点张角跨度为固定的 $2^\circ$。 |
| $[m_{Li}, m_{Ui}]$ | 真实方位角的严格置信区间 | 包含真实干扰源方位的射线展开边界角 | $[\hat{\theta}_i - 1^\circ, \hat{\theta}_i + 1^\circ]$ | 在角度模 $360^\circ$ 环形边界上做区间包裹与展开。 |
| $\mathcal{H}_i^L, \mathcal{H}_i^U$ | 边界角展开诱导的单侧半平面 | 测向方向线向两侧展开 $1^\circ$ 形成的半平面 | 满足向量叉积或法向内积的闭半空间 | 论文采用正切点斜式，B 题推荐采用二维向量外积式。 |
| $\mathcal{S}_i$ | 单测点对应的锥形角域（Wedge / Cone） | 单检测点展开形成的 $2^\circ$ 楔形角域 | 两条极限方位射线夹持的平面区域 | 物理与几何本质完全一致。 |
| $\mathcal{S}$ | 联合可行集（Polytope / 多面体） | 交会定位法形成的多边形定位区域 | $N$ 个检测点楔形角域的交集（四边形或多边形） | Q1 的核心几何解算实体。 |
| $d_{\max}$ | 式 (15) 中使最坏误差优化有界的最大通信/探测距离 | 各干扰源未知的有效接收半径 $R_k \in [1000, 1500]\text{ m}$ | 检测到信号意味着真实源满足 $\|\mathbf{s} - \mathbf{z}_i\| \le R_k \le 1500\text{ m}$ | 论文中为附加已知常量，不属于式 (14) 的角度多胞形。B 题若处理无界扩展可用 $1500\text{ m}$ 作保守必要上界；Q1 正常交会多边形不据此裁剪。 |
| $\mathcal{P} = \{\mathbf{p}_1, \dots, \mathbf{p}_k\}$ | 凸多胞形的可行极点集（Extreme Points） | 多边形定位区域的全部真实几何顶点 | 所有边界直线两两相交且满足全约束的离散顶点 | 计算区域直径与最小外接圆的基础离散点集。 |
| $\hat{\mathbf{s}}$ | 参考位置估计点（如 LS 解） | Q1 中可作为任意候选圆心；后续才可能解释为操作中心 | 二维参考坐标 | 论文只评估给定参考点的最坏误差，不负责选择 Q1 的直径圆心，也不直接给出清除决策。 |
| $v_b$ | 最坏位置误差上界（式 16） | 给定参考点到定位区域的最大欧氏距离 | $\max_j \|\hat{\mathbf{s}} - \mathbf{p}_j\|$ | 可用于检验以该点为圆心的候选圆是否覆盖区域；与 $20\text{ m}$ 比较属于后续清除应用。 |
| $\mathcal{B}$ | 半径为 $v_b$ 的包围球（Ball, 式 17） | 以给定参考点为圆心的区域外包圆 | 满足 $\|\mathbf{x} - \hat{\mathbf{s}}\| \le v_b$ 的圆形闭合区域 | Q1 可借其说明固定圆心的覆盖尺度；清除安全裕度是后续迁移。 |
| $\mathcal{E}$ | 最小体积外接椭球（Löwner-John 椭球） | 定位多边形的平滑外包络与主轴方向估计 | 通过半定规划求解的最小面积椭圆 | 可选的辅助几何工具，不与精确多边形混淆。 |

---

## E. 关键公式

### 公式 1：有界误差下的真值角度界限
- **原文公式编号**：式 (6)
- **章节与页码**：Section II, 正文第 2 页 / PDF 第 3 页
- **LaTeX 表达式**：
  $$\underbrace{\max\{\hat{\theta}_i - U_i, 0\}}_{\triangleq m_{Li}} \le \theta_i \le \underbrace{\min\{\hat{\theta}_i - L_i, \pi\}}_{\triangleq m_{Ui}}$$
- **符号解释**：$\hat{\theta}_i$ 为测点 $i$ 的测向角度读数；$[L_i, U_i]$ 为测向误差的上下界；$m_{Li}, m_{Ui}$ 分别为真值方位角的下界角与上界角。
- **中文含义**：在观测模型 $\hat{\theta}_i = \theta_i + n_i$ 且 $n_i \in [L_i, U_i]$ 的约束下，目标真实方位角必定落在由读数反推的闭区间 $[m_{Li}, m_{Ui}]$ 内。
- **可否迁移到 B 题**：**完全可迁移**。代入 B 题误差范围 $L_i = -1^\circ, U_i = +1^\circ$，并去除 $[0, \pi]$ 的局部截断，即可得到真实方位的严格角界限 $[\hat{\theta}_i - 1^\circ, \hat{\theta}_i + 1^\circ]$。

### 公式 2：单侧半平面解析不等式
- **原文公式编号**：式 (7)–(12)
- **章节与页码**：Section II, 正文第 2 页 / PDF 第 3 页
- **LaTeX 表达式**：
  $$\mathcal{H}_i^L \triangleq \left\{ \mathbf{s} \;\middle|\; \begin{aligned} \mathbf{a}_{li}^T \mathbf{s} &\ge b_{li}, && \text{if } m_{Li} \le \frac{\pi}{2} \\ \mathbf{a}_{li}^T \mathbf{s} &\le b_{li}, && \text{if } m_{Li} \ge \frac{\pi}{2} \end{aligned} \right\}, \quad \mathcal{H}_i^U \triangleq \left\{ \mathbf{s} \;\middle|\; \begin{aligned} \mathbf{a}_{ui}^T \mathbf{s} &\ge b_{ui}, && \text{if } m_{Ui} \le \frac{\pi}{2} \\ \mathbf{a}_{ui}^T \mathbf{s} &\le b_{ui}, && \text{if } m_{Ui} \ge \frac{\pi}{2} \end{aligned} \right\}$$
  其中：
  $$\mathbf{a}_{li} \triangleq [-\tan(m_{Li}), 1]^T, \quad b_{li} \triangleq -\tan(m_{Li})x_i + y_i$$
  $$\mathbf{a}_{ui} \triangleq [-\tan(m_{Ui}), 1]^T, \quad b_{ui} \triangleq -\tan(m_{Ui})x_i + y_i$$
- **符号解释**：$\mathbf{s} = [x_s, y_s]^T$ 为平面内任意待检点；$\mathbf{a}_{li}, \mathbf{a}_{ui}$ 为边界直线的法向量；$b_{li}, b_{ui}$ 为点斜式截距。
- **中文含义**：利用平面几何点斜式直线方程，将角度区间的两条边界线形式化为二维线性半空间不等式。
- **可否迁移到 B 题**：**需改写表达后迁移**。论文公式依赖正切函数 $\tan(m)$，在 $90^\circ$ 或 $270^\circ$ 处存在除零无穷大奇异性。迁移到 B 题时应采用向量叉积形式：记射线单位向量为 $\mathbf{u}(\phi) = [\cos\phi, \sin\phi]^T$，以 $(\mathbf{u} \times (\mathbf{s} - \mathbf{z}_i))_z \ge 0$ 表达半平面。

### 公式 3：多测点交集可行多胞形（Polytope）
- **原文公式编号**：式 (14)
- **章节与页码**：Section II, 正文第 2 页 / PDF 第 3 页
- **LaTeX 表达式**：
  $$\mathbf{s} \in \mathcal{S} = \bigcap_{i=1}^N \mathcal{S}_i = \bigcap_{i=1}^N \left(\mathcal{H}_i^L \cap \mathcal{H}_i^U\right)$$
- **符号解释**：$N$ 为检测点总数；$\mathcal{S}_i$ 为第 $i$ 个检测点形成的无限角域（Wedge）；$\mathcal{S}$ 为联合可行集。
- **中文含义**：未知目标的真实物理位置必须同时满足所有观测站的测向误差范围，因此严格属于所有半平面的有限交集（凸多面体）。
- **可否迁移到 B 题**：**直接对应并完全迁移**。这正是 B 题 Q1 中“两组或多组方向线各向两侧展开 $1^\circ$ 误差角相交形成多边形定位区域”的严格集合论数学表达。

### 公式 4：最坏位置误差优化模型
- **原文公式编号**：式 (15)
- **章节与页码**：Section III, 正文第 3 页 / PDF 第 4 页
- **LaTeX 表达式**：
  $$\begin{array}{rll} v_b = & \max_{\mathbf{s}} & \|\mathbf{s} - \hat{\mathbf{s}}\| \\ & \text{s.t.} & \mathbf{s} \in \displaystyle\bigcap_{i=1}^N \mathcal{S}_i \\ & & \|\mathbf{s} - \mathbf{z}_i\| \le d_{\max}, \quad i = 1, \dots, N \end{array}$$
- **符号解释**：$\hat{\mathbf{s}}$ 为参考估计坐标；$\mathbf{z}_i$ 为锚节点坐标；$d_{\max}$ 为最大通信与探测距离；$v_b$ 为最坏情况下的欧氏距离上界。
- **中文含义**：在可行多面体内寻找距离估计点最远的点，以此表征最坏情况定位偏差。引入距离约束 $d_{\max}$ 是为了保证在交角平行等未闭合退化情形下可行域仍为紧致有界集。
- **可否迁移到 B 题**：**可作为异常输入的扩展处理，不是 Q1 主模型**。若角度交集无界而又需要建立物理有界区域，可利用成功观测蕴含的 $1500\text{ m}$ 必要上界；但加入圆盘后集合一般带圆弧，不再是题目所称的交会多边形。Q1 正常情形直接假设角度交集非空、有界即可。

### 公式 5：极点处取得最坏误差的解析极值定理
- **原文公式编号**：式 (16)
- **章节与页码**：Section III, 正文第 3 页 / PDF 第 4 页
- **LaTeX 表达式**：
  $$v_b = \max_{j=1,\dots,k} \|\hat{\mathbf{s}} - \mathbf{p}_j\|$$
- **符号解释**：$\mathcal{P} = \{\mathbf{p}_1, \dots, \mathbf{p}_k\}$ 为凸多胞形 $\mathcal{S}$ 的全体极点（Extreme Points，即几何顶点）集合；$k$ 为极点总数。
- **中文含义**：在有界凸多胞形上，欧氏距离最大值严格在集合的极点（顶点）处取得，无需在连续多边形内部进行非凸全局网格搜索。
- **可否迁移到 B 题**：**核心理论基石**。
  - 【作者结论】：凸多胞形上点到固定参考点的欧氏距离最大值必然在顶点达到。
  - 【迁移推导至 B 题直径】：B 题 Q1 要求的“多边形直径”定义为区域内任意两点距离最大值 $D = \max_{\mathbf{s}_1, \mathbf{s}_2 \in \mathcal{S}} \|\mathbf{s}_1 - \mathbf{s}_2\|$。利用凸分析极大值原理，固定 $\mathbf{s}_1$ 时最大值关于 $\mathbf{s}_2$ 在顶点取得；再固定 $\mathbf{s}_2$ 时关于 $\mathbf{s}_1$ 亦在顶点取得。因此多边形直径必然在顶点对之间取得：$D = \max_{\mathbf{p}_a, \mathbf{p}_b \in \mathcal{P}} \|\mathbf{p}_a - \mathbf{p}_b\|$。

### 公式 6：最坏误差包围球（Ball）
- **原文公式编号**：式 (17)
- **章节与页码**：Section III, 正文第 3 页 / PDF 第 4 页
- **LaTeX 表达式**：
  $$\mathcal{B} \triangleq \{\mathbf{x} \in \mathbb{R}^2 \mid \|\mathbf{x} - \hat{\mathbf{s}}\| \le v_b\} \implies \mathbf{s} \in \mathcal{B}$$
- **符号解释**：$\hat{\mathbf{s}}$ 为球心（估计点）；$v_b$ 为包围球半径；$\mathcal{B}$ 为外包闭球域。
- **中文含义**：以估计点为圆心、以最坏位置误差为半径构造的闭圆盘，百分之百覆盖未知目标的真实位置。
- **可否迁移到 B 题**：**Q1 可作固定圆心覆盖检验的辅助公式**。若候选圆心为 $\hat{\mathbf{s}}$，半径至少取 $v_b$ 才能覆盖整个定位区域。将其与 $20\text{ m}$ 比较并解释为清除保证属于后续任务，而非 Q1 必答。

### 公式 7：最小体积外接椭球（Löwner-John 椭球）
- **原文公式编号**：式 (18)–(19)
- **章节与页码**：Section III, 正文第 3 页 / PDF 第 4 页
- **LaTeX 表达式**：
  $$\mathcal{E} \triangleq \{\mathbf{x} \mid \|\mathbf{B}\mathbf{x} + \mathbf{d}\| \le 1\}$$
  $$\begin{array}{ll} \min_{\mathbf{B}, \mathbf{d}} & \log\det \mathbf{B}^{-1} \\ \text{s.t.} & \|\mathbf{B}\mathbf{p}_j + \mathbf{d}\| \le 1, \quad j = 1, \dots, k \end{array}$$
  *(注：原文式 (19) 约束下标印刷为 $i=1,\dots,N$，结合上下文及凸优化标准模型，约束对象显然为多胞形的 $k$ 个顶点 $\mathbf{p}_j$，属原文印刷笔误)*。
- **符号解释**：$\mathbf{B} \in \mathbb{S}_{++}^2$ 为对称正定矩阵；$\mathbf{d} \in \mathbb{R}^2$ 为位移向量；$\mathbf{p}_j$ 为多胞形顶点。
- **中文含义**：在不依赖任何参考估计点 $\hat{\mathbf{s}}$ 的前提下，通过凸优化（半定规划）直接求解包裹凸多边形的最小面积椭圆。
- **可否迁移到 B 题**：**可作为可选对比与不确定度形状分析工具**。B 题 Q1 核心要求是求精确多边形直径及判断以直径为直径的圆是否能覆盖区域。外接椭球可作为辅助工具用于刻画定位误差长短轴各向异性，但不应与精确多边形算法混淆。

---

## F. 算法与证明

### 1. 算法流程：两两直线求交与半空间筛选极点
- **来源与位置**：Section IV 第 1 段, 正文第 3 页 / PDF 第 4 页。
- **作者原文表述**：“To find the extreme points, we first calculate all the crossing points between every pair of lines and then check which points belong to the intersection of halfplanes.”
- **算法伪代码**：
  ```text
  输入：
    - 检测点坐标集合 {z_i = [x_i, y_i]^T}, i = 1, ..., N
    - 示向度观测读数 {θ_hat_i}, i = 1, ..., N
    - 误差界限 ±1°，形成边界角区间 [θ_hat_i - 1°, θ_hat_i + 1°]
  输出：
    - 多边形有序几何顶点集合 P_sorted

  步骤 1（生成边界直线）：
    对每个测点 i，由两个边界角生成 2 条射线所在直线方程 L_{i,1}, L_{i,2}，共 2N 条直线。

  步骤 2（候选交点枚举）：
    初始化候选点集合 C = ∅。
    遍历所有直线对 (L_a, L_b) (1 ≤ a < b ≤ 2N)：
      若 L_a 与 L_b 不平行（法向量线性无关）：
        计算其唯一几何交点坐标 q = L_a ∩ L_b，加入集合 C。

  步骤 3（半空间约束剪枝过滤）：
    初始化可行极点集合 P = ∅。
    遍历候选点集合中的每个点 q ∈ C：
      bool is_feasible = true;
      对所有 2N 个半平面约束 H_m (m = 1, ..., 2N)：
        若 q 不满足半平面约束 H_m（即点位于楔形角域外侧）：
          is_feasible = false;
          break;
      若 is_feasible == true：
        将 q 加入集合 P。

  步骤 4（去重与逆时针排序）：
    剔除数值重合点；
    计算集合 P 的几何中心 c = mean(P)；
    按各点关于中心 c 的极角 atan2(y - c_y, x - c_x) 从小到大排序，得到有序顶点序列 P_sorted。
  ```

- **计算复杂度专项核查（不得编造复杂度）**：
  - 【作者原文明确说明】：在 Section III（正文 p. 3 / PDF p. 4），作者明确指出：“Note that finding the extreme points of the polytope $\mathcal{S}$ is not difficult if $N$ is not large, specially for 2D networks.” **原文通篇未给出任何关于渐进复杂度的大 O 公式，也未量化定义何为“$N$ 不大”**。
  - 【迁移推导 / 实现复杂度分析】：
    在算法实现中：
    1. $2N$ 条直线两两求交，产生候选交点个数最多为 $\binom{2N}{2} = \frac{2N(2N-1)}{2} = O(N^2)$；
    2. 对每个候选交点代入 $2N$ 个半平面不等式进行验证，单点验证耗时为 $O(N)$；
    3. 因此两两求交与代数剪枝的总时间复杂度在算法实现上为 $O(N^2 \times N) = O(N^3)$；
    4. 后续极角排序耗时为 $O(k \log k)$，其中极点数 $k \le O(N^2)$。
    因此该直接枚举实现的渐进复杂度为 $O(N^3)$；这是依据流程得到的实现推导，不是原论文给出的复杂度结论。实际运行时间和数值稳健性需要由后续实现测试确认。

### 2. 关键定理与证明依据
- **命题（式 16）**：凸多胞形 $\mathcal{S}$ 上的最坏欧氏距离 $v_b = \max_{\mathbf{s} \in \mathcal{S}} \|\hat{\mathbf{s}} - \mathbf{s}\|$ 必在极点集 $\mathcal{P}$ 处达到。
- **证明依据（凸分析极大值原理）**：
  1. 考察目标函数 $f(\mathbf{s}) \triangleq \|\hat{\mathbf{s}} - \mathbf{s}\|$。欧氏范数与仿射变换复合后仍为凸函数；这里不需要、也不应宣称该函数在整个平面上严格凸；
  2. 可行域 $\mathcal{S}$ 为紧致（有界闭合）的凸集；
  3. 根据凸分析经典极大值原理（Bauer's Maximum Principle），定义在紧凸集上的连续凸函数的全局极大值必然在其极点集合（Extreme Points）上取得；
  4. 二维凸多面体（凸多边形）的极点即为其边界拐角处的几何顶点集 $\mathcal{P} = \{\mathbf{p}_1, \dots, \mathbf{p}_k\}$。故 $\max_{\mathbf{s} \in \mathcal{S}} f(\mathbf{s}) = \max_{\mathbf{p} \in \mathcal{P}} f(\mathbf{p})$。
- **迁移推导至 B 题直径计算**：
  - B 题 Q1 求解多边形直径 $D \triangleq \max_{\mathbf{s}_1, \mathbf{s}_2 \in \mathcal{S}} \|\mathbf{s}_1 - \mathbf{s}_2\|$；
  - 固定任意点 $\mathbf{s}_1 \in \mathcal{S}$，函数 $g(\mathbf{s}_2) = \|\mathbf{s}_1 - \mathbf{s}_2\|$ 关于 $\mathbf{s}_2$ 是凸函数，极大值必在顶点达到，即 $\mathbf{s}_2^* \in \mathcal{P}$；
  - 同理，固定顶点 $\mathbf{s}_2^*$，函数 $h(\mathbf{s}_1) = \|\mathbf{s}_1 - \mathbf{s}_2^*\|$ 关于 $\mathbf{s}_1$ 亦为凸函数，极大值亦必在顶点达到，即 $\mathbf{s}_1^* \in \mathcal{P}$；
  - 从而严格证明：**凸多边形定位区域的直径必然在多边形顶点对之间取得**：
    $$D = \max_{\mathbf{p}_a, \mathbf{p}_b \in \mathcal{P}} \|\mathbf{p}_a - \mathbf{p}_b\|$$
    这为 Q1 只需遍历顶点对（或结合旋转卡壳算法）计算直径提供了不可动摇的数学证明。

---

## G. 实验与可比指标

### 1. 实验场景与基线配置
- **位置**：Section IV, 正文第 3–4 页 / PDF 第 4–5 页。
- **网络拓扑与锚节点**：
  - 二维网络布设 $N=11$ 个锚节点，沿 $x$ 轴均匀排列：$\mathbf{z}_i = [5(i-1), 0]^T, i=1,\dots,11$（坐标范围 $x \in [0, 50]\text{ m}, y = 0\text{ m}$）；
  - 目标沿二次曲线运动：$y = 0.001x^2 - 0.01x + 10$（纵坐标在 $y \approx 10\text{ m}$ 附近）；
  - 每次目标位置处进行 100 次独立的蒙特卡洛噪声试验；
  - 参考位置 $\hat{\mathbf{s}}$ 采用最小二乘估计（Least Squares, LS）。

### 2. 评价指标与关键结论专项核查
- **相对紧度指标（Relative Tightness）**（Section IV, 正文 p. 4 / PDF p. 5）：
  $$\tau_v \triangleq \frac{v_b - e(\mathbf{s})}{e(\mathbf{s})} = \frac{v_b - \|\hat{\mathbf{s}} - \mathbf{s}\|}{\|\hat{\mathbf{s}} - \mathbf{s}\|}$$
  考察其经验累积分布函数 $\Pr\{\tau_v \le x\}$。$\tau_v \ge 0$，该值越小说明最坏误差界限与实际误差越贴近，上界越紧致。

- **专项核查 1：Figure 2 仅作近似图读**：
  - 【作者原文说明】：原文正文第 4 页第 2 段阐述了随着噪声区间增大，可行多面体 $\mathcal{S}$ 变大，上界相应变大，相对紧度降低。
  - 【特别核查说明】：**论文正文未提供任何量化分位数数值表**。对 Figure 2 进行目测近似读图（仅作定性参考与近似经验读数，绝非理论证明值）：
    - 在 $T = 1^\circ$ 曲线中，当横坐标相对紧度 $x \approx 2.0$ 时，对应的纵坐标 CDF 约为 $0.80$（即约 $80\%$ 的噪声实现下相对紧度在 2 以内）；
    - 当 $T$ 扩大到 $10^\circ$ 和 $15^\circ$ 时，CDF 曲线明显向右下方平移，相对紧度严重劣化；
    - **严正声明**：任何具体百分比数字（如 80%）仅系对 Figure 2 曲线的视觉目测近似估计，原文无表格支撑，论文写作中不得伪造为作者给出的精确理论结论。

- **专项核查 2：截断高斯分布与确定性 $\pm 1^\circ$ 误差机理差异**：
  - 【论文实验设置】：作者在仿真中将测向误差 $n_i$ 设定为区间 $[-\pi T/180, \pi T/180]$ 上的截断高斯分布（Truncated Gaussian Distribution），方差设定为 $\sigma^2 = 1$。
  - 【B 题物理机制差异】：
    1. **随机统计 vs 确定性区间**：截断高斯分布具有强烈的中心集中趋势，其大部分抽样样本集中在 $0^\circ$ 附近，落在边界 $\pm T$ 处的极端概率极低；因此图 2 的紧度体现的是高斯噪声下的统计平均特性。而 B 题附录 2 规定的是“环境干扰及测向误差全局在 $[-1^\circ, 1^\circ]$ 范围内”，属于典型的未知但有界（Unknown-but-Bounded）确定性误差集合，没有任何概率密度函数的先验假设；
    2. **重复测量特性**：B 题特别强调“同一地点重复检测误差不变”，说明误差包含不可消除的固定环境扰动或天线安装偏差。因此，绝对不能将高斯噪声下的蒙特卡洛统计均值或置信度结论直接等同于 B 题的确定性最坏情况几何保证。

- **几何构型对可行域的决定性影响（GDOP 效应）**（Section IV, 正文 p. 4 / PDF p. 5, Figure 3）：
  - 实验表明：当目标位于测点阵列正上方且各测点视角张角较大（接近正交）时，多边形可行域紧致且各向均匀；
  - 当目标移动至阵列侧翼或远端、测点视角趋于平行或共线时，可行多边形被显著拉长为窄长细条状，最坏误差上界剧烈上升；
  - 比较集合包络发现：最小体积外接椭球（MinVolEllip）的面积/体积在大部分情形下明显小于单点估计外包球（UppBall）。

---

## H. 可直接用于建模论文的证据卡

### 证据卡 1：测向角误差界限导出凸多边形定位区域
- **结论转述**：在测向误差具有严格先验上下界的前提下，单次测向读数对应一个无限楔形锥域，多次独立测向的可行交集严格表现为一个凸多胞形（Polytope / 二维凸多边形）。
- **精确定位**：Section II, 正文第 2 页 / PDF 第 3 页，式 (7)–(14) 及 Remark 1。
- **推荐放入论文**：问题 1（Q1）模型建立的“交会定位法几何模型与定位区域形式化”部分。
- **适用条件**：测向误差严格有界；各检测点方位角基准统一；目标处于视线可达范围内。

### 证据卡 2：多边形最坏位置误差与区域直径在极点取得
- **结论转述**：欧氏距离是凸函数；在有界凸多胞形上，其最大值至少可在某个极点（顶点）处取得。因此无需连续网格搜索，只需遍历离散顶点集即可精确确定最坏位置误差；进一步对两个变量依次应用该性质，可知多边形直径存在一对顶点实现。
- **精确定位**：Section III, 正文第 3 页 / PDF 第 4 页，式 (16)。
- **推荐放入论文**：问题 1（Q1）模型求解的“定位区域直径计算定理与证明”部分。
- **适用条件**：可行区域为紧致（有界且闭合）的凸多胞形。

### 证据卡 3：两两直线相交与半空间剪枝求极点算法
- **结论转述**：通过计算所有误差界限直线的两两交点，并利用全套半平面代数不等式进行约束剪枝，可以在低计算复杂度下精确、稳定地提取多边形的全体极点。
- **精确定位**：Section IV, 正文第 3 页 / PDF 第 4 页，第 1 自然段。
- **推荐放入论文**：问题 1（Q1）算法设计的“交会多边形顶点生成与剪枝算法步骤”部分。
- **适用条件**：二维网络平面；测点数适中。

### 证据卡 4：无界角域的可选物理有界化
- **结论转述**：当测向线夹角过小或视线平行导致多面体未闭合时，可依据物理上可检测信号的最大接收距离 $d_{\max}$ 引入二次范数约束，确保可行解集紧致有界。
- **精确定位**：Section III, 正文第 3 页 / PDF 第 4 页，式 (15)。
- **推荐放入论文**：仅作为无界输入的扩展说明；Q1 主体直接采用非空、有界交会多边形的正常性假设。
- **适用条件**：确需处理无界角度交集且存在物理探测上限。加入圆盘约束后集合可能含圆弧，不能继续沿用纯多边形的直线交点表示。

---

## I. 不能照搬的部分

| 差异维度 | Gholami (2015) 论文设定 | 2026 全国数模 B 题设定 | 迁移改造与适配策略 |
|---|---|---|---|
| **坐标与角度范围** | 假设 $y_s \ge y_i$，将角度限定在 $[0, \pi]$，使用点斜式 $\tan\theta$ 表达半平面（Assumption 1, 式 7–12） | 干扰源分布在全平面，方位角为全周向 $[0^\circ, 360^\circ)$，包含垂直与反向视线 | **严禁照搬正切公式**。必须改用无奇异的二维向量外积：设测向单位向量为 $\mathbf{u}(\phi) = [\cos\phi, \sin\phi]^T$，以 $(\mathbf{u} \times (\mathbf{s} - \mathbf{z}_i))_z \ge 0$ 表达半平面，杜绝 $90^\circ/270^\circ$ 斜率发散。 |
| **测量误差机理** | 仿真中采用截断高斯分布，大部分误差集中在零附近；式 (5) 假设可通过重复多次测量样本均值来估计界限 | 附录 2 规定为确定性有界误差 $[-1^\circ, 1^\circ]$，且明确“同一地点重复检测误差不变” | **不得套用高斯统计结论或重复测量均值法**。B 题为未知但有界的确定性区间，必须严格在最坏情况几何意义下推导保证，重复测量无法缩小误差区间。 |
| **探测距离物理含义** | 式 (14) 先定义纯角度可行集；式 (15) 才加入已知 $d_{\max}$ 使最坏误差优化有界 | 附录 2 规定各源有效接收半径在 $1000\text{ m}$ 到 $1500\text{ m}$ 之间且具体值未知 | $1000\text{ m}$ 不能作为统一距离上限。若另行处理无界物理可行域，可用 $1500\text{ m}$ 作必要上界；Q1 正常交会多边形不使用距离圆盘裁剪。 |
| **优化目标函数** | 计算以参考估计点 $\hat{\mathbf{s}}$ 为基准的最坏单点误差 $v_b = \max \|\mathbf{s} - \hat{\mathbf{s}}\|$（式 16） | Q1 明确要求计算“多边形定位区域直径”（区域内任意两点最大距离） | **将单点极值拓展为顶点对极大值**。利用极值定理推导出多边形直径为所有离散顶点对之间的最大欧氏距离 $D = \max_{a, b} \|\mathbf{p}_a - \mathbf{p}_b\|$。 |
| **覆盖圆判定** | 构造以 $\hat{\mathbf{s}}$ 为中心的外包球 $\mathcal{B}$（式 17）或最小体积外接椭球 $\mathcal{E}$（式 18–19） | Q1 明确设问：“以定位区域直径为直径的圆能否覆盖此定位区域？” | 论文未直接回答该设问。Q1 应对由最远点对确定的直径圆盘直接检验全部多边形顶点；最小包围圆只可作为解释两种覆盖尺度差异的辅助对象。 |
| **算法计算复杂度** | 原文仅定性指出在二维网络且 $N$ 不大时求解不难，未给出理论复杂度证明 | 建模论文要求清晰阐明算法计算量与实时性 | **明确注明复杂度为实现推导而非原文证明**。直接两两求交并逐约束检验的实现复杂度为 $O(N^3)$；实际耗时和对近似平行边界的数值稳定性须通过测试确认。 |

---

## J. 一页结论

### 1. 最值得保留的 3 点
1. **测向有界误差的半空间代数化建模**：将角度误差严格转化为线性半平面交集，把复杂的测向交会不确定度转化为严格的凸多胞形（Convex Polytope）。
2. **极大值在极点达到的凸分析性质**：严格证明了欧氏距离极大值必然在凸多胞形顶点处取得，奠定了 Q1 计算多边形直径只需在有限离散顶点对间搜索的理论依据。
3. **两两直线相交与半空间约束检验算法**：提供了一种在低维小测点场景下极其简单、鲁棒且高效的极点生成与多边形构建方法。

### 2. 最关键的 2 个公式
1. **联合可行多胞形定义（式 14）**：
   $$\mathbf{s} \in \mathcal{S} = \bigcap_{i=1}^N \left(\mathcal{H}_i^L \cap \mathcal{H}_i^U\right)$$
2. **极点最值定理（式 16）**：
   $$\max_{\mathbf{s} \in \mathcal{S}} \|\hat{\mathbf{s}} - \mathbf{s}\| = \max_{j=1,\dots,k} \|\hat{\mathbf{s}} - \mathbf{p}_j\|$$

### 3. 对 B 题最直接的一个落地动作
在 Q1 建模论文中，将题目附录 2 的交会定位法形式化定义为半空间交集的凸多边形；利用式 (16) 的凸极值定理严格证明区域直径 $D = \max_{\mathbf{p}_a, \mathbf{p}_b \in \mathcal{P}} \|\mathbf{p}_a - \mathbf{p}_b\|$，并采用 Section IV 的两两直线相交与半平面约束筛选算法实现多边形顶点提取与直径的精确高效求解。
