# 09. Kutluyıl Doğançay (2012) - UAV Path Planning for Passive Emitter Localization

---

## A. 书目信息与核验

- **作者 (Authors)**: Kutluyıl Doğançay (Senior Member, IEEE)
- **年份 (Year)**: 2012 (投稿编号 IEEE Log No. T-AES/48/2/943809，出版于 2012 年 4 月)
- **题名 (Title)**: UAV Path Planning for Passive Emitter Localization
- **期刊/会议 (Journal)**: IEEE Transactions on Aerospace and Electronic Systems (IEEE T-AES)
- **卷期页 (Volume, Issue, Pages)**: Vol. 48, No. 2, pp. 1150–1166
- **DOI / 稳定链接**: DOI: [10.1109/TAES.2012.6178054](https://doi.org/10.1109/TAES.2012.6178054)
- **PDF 总页数**: 17 页 (PDF pp. 001–017)
- **正文页码与 PDF 页码核对**:
  - 期刊正式印刷起始页为 p. 1150，终止页为 p. 1166；
  - 映射关系满足严格单调线性关系：$\text{正文页码} = \text{PDF 页码} + 1149$（例如 PDF p. 001 对应正文 p. 1150，PDF p. 008 对应正文 p. 1157，PDF p. 017 对应正文 p. 1166）；两者严格对应，无跳页、漏页或错排。
- **转写质量核验与疑点标记 (OCR Glitches & Ambiguities)**:
  - MinerU 机械转写已覆盖全部 17 页并包含图表关联，但在数学符号、下标与特殊字符上存在多处典型识别退化，本笔记依据数理逻辑与上下文显式甄别并标记如下：
    1. **下标字母退化 [疑点 1]**：正文 p. 1152 (PDF p. 003) 公式 (1) 后文字说明中出现 $\Delta y_i(k) = s_\mathrm{v} - p_i^\mathrm{v}(k)$ 与 $\Delta x_i(k) = s_\mathrm{x} - p_i^\mathrm{x}(k)$，此处 $v$ 系印刷体斜体 $y$ 被误识为 $v$，标准应为 $s_y - p_i^y(k)$。
    2. **希腊字母丢失 [疑点 2]**：正文 p. 1152 (PDF p. 003) II-C 节首段中“Assuming prior knowledge of the emitter scan rate !”丢失扫描角速度符号，结合公式 (5) 可知该符号为 $\omega$。
    3. **矢量符号乱码 [疑点 3]**：正文 p. 1153 (PDF p. 004) III-A 节首段文字中出现“vector of exact AOA values as a function of emitter location s: μ(s)”，结合公式 (9) 原文实为粗体向量 $\boldsymbol{\theta}(\mathbf{s})$；同页末段“determined by °”中度数符号 `°` 实为路径损耗指数 $\gamma$；公式 (15)–(16) 处 subtended angle vector 转写出现乱码 `®(s)`，实为 $\boldsymbol{\alpha}(\mathbf{s})$。
    4. **误差椭圆与信息量符号退化 [疑点 4]**：正文 p. 1155 (PDF p. 006) 公式 (24) 上下文中“1-¾ error ellipse”系 $1\text{-}\sigma$ 误识（$1\sigma$ 标准误差椭圆，覆盖率 $39.4\%$）；同页末段“minimizing ln ©(s)”实为最小化负对数行列式 $-\ln |\Phi(\mathbf{s})|$（即 D-最优设计）。
    5. **极限符号缺失 [疑点 5]**：正文 p. 1158 (PDF p. 009) 第 2 自然段中转写为 `As \mu  0`，箭头丢失，依上下文应为 $\mu \to 0$；转弯率符号 $\varphi$ 在同页第 4 自然段被识为撇号 `'`。
    6. **角度单位误作正负号 [疑点 6]**：正文 p. 1160 (PDF p. 011) VI-A 节第 2 自然段中出现“optimal sensor placement is given by 60± or 120± separation”及“180± u-turn”，此处 `±` 均为度数单位符号 $^\circ$（即 $60^\circ$、$120^\circ$ 与 $180^\circ$）。
    7. **通信距离参数识别乱码 [疑点 7]**：正文 p. 1162 (PDF p. 013) VI-D 节与 Fig. 12 标题中通信距离上限参数转写为 `½ = 7 km`，实为参数 $\rho = 7\text{ km}$。

---

## B. 200 字以内核心摘要

针对多无人机协同定位静止无线电辐射源问题，本文提出一种基于最大化近似 Fisher 信息阵（FIM）行列式（D-最优准则，等价于极小化置信误差椭圆面积）的滚动时域（Receding-Horizon）单步航路点优化算法。系统融合极大似然估计（MLE）与卡尔曼滤波进行目标位置递归估计，并以此构造预测 FIM。通过内点法对数障碍函数处理通信距离上限与圆形禁飞区规避约束，并引入转角限幅适配运动学约束。仿真验证了该航迹规划能显著优于直飞策略，并在风扰下表现出强鲁棒性。

---

## C. 对应 B 题的位置

- **对应题目步骤**: 
  - **直接对应与主要启发：问题 2（第二检测点优选策略与候选区域给出）**；
  - **扩展迁移应用：问题 3 与问题 4（机器狗自主搜索清除中的连续滚动航路点决策与多站位协同观测）**。
- **证据等级**: **方法迁移 (Methodology Transfer)**。
- **一句话评定依据**:
  - 论文研究的是多连续飞行无人机在**高斯测向噪声**下基于**局部最优 Fisher 信息量（D-最优准则）**的单步滚动航路点非线性规划；而 B 题是地面机器狗在**确定性有界误差 $[-1^\circ, 1^\circ]$** 下针对全向干扰源进行的**第二检测点离散优选（综合考虑最坏情况几何定位不确定度与移动/停靠时间代价）**。其“预测信息增益驱动的航路点优化框架”及“避障内点罚函数/运动学受限补偿机制”可深度迁移至 B 题，但目标函数需从高斯协方差椭圆转译为有界多边形直径/面积。

---

## D. 模型拆解

### 1. 状态、已知量、决策变量与观测量
- **状态变量 (State Variables)**:
  - 目标未知二维平面坐标 $\mathbf{s} = [s_x, s_y]^\top$（静止目标）。
  - 各无人机平台在离散时刻 $k$ 的物理位置 $\mathbf{p}_i(k) = [p_i^x(k), p_i^y(k)]^\top \in \mathbb{R}^2$（$i=1,\ldots,N$）。
  - 目标位置的卡尔曼滤波后验状态估计 $\mathbf{s}(k|k) \in \mathbb{R}^2$ 及其后验协方差矩阵 $\mathbf{P}(k|k) \in \mathbb{R}^{2 \times 2}$。
- **已知量与系统参数 (Known Parameters)**:
  - 无人机恒定巡航速率 $v$（仿真中为 $30\text{ m/s}$），航路点更新步长周期 $T$（仿真中为 $10\text{ s}$），单步航程 $\Delta d = vT$。
  - 最大单步偏航转弯角 $\varphi$（仿真中取 $40^\circ$，对应最大角速度 $4^\circ/\text{s}$）。
  - 机间最大通信距离（连通性阈值）$\rho$。
  - 环境威胁/禁飞区参数：障碍中心 $\mathbf{c}_j$ 与所需物理安全间隔 $\kappa_j$（$j=1,\ldots,M$）。
  - 传感器测向基准噪声方差 $\sigma_\mathrm{A}^2$、路径损耗指数 $\gamma$（信噪比衰减模型）。
  - 障碍惩罚因子 $\mu$（仿真中设定极小常数 $10^{-10}$）。
- **决策变量 (Decision Variables)**:
  - 第 $k$ 步各无人机下一步位移控制矢量的方向角 $\vartheta_i(k) \in (-\pi, \pi]$，合成航路点控制矢量 $\mathbf{u}_i(k) = vT [\cos \vartheta_i(k), \sin \vartheta_i(k)]^\top$。
  - 下一时刻预定航路点 $\mathbf{p}_i(k+1) = \mathbf{p}_i(k) + \mathbf{u}_i(k)$。
- **观测量 (Observations)**:
  - 测向角（AOA）观测值：$\hat{\theta}_i(k) = \theta_i(k) + n_i^\mathrm{A}(k)$，其中 $\theta_i(k) = \arctan \frac{s_y - p_i^y(k)}{s_x - p_i^x(k)}$。
  - （文中混合体制还涵盖 TDOA 距离差 $\hat{g}_{ij}(k)$ 与天线扫描周期时差 SC 夹角 $\hat{\alpha}_{ij}(k)$）。

### 2. 核心假设
- **[原文假设 1] 辐射源静止不变**：发射源在二维平面内空间位置固定不变，即 $\mathbf{s}(k+1) = \mathbf{s}(k)$（Sec. III-B, 正文 p. 1154 / PDF p. 005）。
- **[原文假设 2] 测向噪声为零均值高斯白噪声且空间独立**：$n_i^\mathrm{A}(k) \sim \mathcal{N}(0, \sigma_i^2)$，不同无人机间测向误差统计独立（Sec. II-A, 正文 p. 1152 / PDF p. 003）。
- **[原文假设 3] 测向误差方差随距离呈幂律衰减**：$\sigma_{i,\mathrm{A}}^2 = \sigma_\mathrm{A}^2 \|\mathbf{s} - \mathbf{p}_i(k)\|^\gamma$（$0 \le \gamma < 2$），即距离越近、信噪比越高、测向精度越高（Sec. III-A, 正文 p. 1153 / PDF p. 004）。
- **[原文假设 4] 航路点离散同步更新与恒速巡航**：所有无人机以相同巡航速率 $v$ 在离散周期 $T$ 节点同步采样并进行下一步航路点规划（Sec. IV-A, 正文 p. 1154 / PDF p. 005）。
- **[原文假设 5] CRLB 与 FIM 近似有效性**：假定极大似然估计近似达到无偏 Cramér-Rao 下界，优化目标直接采用滤波状态 $\mathbf{s}(k|k)$ 处的预测 FIM 行列式，忽略高阶非线性偏差（Sec. IV-B, 正文 p. 1155 / PDF p. 006）。

### 3. 测量与误差模型
- 真实几何方位角定义为测向站指向辐射源的连线与笛卡尔坐标系横轴之夹角：
  $$\theta_i(k) = \mathrm{atan2}(\Delta y_i(k), \Delta x_i(k)) \in (-\pi, \pi]$$
- 测量噪声协方差矩阵对角线元素与距离关联：
  $$\boldsymbol{\Sigma}_\mathrm{A}(\mathbf{s}) = \sigma_\mathrm{A}^2 \mathrm{diag}\left( \|\mathbf{d}_1^\mathrm{A}(\mathbf{s})\|^\gamma, \ldots, \|\mathbf{d}_{N_\mathrm{A}}^\mathrm{A}(\mathbf{s})\|^\gamma \right)$$

### 4. 目标函数与约束体系
- **规划目标（极小化预测不确定度）**:
  $$\min_{\boldsymbol{\vartheta}(k)} f(\boldsymbol{\vartheta}(k), \boldsymbol{\pi}(k), \mathbf{s}(k|k)) = \frac{1}{|\Phi(\boldsymbol{\pi}(k+1), \mathbf{s}(k|k))|}$$
  其中 $|\Phi|$ 表示预测 Fisher 信息阵的行列式（D-最优准则）。
- **不等式约束 (Inequality Constraints)**:
  1. 机间最大通信间距：$g_{1ij}(\boldsymbol{\vartheta}(k)) = \|\mathbf{p}_i(k+1) - \mathbf{p}_j(k+1)\| - \rho \le 0$。
  2. 障碍物/禁飞区规避硬约束：$g_{2ij}(\boldsymbol{\vartheta}(k)) = \kappa_j - \|\mathbf{p}_i(k+1) - \mathbf{c}_j\| \le 0$。
- **转弯率动力学优先级约束 (Turn Rate Kinematics)**:
  $$|\vartheta_i(k+1) - \vartheta_i(k)| \le \varphi$$
  该约束具有最高优先级，先在无转角限制下求解内点法航向，随后通过硬限幅（hard-limiting）强制执行。

### 5. 论文符号到 B 题映射表 (Symbol Mapping to Problem B)

| 论文符号 | 论文物理含义 (Dogancay 2012) | 对应 B 题实体 / 概念 | B 题数学记号与取值 | 差异与迁移改写处理 |
|:---|:---|:---|:---|:---|
| $\mathbf{s} = [s_x, s_y]^\top$ | 静止无线电发射源坐标 | 未知全向/定向干扰源真实坐标 | $\mathbf{s}^* = (x_0, y_0) \in \mathcal{D}_{1800}$ | B 题原点在中心，分布在半径 $1800\text{ m}$ 圆域内，初始完全未知 |
| $\mathbf{p}_i(k)$ | 第 $i$ 架无人机在第 $k$ 步的航路点坐标 | 机器狗在第 $k$ 次检测时的停靠站位坐标 | $\mathbf{p}_k = (x_k, y_k)$ | 无人机为连续航路点，机器狗为停靠测量点（Q2 为选定 $\mathbf{p}_2$） |
| $\hat{\theta}_i(k)$ | 无人机测得的 AOA 方位角（弧度制，$(-\pi, \pi]$） | 测向机测得的示向度（角度制，$[0^\circ, 360^\circ)$） | $\theta_k \in [0^\circ, 360^\circ)$ | B 题示向度以正东为 $0^\circ$ 逆时针旋转；原论文为标准笛卡尔坐标方位 |
| $n_i^\mathrm{A}(k)$ | 测向高斯白噪声，$n \sim \mathcal{N}(0, \sigma^2 \|\mathbf{d}\|^\gamma)$ | 有界全局示向误差 | $\varepsilon \in [-1^\circ, 1^\circ]$ | **本质差异**：原论文为高斯分布，B 题为严格确定性有界无先验分布区间 |
| $\|\mathbf{d}_i(k)\|$ | 无人机到目标的欧氏距离 | 检测点到干扰源的距离 | $r_k = \|\mathbf{p}_k - \mathbf{s}^*\|$ | B 题有效探测距离为 $r \le R_\mathrm{max} \in [1000, 1500]\text{ m}$；盲区 $r \le 5\text{ m}$ |
| $v$ | 无人机巡航速度（$30\text{ m/s}$） | 机器狗直线行进速度 | $v_\mathrm{dog} = 5\text{ m/s}$ | 无人机恒速直飞，机器狗具有移动与停靠双重状态 |
| $T$ | 航路点离散更新时间间隔（$10\text{ s}$） | 两检测点间移动时间 + 停靠检测耗时 | $t_\mathrm{move} + t_\mathrm{sense} = \frac{\|\mathbf{p}_2 - \mathbf{p}_1\|}{v_\mathrm{dog}} + 5\text{ s}$ | B 题移动与测量解耦，停靠测量固定耗时 $5\text{ s}$ |
| $\varphi$ | 无人机单步最大转弯偏角（$40^\circ$） | 机器狗转向能力 | 自由转向（可原地转弯或全向机动） | 机器狗在地面可视为无非完整转向约束，$\varphi$ 约束放宽为自由转角 |
| $\Phi(\mathbf{s})$ | Fisher 信息矩阵（FIM） | 交会凸多边形或置信区域信息度量 | 信息矩阵 $\mathbf{F}$ 或多边形面积/直径倒数 | 统计下界转换为有界几何交会区域的逆尺寸（$\mathrm{Area}(\mathcal{P})$ 或 $\mathrm{Diam}(\mathcal{P})$） |
| $A_{1\sigma}$ | $1\sigma$ 置信误差椭圆面积（$39.4\%$） | 两组示向线相交构成的四边形定位区域 | 凸四边形 $\mathcal{P}(\mathbf{p}_1, \theta_1, \mathbf{p}_2, \theta_2)$ 面积或直径 | 原文依赖高斯二阶矩，B 题依赖 $\pm 1^\circ$ 边界线求交多边形 |
| $\mathbf{c}_j, \kappa_j$ | 威胁物/禁飞区中心及安全隔离半径 | 目标区域边界或不可达障碍物 | 区域圆域边界 $x^2+y^2 \le 1800^2$ | 用于限制第二检测点 $\mathbf{p}_2$ 必须落在合法任务区域内部 |
| $\boldsymbol{\vartheta}^*(k)$ | 最优航向角（由非线性规划求解） | 第二检测点选址相对于当前点的位移向量/方位 | $\Delta \mathbf{p} = \mathbf{p}_2 - \mathbf{p}_1$ | B 题求解最优第二检测点 $\mathbf{p}_2^*$ 使综合代价最小 |

---

## E. 关键公式

### 公式 1：AOA 真实方位角与几何关系
- **论文编号**: (1)
- **章节定位**: Section II-A (正文 p. 1151–1152 / PDF pp. 002–003)
- **LaTeX 源码**:
  $$\theta_i(k) = \tan^{-1} \frac{\Delta y_i(k)}{\Delta x_i(k)}, \qquad -\pi < \theta_i(k) \le \pi$$
  其中 $\Delta y_i(k) = s_y - p_i^y(k), \Delta x_i(k) = s_x - p_i^x(k)$。
- **符号解释**: $\mathbf{s} = [s_x, s_y]^\top$ 为辐射源位置；$\mathbf{p}_i(k) = [p_i^x(k), p_i^y(k)]^\top$ 为观测站位置；$\tan^{-1}$ 表示四象限反正切。
- **中文物理含义**: 观测平台指向静止辐射源的真实视线角（Line-of-Sight, LOS）计算公式。
- **可否迁移到 B 题**: **可直接迁移**。与 B 题附录 2 示向度定义本质一致（B 题转为度数制与 $[0^\circ, 360^\circ)$ 区间）。

### 公式 2：测向加性高斯噪声模型
- **论文编号**: (2)
- **章节定位**: Section II-A (正文 p. 1152 / PDF p. 003)
- **LaTeX 源码**:
  $$\widehat{\theta}_i(k) = \theta_i(k) + n_i^\mathrm{A}(k), \qquad -\pi < \widehat{\theta}_i(k) \le \pi$$
- **符号解释**: $\widehat{\theta}_i(k)$ 为带噪观测角；$n_i^\mathrm{A}(k)$ 为零均值高斯白噪声。
- **中文物理含义**: 经典加性测向误差模型。
- **可否迁移到 B 题**: **需改写后迁移**。B 题为确定性硬界误差 $n \in [-1^\circ, 1^\circ]$，非无界高斯噪声。

### 公式 3：AOA 测向误差协方差矩阵（距离幂律衰减）
- **论文编号**: (11)
- **章节定位**: Section III-A (正文 p. 1153 / PDF p. 004)
- **LaTeX 源码**:
  $$\boldsymbol{\Sigma}_\mathrm{A} = \sigma_\mathrm{A}^2 \begin{bmatrix} \|\mathbf{d}_1^\mathrm{A}(\mathbf{s}_0)\|^\gamma & & \mathbf{0} \\ & \ddots & \\ \mathbf{0} & & \|\mathbf{d}_{N_\mathrm{A}}^\mathrm{A}(\mathbf{s}_0)\|^\gamma \end{bmatrix}$$
- **符号解释**: $\sigma_\mathrm{A}^2$ 为单位距离参考噪声方差；$\gamma \in [0, 2)$ 为路径损耗指数；$\mathbf{s}_0$ 为目标初始参考先验位置。
- **中文物理含义**: 描述信号场强随传播距离衰减对测向精度的物理影响，距离越远测向信噪比越低，方差越大。
- **可否迁移到 B 题**: **理论参考，不可照搬**。B 题明确指出测向误差在有效距离内全局处于 $[-1^\circ, 1^\circ]$，不随距离缩放；但该式揭示了“靠近目标可获得更好物理信噪比/较小横向位移发散”，对 Q2/Q3 靠近目标移动策略提供理论支撑。

### 公式 4：AOA 测向误差雅可比矩阵
- **论文编号**: (36a)
- **章节定位**: Section IV-C (正文 p. 1157 / PDF p. 008)
- **LaTeX 源码**:
  $$\mathbf{J}_\mathrm{A}(\mathbf{s}) = \frac{\partial \mathbf{e}_\mathrm{A}(\mathbf{s})}{\partial \mathbf{s}} = \begin{bmatrix} \frac{1}{\|\mathbf{d}_1^\mathrm{A}(\mathbf{s})\|} \left[ \sin \theta_1(\mathbf{s}), -\cos \theta_1(\mathbf{s}) \right] \\ \vdots \\ \frac{1}{\|\mathbf{d}_{N_\mathrm{A}}^\mathrm{A}(\mathbf{s})\|} \left[ \sin \theta_{N_\mathrm{A}}(\mathbf{s}), -\cos \theta_{N_\mathrm{A}}(\mathbf{s}) \right] \end{bmatrix}_{N_\mathrm{A} \times 2}$$
- **符号解释**: $\mathbf{e}_\mathrm{A}(\mathbf{s}) = \widehat{\boldsymbol{\theta}} - \boldsymbol{\theta}(\mathbf{s})$ 为测向残差；行向量垂直于第 $i$ 条视线方向。
- **中文物理含义**: 方位角变化对目标二维空间坐标的一阶敏感度矩阵。敏感度幅值与距离成反比（$1/d_i$），方向垂直于视线角（$[-\sin \theta_i, \cos \theta_i]$ 法向投影）。
- **可否迁移到 B 题**: **可直接迁移（作为敏感度与误差传播分析基准）**。其行列式直观推导出两测向线外积正比于 $\sin(\theta_2 - \theta_1)$，是证明交会角接近 $90^\circ$ 最优的解析根源。

### 公式 5：AOA 定位 Fisher 信息阵 (FIM)
- **论文编号**: (32) 中 AOA 单独项
- **章节定位**: Section IV-C (正文 p. 1157 / PDF p. 008)
- **LaTeX 源码**:
  $$\boldsymbol{\Phi}_\mathrm{A}(\mathbf{s}) = \mathbf{J}_\mathrm{A}^\top(\mathbf{s}) \boldsymbol{\Sigma}_\mathrm{A}^{-1}(\mathbf{s}) \mathbf{J}_\mathrm{A}(\mathbf{s}) = \sum_{i=1}^{N_\mathrm{A}} \frac{1}{\sigma_i^2 \|\mathbf{d}_i\|^2} \begin{bmatrix} \sin^2 \theta_i & -\sin \theta_i \cos \theta_i \\ -\sin \theta_i \cos \theta_i & \cos^2 \theta_i \end{bmatrix}$$
- **符号解释**: $\boldsymbol{\Phi}_\mathrm{A}(\mathbf{s})$ 为 $2 \times 2$ 信息矩阵；每个观测站贡献一个沿视线法向的外积投影秩 1 矩阵。
- **中文物理含义**: 观测几何对目标空间坐标约束能力的完全二阶统计度量。
- **可否迁移到 B 题**: **可直接迁移作为连续平滑目标准则**。当两站交会时，$|\boldsymbol{\Phi}| = \frac{\sin^2(\theta_2 - \theta_1)}{\sigma_1^2 \sigma_2^2 d_1^2 d_2^2}$，当且仅当交会角 $|\theta_2 - \theta_1| = 90^\circ$ 时信息量取极大值。

### 公式 6：不确定性误差椭圆面积与 D-最优准则
- **论文编号**: (24)
- **章节定位**: Section IV-B (正文 p. 1155 / PDF p. 006)
- **LaTeX 源码**:
  $$A_{1\sigma} = \frac{\pi}{|\boldsymbol{\Phi}(\mathbf{s})|^{1/2}}$$
- **符号解释**: $A_{1\sigma}$ 为一阶标准差误差椭圆面积（高斯二元分布下对应 $39.4\%$ 置信区间）；$|\boldsymbol{\Phi}(\mathbf{s})|$ 为 FIM 行列式。
- **中文物理含义**: 目标定位不确定性几何面积与 Fisher 信息阵行列式的平方根严格成反比。最大化 $|\boldsymbol{\Phi}|$ 等同于极小化定位置信椭圆面积（D-最优性）。
- **可否迁移到 B 题**: **方法迁移**。B 题追求极小化有界交会四边形面积/直径，该公式证明了“最大化两方向线张成的行列式/外积”能够协同极小化空间发散面积。

### 公式 7：滚动单步航路规划非线性目标函数
- **论文编号**: (25), (29a), (29b)
- **章节定位**: Section IV-B (正文 p. 1156 / PDF p. 007)
- **LaTeX 源码**:
  $$f(\boldsymbol{\vartheta}(k), \boldsymbol{\pi}(k), \mathbf{s}(k|k)) = \frac{1}{|\boldsymbol{\Phi}(\boldsymbol{\pi}(k+1), \mathbf{s}(k|k))|}$$
  $$\boldsymbol{\vartheta}^*(k) = \arg\min_{-\pi < \vartheta_i(k) \le \pi} f(\boldsymbol{\vartheta}(k), \boldsymbol{\pi}(k), \mathbf{s}(k|k))$$
  $$\mathbf{u}_i(k) = vT \begin{bmatrix} \cos \vartheta_i^*(k) \\ \sin \vartheta_i^*(k) \end{bmatrix}$$
- **符号解释**: $\mathbf{s}(k|k)$ 为当前时刻后验滤波目标估计；$\boldsymbol{\pi}(k+1)$ 为候选下一步位置向量；$\boldsymbol{\vartheta}^*(k)$ 为最优航向角度。
- **中文物理含义**: 在当前目标先验分布下，寻找使下一步联合观测 FIM 行列式最大的航向角矢量，以恒定单步步长推进航路点。
- **可否迁移到 B 题**: **核心方法迁移**。构成了 Q2 选择第二点及 Q3/Q4 机器狗滚动选择观测点的基本范式（将目标函数替换为几何多边形最坏指标+时间代价）。

### 公式 8：内点对数障碍函数 (Logarithmic Barrier Function)
- **论文编号**: (45), (46)
- **章节定位**: Section V (正文 p. 1158 / PDF p. 009)
- **LaTeX 源码**:
  $$c(\boldsymbol{\vartheta}(k)) = -\sum_{i=1}^{N-1} \sum_{j=i+1}^N \ln(-g_{1ij}(\boldsymbol{\vartheta}(k))) - \sum_{i=1}^N \sum_{j=1}^M \ln(-g_{2ij}(\boldsymbol{\vartheta}(k)))$$
  $$\boldsymbol{\vartheta}^*(k, \mu) = \arg\min_{\boldsymbol{\vartheta}(k) \in \mathcal{T}(k)} \left[ f(\boldsymbol{\vartheta}(k), \boldsymbol{\pi}(k), \mathbf{s}(k|k)) + \mu c(\boldsymbol{\vartheta}(k)) \right]$$
- **符号解释**: $g_{1ij} \le 0$ 为机间连通距离约束；$g_{2ij} \le 0$ 为禁飞区避障约束；$\mu > 0$ 为极小惩罚参数；$\mathcal{T}(k)$ 为可行内部集。
- **中文物理含义**: 将带复杂非线性几何不等式约束的优化问题转化为参数化无约束优化问题，当轨迹接近约束边界时惩罚急剧趋于无穷，实现光滑避障。
- **可否迁移到 B 题**: **可直接迁移**。机器狗在目标区域内移动需保证不越过 $1800\text{ m}$ 圆形边界及其他障碍物，可用该障碍函数构造连续可微的候选点评分器。

### 公式 9：转向率受限下的等效安全裕度膨胀公式
- **论文编号**: (48a), (49), (50)
- **章节定位**: Section V (正文 p. 1158–1159 / PDF pp. 009–010)
- **LaTeX 源码**:
  $$r = \frac{vT}{\sin \varphi} \sqrt{\frac{1}{2}(1 + \cos \varphi)}$$
  $$\hat{\kappa}_j = \|\mathbf{q} - \mathbf{c}_j\| - r = \sqrt{\left(\frac{vT}{2} + \kappa_j\right)^2 + \frac{(vT)^2}{4 \sin^2 \varphi}(1+\cos \varphi)^2} - \frac{vT}{\sin \varphi}\sqrt{\frac{1}{2}(1+\cos \varphi)}$$
- **符号解释**: $r$ 为由相邻 3 航路点决定的极限外接圆转弯半径；$\varphi$ 为最大转弯角；$\kappa_j$ 为算法名义隔离半径；$\hat{\kappa}_j \le \kappa_j$ 为动力学受限下的实际最差穿透清除距离。
- **中文物理含义**: 证明当平台存在转弯角速度上限时，为了绝对避开半径为 $\hat{\kappa}_j$ 的危险圆，算法必须在优化时将名义避障半径主动放大为 $\kappa_j$（保守设计）。
- **可否迁移到 B 题**: **方法迁移**。为 B 题中若考虑机器狗减速转弯、刹车距离或近场 $5\text{ m}$ 盲区规避时，提供了严格的“几何裕度膨胀（Conservative Buffer）”量化推导方法。

---

## F. 算法与证明

### 1. 算法流程：基于内点优化的 UAV 协同导引算法 (Table I)
- **输入**:
  - 当前时刻无人机站位坐标 $\mathbf{p}_1(k), \ldots, \mathbf{p}_N(k)$；
  - 几何与动力学参数：通信半径 $\rho$、威胁集 $\{\mathbf{c}_j, \kappa_j\}$、转弯角上限 $\varphi$、巡航速度 $v$、周期 $T$；
  - 测向传感器观测向量 $\widehat{\boldsymbol{\theta}}(k)$。
- **步骤**:
  1. **状态更新**:
     - 利用当前观测 $\widehat{\boldsymbol{\theta}}(k)$ 求解非线性最小二乘极大似然估计 $\hat{\mathbf{s}}(k) = \arg\min J_\mathrm{MLE}(\mathbf{s})$；
     - 结合先验估计执行卡尔曼滤波时间与测量更新，得到滤波状态 $\mathbf{s}(k|k)$ 与估计协方差 $\mathbf{P}(k|k)$。
  2. **构造预测性能目标**:
     - 以 $\mathbf{s}(k|k)$ 替代未知真实目标位置，代入下一时刻预测 FIM：$\boldsymbol{\Phi}(\boldsymbol{\pi}(k+1), \mathbf{s}(k|k))$；
     - 目标函数设为 $f(\boldsymbol{\vartheta}(k)) = 1 / |\boldsymbol{\Phi}|$。
  3. **初值启发式搜索 (Initialization)**:
     - 方案一（指向目标）：$\vartheta_i = \angle(\mathbf{s}(k|k) - \mathbf{p}_i(k))$；
     - 方案二（梯度上升）：沿信息量关于当前位置的梯度方向 $\boldsymbol{\xi}_i = \frac{\partial |\boldsymbol{\Phi}|}{\partial \mathbf{p}_i(k)}$，置 $\vartheta_i = \angle \boldsymbol{\xi}_i$；
     - 针对违反不等式约束的初值，采用 $K=32$ 个离散等间隔方位角进行局部轻量网格搜索，确保落在可行域内 $\boldsymbol{\vartheta} \in \mathcal{T}(k)$。
  4. **求解参数化无约束优化**:
     - 固定极小障碍因子 $\mu = 10^{-10}$，利用 Nelder-Mead 单纯形法或高斯-牛顿法求解无约束极小化：$\min_{\boldsymbol{\vartheta}} [f(\boldsymbol{\vartheta}) + \mu c(\boldsymbol{\vartheta})]$，输出最优角度 $\boldsymbol{\vartheta}^*(k)$。
  5. **执行运动学转角硬限幅**:
     - 检验 $|\vartheta_i^*(k) - \vartheta_i(k-1)|$；若超过 $\varphi$，则强制截断为偏差等于 $\varphi$ 的方向（优先保证动力学生存）。
  6. **航路点生成与执行**:
     - 计算控制矢量 $\mathbf{u}_i(k) = vT [\cos \vartheta_i^*(k), \sin \vartheta_i^*(k)]^\top$，无人机飞行至 $\mathbf{p}_i(k+1) = \mathbf{p}_i(k) + \mathbf{u}_i(k)$。
- **输出**: 下一时刻全局航路点 $\mathbf{p}_i(k+1)$。
- **停止条件**: 无人机到达辐射源附近或滤波 MSE 低于预设阈值 $\epsilon$。
- **计算复杂度**: 
  - 单步 FIM 评价为 $\mathcal{O}(N)$；
  - 优化求解器收敛通常在 10–30 次迭代内完成；
  - 相比全局多步动态规划 $\mathcal{O}(K^{H \cdot N})$，单步滚动时域复杂度仅为 $\mathcal{O}(N \cdot I_\mathrm{iter})$，满足在线实时计算要求。

### 2. 核心定理与关键结论推导
- **[结论 1] 最优角分离定理（文献引用与支撑）**:
  - 原文引述 Dogancay & Hmam (2008) 证明：当两测向站与辐射源等距时，使 FIM 行列式最大的最优交会角为 $|\theta_1 - \theta_2| = 90^\circ$；当三测向站等距时，最优角分离为 $60^\circ$ 或 $120^\circ$（正文 p. 1160 / PDF p. 011）。
  - *推导证据*：两站 AOA 时，行列式 $|\boldsymbol{\Phi}| \propto \frac{\sin^2(\theta_1 - \theta_2)}{d_1^2 d_2^2}$，正交交会从根本上消除了视线方向交叉时的共线性奇异。
- **[结论 2] 转向限制对障碍清除距离的侵蚀效应**:
  - 原文严格推导公式 (48)–(49)：无人机在最大角速度下沿切线转弯时，由于离散控制步长 $vT$ 与最大角速度 $\varphi$ 限制，实际飞行轨迹构成的外接圆会向禁飞区内部“深切”穿透，造成有效避障距离从名义 $\kappa_j$ 缩水至 $\hat{\kappa}_j$（正文 p. 1158–1159 / PDF pp. 009–010）。
  - *适用条件*：离散控制周期 $T$ 越大或转弯率 $\varphi$ 越小，内切穿透越严重。

---

## G. 实验与可比指标

### 1. 仿真场景与基线设置
- **辐射源位置**: $\mathbf{s} = [10000, 3000]^\top\text{ m}$，扫描周期角速度 $\omega = \pi\text{ rad/s}$（Sec. VI, 正文 p. 1159 / PDF p. 010）。
- **无人机配置**: 3 架平台 ($N=3$)，初始位置 $\mathbf{p}_1(0) = [1000, 1000]^\top$, $\mathbf{p}_2(0) = [2000, 0]^\top$, $\mathbf{p}_3(0) = [1000, -1000]^\top\text{ m}$。
- **运动与传感器参数**: 速度 $v = 30\text{ m/s}$，时间间隔 $T = 10\text{ s}$（单步步长 $300\text{ m}$），转弯限幅 $\varphi = 40^\circ$（即 $4^\circ/\text{s}$）。测向误差基准标准差 $\sigma_\mathrm{A} = 0.005^\circ$（转写原文值），衰减指数真实值 $\gamma=0.8$，算法设 $\gamma_a = 2$。
- **对比基线 (Baseline)**: 直线基线策略（Straight-line paths，各无人机无视 FIM 几何，始终沿朝向目标估计位置的最短直线飞行）。
- **评估指标**: 目标定位均方误差 $\mathrm{MSE} = \mathrm{tr}(\mathbf{P}(k|k))$ 随时间步 $k$ 的收敛演变曲线。

### 2. 核心数值实验结论
- **AOA 纯测向实验 (Fig. 5, 正文 p. 1160 / PDF p. 011)**:
  - 最优路径策略下，3 架无人机迅速自主展开基线，形成约 $60^\circ$ 的等角分离包围构型；
  - MSE 收敛速度显著高于直飞基线（在 $k=15$ 步后，最优规划航路的定位协方差迹比直飞策略低 1 到 2 个数量级）；直飞策略由于基线夹角收缩过快，在逼近目标时几何交会奇异性加剧。
- **硬约束避障实验 (Fig. 10 & 11, 正文 p. 1162–1164 / PDF pp. 013–015)**:
  - 在两个威胁禁飞区 $\mathbf{c}_1 = [4000, 4000]^\top$ ($\kappa_1 = 1000\text{ m}$) 和 $\mathbf{c}_2 = [8000, -500]^\top$ ($\kappa_2 = 1200\text{ m}$) 存在时，无人机在保持规避圆柱边界的同时顺利通过，轨迹平滑贴合约束边缘；
  - 当转弯率人为限制在较小的 $\varphi = 30^\circ$ 时，实测最小安全距离准确逼近由公式 (49) 计算所得的理论侵蚀极限 $\hat{\kappa}_1 = 0.7\text{ km}$（原设 $\kappa_1 = 1.0\text{ km}$）。
- **风场扰动鲁棒性实验 (Fig. 13, 正文 p. 1164–1165 / PDF pp. 015–016)**:
  - 施加 Davenport 离散滤波风扰（风向东南 $\pm 10^\circ$，风速均值 100，阵风方差 250），航路点实际发生位置偏移；但由于每步重规划以当前实际 GPS 定位为基准，系统未产生累积漂移误差，MSE 依然保持收敛。

---

## H. 可直接用于建模论文的证据卡

### 证据卡 1：D-最优设计准则作为定位面积的代理指标
- **结论转述**: 极大似然估计的置信误差椭圆面积与 Fisher 信息阵行列式的平方根成严格反比；最大化 FIM 行列式等价于极小化多向测向交会的不确定性区域面积。
- **定位**: Section IV-B, 正文 p. 1155 / PDF p. 006, 公式 (24)。
- **论文推荐章节**: B 题问题 2“第二检测点优选准则设计” / 理论基础对比段。
- **适用条件**: 测量误差为小误差高斯白噪声或渐近有效无偏估计；在有界误差下，可作为连续平滑的凸优化代理目标。

### 证据卡 2：滚动时域单步前瞻决策架构 (Receding Horizon Look-Ahead)
- **结论转述**: 在未知目标定位中，无需事先规划全程轨迹，通过“当前估计 $\rightarrow$ 预测下一站位 FIM $\rightarrow$ 局部最优航向求解 $\rightarrow$ 步进执行”的闭环迭代，可在极低算力开销下实现全局渐近最优逼近。
- **定位**: Section IV-B, 正文 p. 1156 / PDF p. 007, 图 3 与公式 (25)–(29)。
- **论文推荐章节**: B 题问题 2 算法设计 / 问题 3 机器狗多步在线搜索规划。
- **适用条件**: 每次观测后能够获得目标的可行域或后验质心估计，步长与探测范围适配。

### 证据卡 3：两测向站的最佳正交交会几何与角分离特性
- **结论转述**: 当由两处站位对目标进行纯方位角交叉定位时，信息量行列式在两视线夹角呈 $90^\circ$ 垂直正交时达到全局极大值；若为三站等距则为 $60^\circ$ 或 $120^\circ$。
- **定位**: Section VI-A, 正文 p. 1160 / PDF p. 011, 引用文 [27]。
- **论文推荐章节**: B 题问题 2“候选区域生成几何约束推导” / 直观几何验证。
- **适用条件**: 假设两站位到目标距离相近，且测向误差关于方位各向同性。

### 证据卡 4：非完整机动约束下的安全边界保守设计法
- **结论转述**: 当移动平台具有最大转向角/转弯曲率限制时，实际机动会产生内切深穿现象；为保证对障碍物/危险区（或近场盲区）的绝对物理隔离，规划层的名义安全边界必须依据最大转弯率按解析几何公式予以膨胀放大。
- **定位**: Section V, 正文 p. 1158–1159 / PDF pp. 009–010, 公式 (48)–(50) 及图 4。
- **论文推荐章节**: B 题问题 2/3“机器狗近场盲区（5m）规避与任务边界安全约束”。
- **适用条件**: 平台具有离散采样步长与曲率转向限制。

---

## I. 不能照搬的部分与改写指南

### 1. 差异对比矩阵

| 维度 | 论文原生设定 (Dogancay 2012) | 2026 数模 B 题实情 (Problem B) | 迁移风险与阻断原因 |
|:---|:---|:---|:---|
| **噪声本质** | 零均值无界高斯白噪声，$n \sim \mathcal{N}(0, \sigma^2)$ | 严格确定性有界误差，$\varepsilon \in [-1^\circ, 1^\circ]$ | 若直接使用高斯似然函数，会丢失最坏情况保证，导致多边形顶点漏判 |
| **距离依赖** | 噪声方差随距离呈幂律衰减 $\sigma^2 \|\mathbf{d}\|^\gamma$ | 在有效范围 $[0, 1500]\text{ m}$ 内全局恒定 $\pm 1^\circ$ | 论文中“距离越近方差越小”直接影响权值，B 题中距离仅通过几何横向放大影响跨度 |
| **先验状态** | 假设已有目标单点先验估计 $\mathbf{s}_0$ 或多机瞬间 MLE | 第一次检测后目标仅被约束在一条射线夹角为 $2^\circ$ 的无限/长楔形内 | **Q2 第一步无单点目标估计**，无法直接将目标固定为单点 $\mathbf{s}(k|k)$ 计算 FIM |
| **运动形态** | 空中无人机连续匀速飞行，转弯受非完整向心力限制 | 地面机器狗走走停停（直线 $5\text{ m/s}$，停靠 $5\text{ s}$，频道切换 $1\text{ s}$） | 无人机无停靠成本，B 题每增设一个采样点都背负固定时间惩罚 |
| **传感器配置**| 异构多机协同（AOA + TDOA + Scan） | 单一机器狗搭载单信道测向机，时序移动交会 | 论文为空间分布式并发测量，B 题为时间换空间的序贯单站测量 |
| **优化准则** | 局部统计最优（极大化 Fisher 信息量） | 最坏情况几何极小化（Minimax 直径/外接圆半径）+ 时间代价 | 纯信息增益忽略移动时间开销，易导致机器狗为追求微小精度而长途奔袭 |

### 2. 手册级改写指南（面向 B 题 Q2 的定制化改造）

#### 改写步骤 1：目标函数由“高斯 FIM”重塑为“几何最坏情况 (Worst-Case) + 时间代价”
- **原论文目标**: $\min_{\boldsymbol{\vartheta}} \frac{1}{|\boldsymbol{\Phi}(\mathbf{p}(k+1), \mathbf{s})|}$。
- **B 题改写**:
  设定综合代价评分函数（Pareto 加权或约束最优化）：
  $$\min_{\mathbf{p}_2} \mathcal{J}(\mathbf{p}_2) = \underbrace{w_1 \cdot \frac{t_\mathrm{move}(\mathbf{p}_1, \mathbf{p}_2) + t_\mathrm{sense}}{T_\mathrm{norm}}}_{\text{时间代价}} + \underbrace{w_2 \cdot \frac{\max_{\mathbf{s} \in \mathcal{W}_1} \mathrm{Diam}\left(\mathcal{P}(\mathbf{p}_1, \theta_1, \mathbf{p}_2, \mathbf{s})\right)}{D_\mathrm{norm}}}_{\text{最坏交会多边形几何直径}}$$
  其中 $t_\mathrm{move} = \frac{\|\mathbf{p}_2 - \mathbf{p}_1\|}{5\text{ m/s}}$，$t_\mathrm{sense} = 5\text{ s}$；$\mathcal{W}_1$ 为第一次测量给出的 $2^\circ$ 示向角楔形区域（截断于有效距离 $1500\text{ m}$ 与目标圆域边界）。

#### 改写步骤 2：破解“无单点先验”瓶颈——基于支撑线段的 Minimax 积分
- 论文在计算信息量时直接代入滤波点估计 $\mathbf{s}(k|k)$。但在 Q2 初始状态下，仅有单个测向角 $\theta_1$，目标在视线方向的距离 $r \in [5, 1500]\text{ m}$ 完全未知。
- **改写方案**：沿首次测向中心视线离散化采样 $M$ 个潜在目标点 $\mathbf{s}^{(m)} = \mathbf{p}_1 + r_m [\cos \theta_1, \sin \theta_1]^\top$（例如 $r_m \in \{100, 300, 600, 1000, 1500\}\text{ m}$）。对候选第二点 $\mathbf{p}_2$，分别计算各采样点的交会四边形直径，取其上确界（Supremum）作为保守估计：
  $$\mathrm{Uncertainty}(\mathbf{p}_2) = \max_{m} \mathrm{Diam}\left( \mathcal{P}(\mathbf{p}_1, \mathbf{p}_2, \mathbf{s}^{(m)}) \right)$$

#### 改写步骤 3：第二检测点候选区域（Candidate Region）的几何解析刻画
- 借鉴论文中关于“两站 $90^\circ$ 正交最优”的拓扑定理，B 题第二检测点 $\mathbf{p}_2$ 的搜索方向应严格避开与第一条射线共线（若两检测点与目标共线，交会角为 $0^\circ$ 或 $180^\circ$，多边形发散至无穷大）。
- **候选区域判定规则**:
  1. **正交张角带**: $\mathbf{p}_2$ 应分布在第一测向射线两侧、视线交会角满足 $\beta \in [60^\circ, 120^\circ]$ 的环形扇区内；
  2. **位移步长折中区**: 距离 $\mathbf{p}_1$ 不宜过小（过小则基线太短，角误差放大导致四边形极长），亦不宜过大（移动时间过长，且可能超出干扰源 $1500\text{ m}$ 有效接收范围）；
  3. **区域边界约束**: $\mathbf{p}_2$ 必须严格位于半径 $1800\text{ m}$ 的任务圆域内（即 $\|\mathbf{p}_2\| \le 1800$）。

---

## J. 一页结论

### 1. 最值得保留的 3 点技术遗产
1. **闭环滚动决策架构**: 摒弃开环静态规划，将测向定位解构为“当前估计 $\rightarrow$ 预测候选点收益 $\rightarrow$ 步进移动测量”的在线闭环，天然兼容动态未知环境。
2. **正交交会信息增益极值性**: 证明了两测向站视线夹角呈 $90^\circ$ 时信息量行列式取极大值，为 B 题第二检测点在第一条示向线法向两侧优选提供了坚实的理论依据。
3. **环境约束的内点平滑惩罚与机动补偿**: 利用对数障碍函数处理区域边界与禁飞避障，并针对转弯/盲区进行前瞻几何裕度膨胀，保证了算法在复杂约束下的数值稳健性。

### 2. 最关键的 2 个公式
- **FIM 行列式与正交分离解析解**:
  $$|\boldsymbol{\Phi}_\mathrm{A}(\mathbf{s})| = \frac{\sin^2(\theta_2 - \theta_1)}{\sigma_1^2 \sigma_2^2 \|\mathbf{d}_1\|^2 \|\mathbf{d}_2\|^2}$$
  *(直观指示：交会角差值取 $90^\circ$ 且测向距离越近，定位确定性越高)*
- **滚动预测单步决策机制**:
  $$\mathbf{p}^*(k+1) = \arg\max_{\mathbf{p} \in \Omega_\mathrm{feas}} \left[ \mathrm{Gain}(\mathbf{p}, \mathbf{s}(k|k)) - \lambda \cdot \mathrm{Cost}(\mathbf{p}(k), \mathbf{p}) \right]$$
  *(直观指示：信息收益与移动能耗/时间代价的 Pareto 权衡方程)*

### 3. 对 B 题最直接的一个落地动作
- **构建 Q2 第二检测点“法向偏移+距离扫描”候选集生成算法**:
  在获取第 1 检测点 $\mathbf{p}_1$ 与示向度 $\theta_1$ 后，机器狗不盲目全图网格搜索，而是以 $\mathbf{p}_1$ 为基点，沿垂直于示向度的法向方向（$\theta_1 \pm 90^\circ$）向外延伸基线步长 $L \in [300, 800]\text{ m}$，在此法向主轴两侧按扇形扰动形成候选点集合 $\Omega_{\mathbf{p}_2}$；随后在该集合上评估“最坏多边形直径 + 移动耗时”双指标，直接输出最优第二检测点坐标及候选几何连通域。
