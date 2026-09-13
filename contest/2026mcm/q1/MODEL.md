# B 题 Q1 数学模型

> 本文件给出 Q1 经问题理解、独立建模和文献核验后确认的数学系统。题意裁决见 RESEARCH.md；具体求解算法、数值实现与验证见后续 METHOD.md。

## 1. 模型摘要与正式任务

Q1 建立的是确定性有界测向误差下的集合定位与几何判定模型。若干个有效示向度分别产生前向测向角域，其交集形成定位凸多边形；模型进一步计算该区域的直径和最远点对，并判断以该点对为直径构造的闭圆盘能否覆盖整个定位区域。

唯一主线为

$$
\{(\mathbf p_i,\hat\theta_i)\}_{i=1}^{n}
\longrightarrow
\mathcal R
\longrightarrow
(D,\mathbf a^*,\mathbf b^*)
\longrightarrow
\kappa.
$$

| 题面任务 | 模型对象 | 正式输出 |
|---|---|---|
| 交会定位 | 全部前向测向角域的交集 | 定位多边形 $\mathcal R$ 或其顶点集 $\mathcal V$ |
| 计算区域直径 | 连续区域上的最大点间距离 | $D$ 及最远点对 $(\mathbf a^*,\mathbf b^*)$ |
| 判断圆能否覆盖 | 直径点对确定的闭圆盘与集合包含关系 | $\kappa\in\{0,1\}$ |

## 2. 继承语义、对象与参数

定位对象是一个干扰源，观测来自 $n$ 个已知检测点。示向度从 $x$ 轴正向逆时针量取，全部示向度已经按同一频道正确对应，且均为题设有效观测。

测向误差半宽为

$$
\varepsilon=1^\circ=\frac{\pi}{180}.
$$

题面和数据接口使用角度制，数学系统内部统一使用弧度制；误差区间包含边界，全部角度按 $2\pi$ 周期处理。

有效接收半径、近场规则以及全向或定向覆盖决定某个示向度能否产生，属于题设有效输入的前置条件。Q1 已以有效示向度为输入，因此模型从观测成功之后开始，不再反推无示向原因，也不把这些观测可得性条件加入定位区域。半径为 $1800\text{ m}$ 的目标圆域属于全题场景边界，同样不裁剪附录 2 指定的交会定位多边形。

## 3. 对象、未知量、决策变量、状态与表示

模型中的量及其角色为：

- $n,\mathbf p_i=(x_i,y_i)^T,\hat\theta_i$：检测点数量、坐标和实测示向度，是给定输入；
- $\varepsilon$：固定的测向误差半宽；
- $\mathbf s=(s_x,s_y)^T$：现实中唯一但未知的真实干扰源位置；
- $\mathbf x$：遍历全部候选源位置的集合变量；
- $\mathcal W_i$：第 $i$ 次观测产生的前向测向角域；
- $\mathcal R$ 与 $\mathcal V$：联合定位多边形及其顶点集；
- $D,\mathbf a^*,\mathbf b^*,\kappa$：区域直径、直径点对和覆盖结论。

Q1 没有可控决策变量。实际误差 $e_i$ 只用于解释观测生成，随后被等价消去为角域约束，不作为独立状态保存。

## 4. 核心关系、命题与推导

### 4.1 有界示向观测

第 $i$ 次观测满足

$$
\hat\theta_i
=
\arg(\mathbf s-\mathbf p_i)+e_i
\pmod{2\pi},
\qquad
|e_i|\le\varepsilon.
$$

$e_i$ 是未知但确定性有界的误差，不预设概率分布。同一地点重复检测时误差不变，因此重复读数不产生独立的误差收缩信息。

### 4.2 前向测向角域

定义第 $i$ 次观测的两条边界方向单位向量

$$
\mathbf u_i^\pm=
\begin{bmatrix}
\cos(\hat\theta_i\pm\varepsilon)\\
\sin(\hat\theta_i\pm\varepsilon)
\end{bmatrix}.
$$

对二维向量定义标量叉积 $\mathbf a\times\mathbf b=a_xb_y-a_yb_x$，则该次观测允许的闭合前向角域为

$$
\mathcal W_i=
\left\{
\mathbf x:
\mathbf u_i^-\times(\mathbf x-\mathbf p_i)\ge0,\quad
(\mathbf x-\mathbf p_i)\times\mathbf u_i^+\ge0
\right\}.
$$

这一表示同时保留前向性、含边界的测向误差和全周向周期性，并避免斜率表示的奇异性。

### 4.3 联合定位多边形

所有同源观测必须同时成立，因此

$$
\mathcal R=\bigcap_{i=1}^{n}\mathcal W_i.
$$

此后 $\mathcal R$ 专指由测向误差角域形成的角度交会区域，即 $\mathcal R=\mathcal R_{\mathrm{angle}}$，不包含接收距离、近场排除或目标圆域约束。

在正常输入条件下，$\mathcal R$ 是非空、有界且具有非零面积的凸多边形。记其全部顶点为 $\mathcal V$，则

$$
\mathcal R=\operatorname{conv}(\mathcal V),
\qquad
\mathbf s\in\mathcal R.
$$

附录中由两个检测点形成四边形只是该定义的一个特例；检测点数量增加时仍使用同一交集定义，冗余角域或半平面不会改变定位区域。

### 4.4 区域直径及顶点化

定位区域直径定义为

$$
D=
\max_{\mathbf x,\mathbf y\in\mathcal R}
\|\mathbf x-\mathbf y\|_2.
$$

该连续区域上的最大值可以严格归结为顶点对：

$$
D=
\max_{\mathbf v_j,\mathbf v_k\in\mathcal V}
\|\mathbf v_j-\mathbf v_k\|_2.
$$

证明如下。任取

$$
\mathbf x=\sum_j\lambda_j\mathbf v_j,
\qquad
\mathbf y=\sum_k\mu_k\mathbf v_k,
$$

其中 $\lambda_j,\mu_k\ge0$ 且各自之和为 $1$，由三角不等式有

$$
\|\mathbf x-\mathbf y\|_2
\le
\sum_{j,k}\lambda_j\mu_k
\|\mathbf v_j-\mathbf v_k\|_2
\le
\max_{j,k}\|\mathbf v_j-\mathbf v_k\|_2.
$$

而顶点本身属于 $\mathcal R$，故上式给出的上界能够由某一顶点对实现。取一组直径见证

$$
(\mathbf a^*,\mathbf b^*)
\in
\operatorname*{arg\,max}_{\mathbf v_j,\mathbf v_k\in\mathcal V}
\|\mathbf v_j-\mathbf v_k\|_2.
$$

### 4.5 直径圆盘与覆盖判据

以该直径点对为端点，定义圆心和闭圆盘

$$
\mathbf c^*=\frac{\mathbf a^*+\mathbf b^*}{2},
\qquad
\mathcal C^*=
\left\{
\mathbf x:
\|\mathbf x-\mathbf c^*\|_2\le\frac D2
\right\}.
$$

由恒等式

$$
(\mathbf x-\mathbf a^*)\cdot(\mathbf x-\mathbf b^*)
=
\|\mathbf x-\mathbf c^*\|_2^2-\frac{D^2}{4},
$$

可得点的圆盘归属判据。进一步利用 $\mathcal R=\operatorname{conv}(\mathcal V)$ 和闭圆盘的凸性，

$$
\mathcal R\subseteq\mathcal C^*
\iff
(\mathbf v-\mathbf a^*)\cdot(\mathbf v-\mathbf b^*)\le0,
\quad
\forall\mathbf v\in\mathcal V.
$$

该顶点判据是充分必要的：若整个区域被覆盖，其顶点必被覆盖；反之，若所有顶点均位于圆盘内，则对任意 $\mathbf x=\sum_j\lambda_j\mathbf v_j\in\mathcal R$，

$$
\|\mathbf x-\mathbf c^*\|_2
\le
\sum_j\lambda_j\|\mathbf v_j-\mathbf c^*\|_2
\le
\frac D2,
$$

故整个定位区域均被覆盖。

多组直径点对也不会造成覆盖结论不一致。若某一直径圆盘已经覆盖 $\mathcal R$，另一组直径点对 $(\mathbf a',\mathbf b')$ 的两个端点均在该半径为 $D/2$ 的圆盘内，且二者相距 $D$，于是

$$
D=\|\mathbf a'-\mathbf b'\|_2
\le
\|\mathbf a'-\mathbf c^*\|_2+
\|\mathbf b'-\mathbf c^*\|_2
\le D.
$$

三角不等式必须处处取等号，因此两点均在圆周上并关于 $\mathbf c^*$ 反向共线，即它们也是同一圆盘的对径点。故若一组直径点对能够覆盖，则所有直径点对构造的圆盘相同；反之，任一组不覆盖时也不存在另一组能够覆盖。

## 5. 正式目标、判定命题与评价量

定义覆盖输出

$$
\kappa=
\begin{cases}
1,&\mathcal R\subseteq\mathcal C^*,\\
0,&\text{否则}.
\end{cases}
$$

Q1 的正式输出为

$$
\boxed{
\mathcal V,\quad
D,\quad
(\mathbf a^*,\mathbf b^*),\quad
\mathbf c^*,\quad
\kappa
}.
$$

直径圆盘只能直接保证包含实现直径的两个端点，不能由直径数值 $D$ 单独保证覆盖整个定位多边形；覆盖性取决于区域的整体形状，必须执行上述集合判定。例如，边长为 $D$ 的等边三角形以任一边为直径时，第三个顶点均位于对应的直径圆盘之外，因此一般不能保证覆盖。

## 6. 约束、可行域、简化与假设

### 6.1 题设输入条件与模型假设

1. 干扰源在全部观测期间静止，检测点坐标和全局方向基准准确。
2. 题目给出的全部示向度属于同一干扰源，已经按频道正确对应且均满足有效观测条件；无示向或观测不可得不属于 Q1 的输入。
3. 测向误差是包含边界的确定性有界扰动，不引入概率分布。
4. 不同地点的实际误差可以不同；同一地点重复检测时误差不变。
5. 交会区域 $\mathcal R$ 非空、有界且具有非零面积。

### 6.2 关键模型裁决

| 议题 | 当前处理 | 决定性理由 | 恢复条件 |
|---|---|---|---|
| 有效接收、近场与方向覆盖 | 作为题设有效输入的前置条件，不裁剪 $\mathcal R$ | 它们决定示向度能否产生；Q1 从成功观测开始，要求的是角度交会多边形 | 后续研究观测获取、无示向反馈或定向源搜索 |
| 目标圆域 | 不裁剪 $\mathcal R$ | 它是全题场景边界，不是附录 2 交会定位多边形的组成部分 | 后续搜索和行动决策 |
| 误差变量 | 消去为角域约束 | 与确定性区间误差严格等价 | 获得误差概率分布或相关性证据 |
| 多源关联 | 不建模 | 频道已经区分同源观测 | 后续输入未按频道归属或需要跨源关联 |
| 代表点与概率估计 | 不使用 | Q1 要求完整的确定性定位区域 | 后续行动阶段可另设操作点 |
| 最小包围圆 | 不作为主对象 | 题目指定的是以区域直径为直径的圆 | 研究单点保证清除时 |

必须特别区分两个量词：有效观测意味着实际真实源满足相应的观测产生条件，其中包括到检测点的距离不超过实际有效接收半径、因而不超过 $1500\text{ m}$；但 $\mathcal R$ 中的点只是满足全部角度误差约束的候选位置，并不因此逐点继承上述距离条件。因此，本问不应据此用 $1500\text{ m}$ 接收圆盘裁剪 $\mathcal R$。

## 7. 数学结构、输出与边界

本模型是二维、静态、确定性、集合值的几何模型。单次测向可行集由线性不等式表示，联合定位区域是凸多边形；连续区域的直径和圆盘覆盖判定都可以严格归结到有限顶点集，而不丢失定位区域的信息。

下一阶段只需分别实现以下三个数学接口：

$$
\{(\mathbf p_i,\hat\theta_i)\}_{i=1}^{n}
\longmapsto
\mathcal V,
$$

$$
\mathcal V
\longmapsto
(D,\mathbf a^*,\mathbf b^*),
$$

$$
(\mathcal V,\mathbf a^*,\mathbf b^*)
\longmapsto
\kappa.
$$

本文件不指定这些接口的具体求解算法。

无效、异源或无示向观测位于 Q1 的输入域之外；对已经给出的角度约束，交集为空、无界或退化为低维集合属于方法端需要识别的几何状态，而不是接收距离异常的替代解释。若后续任务要求联合研究观测可得性、目标区域和搜索范围，应在相应阶段另建外层模型，不改变本问 $\mathcal R$ 的定义。

Q2—Q4 可以继承“有效示向度—前向角域—同源交集”的定位语义，但观测获取、搜索、移动、定向覆盖和清除决策须在各自阶段另行建模。
