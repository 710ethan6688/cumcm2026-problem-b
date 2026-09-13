# B题 18 篇论文：Antigravity 精读拆解任务单

> 用途：请 Antigravity 从 18 篇论文 PDF 中只提取对数学建模 B 题有用的证据、公式与算法，不做全文翻译，不复述无关背景。
>
> 配套材料：`papers/00_B题.pdf`、`B题_Q1-Q4文献调研整理稿.md`、`papers/` 下各论文 PDF。

## 0. 任务目标

围绕 B 题四个问题建立“题目步骤—论文证据”链：

1. **Q1：**有界示向误差如何形成可行多边形，如何求多边形直径，以及如何判断能否被半径 20 m 的清除范围覆盖；
2. **Q2：**第一次观测后，如何选择第二检测点，并兼顾定位精度、最坏情况与移动/测量时间；
3. **Q3：**多个全向源、未知数量和位置时，如何保证发现、逐步定位并规划运动；
4. **Q4：**定向源下如何处理方向性可见区域、无信号（negative evidence）、多视角观测和部分可观测决策。

文献标签含义：

- **直接对应：**数学对象、误差形式或目标函数与 B 题高度一致，可直接支撑主模型；
- **方法迁移：**原应用或噪声假设不同，但算法框架可以改造后用于本题；
- **理论基础：**支撑某个几何、优化或集合估计步骤，不代表论文直接研究 B 题。

---

## 1. 文件目录与完整性状态

### 1.1 已下载并校验（18 篇）

| 编号 | 文件名 | 对应问题 | 标签 |
|---:|---|---|---|
| 01 | `01_Gholami_2015_WorstCase_BearingOnly.pdf` | Q1 | 直接对应 |
| 02 | `02_Colle_Galerne_2013_Set_Inversion.pdf` | Q1 | 直接对应/方法迁移 |
| 03 | `03_Jaulin_Walter_1993_SIVIA.pdf` | Q1 | 理论基础 |
| 04 | `04_Toussaint_1983_Rotating_Calipers.pdf` | Q1 | 理论基础 |
| 05 | `05_Welzl_1991_Smallest_Enclosing_Disks.pdf` | Q1 | 理论基础 |
| 06 | `06_Tokekar_Isler_2013_Bounded_Bearing_Placement.pdf` | Q2 | 直接对应 |
| 07 | `07_Dogancay_Hmam_2008_Optimal_Angular_Separation.pdf` | Q2 | 直接理论支撑 |
| 08 | `08_VanderHook_2014_Cautious_Greedy.pdf` | Q2 | 直接对应/方法迁移 |
| 09 | `09_Dogancay_2012_UAV_Path_Planning.pdf` | Q2 | 方法迁移 |
| 10 | `10_Song_2011_Limited_Sensing_Search.pdf` | Q3 | 方法迁移 |
| 11 | `11_Song_2012_Multiple_Radio_Sources.pdf` | Q3 | 直接对应/方法迁移 |
| 12 | `12_Bai_2023_Multi_Radiation_Search.pdf` | Q3 | 方法迁移 |
| 13 | `13_Choset_2001_Coverage_Robotics.pdf` | Q3 | 理论基础 |
| 14 | `14_Ryan_Hedrick_2010_Information_Active_Sensing.pdf` | Q3/Q4 | 方法迁移 |
| 15 | `15_Koch_2007_Negative_Evidence.pdf` | Q4 | 方法迁移 |
| 16 | `16_Guvensan_Yavuz_2011_Directional_Coverage.pdf` | Q4 | 理论基础/方法迁移 |
| 17 | `17_Bercea_2016_Angle_Constraints.pdf` | Q4 | 理论基础/方法迁移 |
| 18 | `18_Huo_2020_Autonomous_Radioactive_Search.pdf` | Q4 | 方法迁移 |

### 1.2 完整性核验

- 目录中共有 18 篇论文，编号 01–18 连续，无缺号；
- 18 个文件均通过 PDF 结构解析检查；
- 论文题名均已通过元数据、文本首页或扫描首页核对；
- 文件夹分布：Q1 共 5 篇、Q2 共 4 篇、Q3 共 5 篇、Q4 共 4 篇；
- 第 13 篇为扫描型 PDF，Antigravity 拆解前需要先执行 OCR；其余论文具有可提取文本层。

---

## 2. Antigravity 的统一输出规范

请为每篇论文生成一个单独的 Markdown 文件：

```text
notes/01_Gholami_2015_拆解.md
notes/02_Colle_Galerne_2013_拆解.md
...
notes/18_Huo_2020_拆解.md
```

每篇必须使用以下固定结构：

```markdown
# 编号 + 论文题名

## A. 书目信息与核验
- 作者、年份、题名、期刊/会议、卷期页、DOI/稳定链接
- PDF 页数；正文页码与 PDF 页码是否一致

## B. 200 字以内核心摘要
- 论文解决什么问题
- 使用什么模型/算法
- 得到什么主要结论

## C. 对应 B 题的位置
- 对应 Q1/Q2/Q3/Q4 的哪一步
- 证据等级：直接对应 / 方法迁移 / 理论基础
- 一句话说明为何属于该等级

## D. 模型拆解
- 状态、已知量、决策变量、观测量
- 核心假设
- 测量/误差模型
- 目标函数与约束

## E. 关键公式
对每条公式给出：论文公式编号、章节、正文页码、PDF 页码、LaTeX、符号解释、中文含义、可否迁移到 B 题。

## F. 算法与证明
- 算法步骤或伪代码
- 输入、输出、停止条件、复杂度
- 关键定理/引理的条件与结论

## G. 实验与可比指标
- 场景、参数、基线、评价指标、主要数值结论
- 只保留能帮助 B 题设计算法或实验的结果

## H. 可直接用于建模论文的证据卡
- 结论的中文转述
- 精确定位：章节 + 页码 + 公式/定理/图表编号
- 推荐放入 B 题论文的章节
- 必须附带的适用条件

## I. 不能照搬的部分
- 噪声、传感器、目标运动、探测距离、维数、先验等差异
- 若迁移，需要怎样改写

## J. 一页结论
- 最值得保留的 3 点
- 最关键的 1–3 个公式
- 对 B 题最直接的一个落地动作
```

### 强制质量要求

1. 所有结论必须标明**章节、正文页码、PDF 页码**；公式还要保留原编号。
2. 不要凭摘要补写正文；看不清或正文未给出时标记“原文未明确”，不要猜。
3. 不做大段逐字摘录。证据以中文转述为主；确需原句时，每处最多 1–2 句。
4. 必须区分“作者已经证明/实验验证”和“我们据此推导/迁移”。
5. 必须记录适用条件，尤其是高斯噪声、有界噪声、目标位置已知/未知、传感器量程、连续测量/停靠测量。
6. 对 B 题无关的综述背景、历史沿革和常规介绍可跳过。
7. 公式中的角度单位、坐标系、方位角定义和符号方向必须注明。
8. 若 PDF 为扫描版，先 OCR；页码定位仍按 PDF 页码记录。

---

# 3. Q1：有界示向误差、可行域、直径与清除判据

## 01. Gholami et al. (2015)

**Characterizing the Worst-Case Position Error in Bearing-Only Target Localization**  
标签：**直接对应**；Q1 主文献。

重点拆解：

- 有界 AOA/bearing 误差如何表示为上下界 `L_i, U_i`；
- 每次观测对应的两个半平面（或 wedge）及其公式；
- 单次可行集 `S_i` 与多次观测交集 `S=∩S_i`；
- 交集为何是凸集，何时成为有界 polytope；
- worst-case position error 与可行域极点/顶点的关系；
- 数值实验中“边界线两两求交，再检验是否满足全部约束”的算法；
- 外包椭球若有，作为可选近似方法单列，不与精确多边形混淆。

需要产出：一张“论文符号 → B 题检测点/示向度/±1°/定位区域”的映射表。

## 02. Colle & Galerne (2013)

**Mobile robot localization by multiangulation using set inversion**  
标签：**直接对应/方法迁移**。

重点拆解：

- 多角度定位的非线性有界误差模型与状态向量；
- 角度测量如何变成集合约束；
- set inversion / SIVIA 的实际工作流程；
- 传感器或模型误差、异常观测如何处理；
- 算法精度参数、计算量和实时性讨论；
- 为什么保留可行集合比输出单一估计点更合适。

特别说明：本题二维固定测点、±1° 边界可能可直接化成半平面，需指出何时无需动用完整 SIVIA。

## 03. Jaulin & Walter (1993)

**Set Inversion via Interval Analysis for Nonlinear Bounded-Error Estimation**  
标签：**理论基础**。

重点拆解：

- feasible parameter set 的严格定义；
- 区间盒、包含函数（inclusion function）和集合反演；
- SIVIA 伪代码及三类盒：确定可行、确定不可行、不确定边界；
- 内近似/外近似、收敛与分辨率参数；
- 计算复杂度或维数灾难相关说明；
- 哪些内容可支撑“有界误差不应默认概率分布”。

只作理论引用，不把通用区间算法写成本题唯一必要算法。

## 04. Toussaint (1983)

**Solving Geometric Problems with the Rotating Calipers**  
标签：**理论基础**。

重点拆解：

- 凸多边形直径与最远点对定义；
- antipodal pairs 的定义和枚举方式；
- 旋转卡壳求凸多边形直径的算法/伪代码；
- 为什么至少一对对踵点包含直径点对的证明思路；
- 时间复杂度；
- 平行边、共线点、重复顶点等退化情形。

需要产出：可直接转写为程序流程的简洁伪代码。

## 05. Welzl (1991)

**Smallest Enclosing Disks (Balls and Ellipsoids)**  
标签：**理论基础**。

重点拆解：

- 最小包围圆问题定义；
- 解由 2 个或 3 个边界支撑点决定的性质；
- 随机递归算法的输入、递归不变量和终止条件；
- 期望线性时间结论及成立条件；
- “最小包围圆”与“以多边形直径为直径的圆”为什么不是同一个概念；
- 如何把最小包围圆半径 `r* ≤ 20 m` 写成清除保证判据。

## Q1 综合输出

完成上述 5 篇后，另写 `notes/Q1_证据链.md`，按以下链条汇总：

```text
±1° 有界示向误差
→ wedge/半平面约束
→ 多观测交集形成凸多边形
→ 顶点/边界构造
→ 旋转卡壳求直径
→ 最小包围圆检验 20 m 清除条件
```

每个箭头必须指定至少一篇论文和精确定位；自行推导的部分明确写“由题意推导”。

---

# 4. Q2：第二检测点与主动定位

## 06. Tokekar & Isler (2013)

**Sensor Placement and Selection for Bearing Sensors with Bounded Uncertainty**  
标签：**直接对应**；Q2 主文献。

重点拆解：

- 每个 bearing 观测形成 `2α` wedge 的模型；
- 多 wedge 交集及直径/面积不确定性指标；
- worst case 中究竟对目标位置、噪声还是传感器选择取最坏；
- 下界引理、三角网格布置或其他保证性结论；
- sensor placement 与 sensor selection 的区别；
- 论文结果对“第一次测量后自适应选择第二点”的可迁移方式；
- 所有几何保证成立所需的区域、传感器数和角误差条件。

## 07. Doğançay & Hmam (2008)

**Optimal Angular Sensor Separation for AOA Localization**  
标签：**直接理论支撑，但需限制适用范围**。

重点拆解：

- AOA 测量模型、噪声分布和 Fisher information matrix；
- FIM 行列式或其他最优准则的具体公式；
- Theorem 1（或相应定理）的最优角间隔条件；
- `N=2` 时为何推出约 `90°` 交会角；
- 距离权重、传感器到目标距离是否固定；
- 证明/结论依赖的高斯、小误差或局部近似条件。

必须明确：90° 是局部统计最优几何依据，不是未知距离、有界误差和行程代价下的无条件答案。

## 08. Vander Hook, Tokekar & Isler (2014)

**Cautious Greedy Strategy for Bearing-Only Active Localization: Analysis and Field Experiments**  
标签：**直接对应/方法迁移**。

重点拆解：

- 总任务时间目标中测量次数、每次测量时间、移动距离/速度的组合；
- 定位区域直径或精度阈值约束；
- 单次 bearing 的 wedge/双楔形歧义模型；
- `β-cautious` 策略的完整伪代码、候选动作和参数意义；
- 初始化策略；
- 理论上下界或近似保证；
- 仿真和外场实验使用的基线、指标和关键结论。

重点映射到本题：第二点选择不能只看几何精度，还应加入新增行驶时间与停靠测量时间。

## 09. Doğançay (2012)

**UAV Path Planning for Passive Emitter Localization**  
标签：**方法迁移**。

重点拆解：

- 被动辐射源 AOA 模型；
- 近似 FIM/CRLB 目标；
- waypoint 优化的目标函数和飞行约束；
- successive / receding-horizon 重新规划流程；
- 仿真几何、比较策略和结果；
- 哪些内容仅适用于 UAV 动力学，哪些可迁移为地面检测车的候选点滚动优化。

## Q2 综合输出

完成 4 篇后写 `notes/Q2_证据链.md`，回答：

1. 为什么保留第一次观测的整条楔形可行域；
2. 候选第二点如何计算最坏交集直径/面积；
3. 90° 交会角是启发式、局部最优还是全局保证；
4. 如何把“移动时间 + 测量时间 + 定位精度”合并为可计算准则；
5. 哪一部分是论文直接结论，哪一部分是针对 B 题的新组合。

---

# 5. Q3：多全向源搜索、发现与定位

## 10. Song, Kim & Yi (2011)

**On the Time to Search for an Intermittent Signal Source Under a Limited Sensing Range**  
标签：**方法迁移**。

重点拆解：

- 有限感知范围、间歇信号和搜索区域的假设；
- expected search time 的定义、公式与变量；
- slap method、random walk 等策略；
- 渐近结论与适用条件；
- 搜索轨迹与覆盖保证的关系；
- 如果 B 题只能停靠测量，连续移动感知策略应如何改为离散停靠点。

## 11. Song, Kim & Yi (2012)

**Simultaneous Localization of Multiple Unknown and Transient Radio Sources Using a Mobile Robot**  
标签：**直接对应/方法迁移**；Q3 主文献。

重点拆解：

- 信号源数量、位置未知且信号短暂时的建模；
- SPOG（若原文如此命名）的状态/图结构、事件与更新方程；
- 何时认为一个源已定位；
- ridge-walking 或对应的探索运动机制；
- 完整运动规划/定位算法；
- random walk、fixed route 等基线；
- 评价指标、实验参数和主要数值结果；
- 若 B 题按频道区分信号源，如何简化论文中的数据关联困难。

## 12. Bai et al. (2023)

**A Study of Robotic Search Strategy for Multi-Radiation Sources in Unknown Environments**  
标签：**方法迁移**。

重点拆解：

- Observation–Estimation–Exploration（OEE）整体架构；
- ADE-PSPF 或相应估计器只保留理解框架所需的核心方程；
- radiation gain / 信息收益指标；
- RRT、滚动规划或下一步动作生成方式；
- 探索—利用目标函数；
- boustrophedon、next-best-view 等比较基线；
- 成功率、搜索时间、行程或定位误差结果；
- 明确辐射强度物理模型为何不能直接替换 B 题的示向度观测。

## 13. Choset (2001)

**Coverage for Robotics—A Survey of Recent Results**  
标签：**理论基础**。

重点拆解：

- coverage path planning 与 completeness 的定义；
- heuristic、approximate、partial、exact cellular 等分类；
- exact cellular / boustrophedon decomposition 的核心思想；
- 完备覆盖结论成立的空间与传感器条件；
- 路径连续扫过区域与“只能在停靠点测量”的本题差异；
- 如何将本题改写为停靠点半径 1000 m 圆并集覆盖半径 1800 m 区域。

## 14. Ryan & Hedrick (2010)

**Particle Filter Based Information-Theoretic Active Sensing**  
标签：**方法迁移**。

重点拆解：

- 状态、传感器和 belief/粒子滤波模型；
- receding-horizon entropy 或 mutual information 目标；
- 预测条件熵/信息增益公式；
- Monte Carlo 近似与计算流程；
- 动作选择—观测—更新循环和复杂度；
- 非高斯、有限量程或非线性情形下使用粒子的理由；
- 如何把熵指标替换为本题可解释的可行集直径、面积或排除率。

## Q3 综合输出

写 `notes/Q3_证据链.md`，至少给出：

- 1000 m 探测范围下的**停靠点覆盖保证**；
- 频道独立状态如何降低多源数据关联难度；
- 全局发现、局部定位、20 m 清除三类动作如何滚动切换；
- 时间目标应含行程、停靠测量次数和清除时间；
- 一组可用于仿真的基线：固定覆盖、随机、贪心最近、信息驱动/滚动策略。

---

# 6. Q4：定向源、无信号与多视角搜索

## 15. Koch (2007)

**On Exploiting ‘Negative’ Sensor Evidence for Target Tracking and Sensor Data Fusion**  
标签：**方法迁移**；Q4 主文献之一。

重点拆解：

- negative evidence 的准确定义；
- “本应检测到但没有检测到”如何进入似然或 Bayes 更新；
- `p(z=∅ | x)`、漏检概率或类似核心公式；
- 使用负信息必须具备怎样的检测概率、视场、量程或遮挡模型；
- 论文示例中负信息带来的改进；
- 模型失配时把无信号当成强排除证据的风险。

映射 B 题时必须区分无信号的多种原因：超出 1000 m、位于定向源背向半平面、漏检或频道不存在。

## 16. Guvensan & Yavuz (2011)

**On Coverage Issues in Directional Sensor Networks: A Survey**  
标签：**理论基础/方法迁移**。

重点拆解：

- directional sensing model：视角/AoV、工作方向、LoS、量程；
- directional sensor network 与全向传感网络的关键差异；
- 方向覆盖问题的分类和评价指标；
- 方向调整、节点移动、多重覆盖等策略；
- 二维扇形/半平面模型的关键公式和图；
- 如何利用几何对偶，将“定向传感器看目标”迁移为“固定方向发射源被检测车接收”；
- 综述结论中不能直接当作本题算法保证的部分。

## 17. Bercea, Isler & Khuller (2016)

**Minimizing Uncertainty through Sensor Placement with Angle Constraints**  
标签：**理论基础/方法迁移**。

重点拆解：

- angular `α`-coverage 的严格定义；
- 带距离、可见性或障碍约束的问题形式；
- 近似算法与近似比；
- `α ≤ π/3` 等条件若存在，说明它们在定理中的作用；
- 为什么同一目标需要来自不同方向的传感器对；
- 如何迁移为 Q4 的多视角停靠点设计；
- 明确论文定理为何不能直接保证未知发射方向、未知源位置下的 B 题解。

## 18. Huo et al. (2020)

**Autonomous Search of Radioactive Sources through Mobile Robots**  
标签：**方法迁移**。

重点拆解：

- POMDP 的状态、动作、观测、转移与奖励；
- 辐射源观测/误差模型；
- Bayesian 参数更新；
- 行为选择、搜索终止和找到源的判据；
- 关键公式（重点检查原文式 (3)–(4)、式 (21) 附近，但以实际 PDF 为准）；
- 仿真与机器人实验的指标和结果；
- 哪些只适用于辐射强度衰减，哪些可迁移为 Q4 的“位置—类型—方向”belief。

## Q4 综合输出

写 `notes/Q4_证据链.md`，形成以下闭环：

```text
位置 + 全向/定向类型 + 发射方向的联合候选状态
→ 有信号：bearing 楔形 + 距离 + 发射半平面
→ 无信号：在检测模型条件下删除或降权候选状态
→ 选择能区分类型/方向的多视角下一点
→ 更新 belief/可行集
→ 定位并满足 20 m 清除条件
```

必须单列“无信号不能直接等于目标不存在”的风险说明。

---

# 7. 最终跨论文交付物

完成 18 篇后再生成 `notes/18篇论文_证据矩阵.md`，包含以下表格：

| B题步骤 | 论文编号 | 证据等级 | 原文结论 | 精确页码/公式 | 本题如何采用 | 必要改动 | 风险 |
|---|---:|---|---|---|---|---|---|

并给出以下四项：

1. **每问的主文献：**每问最多 2–3 篇，避免堆砌引用；
2. **算法组件表：**半平面求交、直径、最小包围圆、第二点选择、覆盖、信息更新、负证据；
3. **假设冲突表：**有界/高斯误差、停靠/连续测量、单源/多源、全向/定向、已知/未知源数；
4. **引用候选句：**每篇最多 3 句中文学术转述，附精确定位和适用条件。

最终不要替我们虚构“论文已解决 B 题”。正确表述应类似：

> 某论文直接支撑其中一个数学步骤；我们再依据 B 题的停靠测量、±1° 有界误差、1000 m 探测范围和 20 m 清除半径完成组合与改造。

---

# 8. 十八篇参考文献核对表

1. Gholami, M. R., et al. (2015). *Characterizing the Worst-Case Position Error in Bearing-Only Target Localization*. WPNC.
2. Colle, E., & Galerne, S. (2013). *Mobile Robot Localization by Multiangulation Using Set Inversion*. Robotics and Autonomous Systems, 61(1), 39–48.
3. Jaulin, L., & Walter, E. (1993). *Set Inversion via Interval Analysis for Nonlinear Bounded-Error Estimation*. Automatica, 29(4), 1053–1064.
4. Toussaint, G. T. (1983). *Solving Geometric Problems with the Rotating Calipers*. IEEE MELECON '83.
5. Welzl, E. (1991). *Smallest Enclosing Disks (Balls and Ellipsoids)*. LNCS 555, 359–370.
6. Tokekar, P., & Isler, V. (2013). *Sensor Placement and Selection for Bearing Sensors with Bounded Uncertainty*. IEEE ICRA, 2515–2520.
7. Doğançay, K., & Hmam, H. (2008). *Optimal Angular Sensor Separation for AOA Localization*. Signal Processing, 88(5), 1248–1260.
8. Vander Hook, J., Tokekar, P., & Isler, V. (2014). *Cautious Greedy Strategy for Bearing-Only Active Localization: Analysis and Field Experiments*. Journal of Field Robotics, 31(2), 296–318.
9. Doğançay, K. (2012). *UAV Path Planning for Passive Emitter Localization*. IEEE Transactions on Aerospace and Electronic Systems, 48(2), 1150–1166.
10. Song, D., Kim, C.-Y., & Yi, J. (2011). *On the Time to Search for an Intermittent Signal Source Under a Limited Sensing Range*. IEEE Transactions on Robotics, 27(2), 313–323.
11. Song, D., Kim, C.-Y., & Yi, J. (2012). *Simultaneous Localization of Multiple Unknown and Transient Radio Sources Using a Mobile Robot*. IEEE Transactions on Robotics, 28(3), 668–680.
12. Bai, H., et al. (2023). *A Study of Robotic Search Strategy for Multi-Radiation Sources in Unknown Environments*. Robotics and Autonomous Systems, 169, 104529.
13. Choset, H. (2001). *Coverage for Robotics—A Survey of Recent Results*. Annals of Mathematics and Artificial Intelligence, 31, 113–126.
14. Ryan, A., & Hedrick, J. K. (2010). *Particle Filter Based Information-Theoretic Active Sensing*. Robotics and Autonomous Systems, 58(5), 574–584.
15. Koch, W. (2007). *On Exploiting ‘Negative’ Sensor Evidence for Target Tracking and Sensor Data Fusion*. Information Fusion, 8(1), 28–39.
16. Guvensan, M. A., & Yavuz, A. G. (2011). *On Coverage Issues in Directional Sensor Networks: A Survey*. Ad Hoc Networks, 9(7), 1238–1255.
17. Bercea, I. O., Isler, V., & Khuller, S. (2016). *Minimizing Uncertainty through Sensor Placement with Angle Constraints*. CCCG 2016.
18. Huo, J., et al. (2020). *Autonomous Search of Radioactive Sources through Mobile Robots*. Sensors, 20(12), 3461.
