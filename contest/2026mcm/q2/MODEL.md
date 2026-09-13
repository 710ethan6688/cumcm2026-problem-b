# B题 Q2 数学模型

> 本文件定义第一次获得有效示向度后，如何在保守接收安全区域内选择第二检测点。主目标是最小化反馈后的最坏位置域直径；完整曲线、覆盖比例和联合状态安全认证保留为离线增强验证。问题理解见 RESEARCH.md；稀疏搜索、局部二次求解和验证方案见 METHOD.md。

## 1. 模型摘要与正式任务

Q2 建立一个带有有界测向误差和未知接收半径的静态集合决策模型。输入为第一检测点、第一次实测示向度及题面常数，决策变量为第二检测点。模型保留 near、direction、no_signal 三类结果，不给源位置、接收半径或测向误差人为指定概率分布。

主模型先以题面给出的最小接收半径构造一个充分但可能偏保守的安全候选区域。在该区域内，存活的全向源必然返回 `direction` 或 `near`；模型对所有相容源位置、第二次测向误差及可能反馈应用统一后验更新，并最小化更新后位置可行域的最坏直径。`near` 视为可以直接进入清除的终止反馈。

完整联合位置—半径安全条件、纯角域几何达到曲线、有效覆盖和近场覆盖继续保留，但只用于扩展安全区域、检验主推荐点和分析保守性，不再参与在线主优化。移动距离仅在最坏直径数值不可区分时作为次级条件。

模型主线为
 
\[
\mathcal P_1
\longrightarrow \mathcal A_1
\longrightarrow \mathscr U
\longrightarrow \Phi(q)
\longrightarrow \mathcal Q^*.
\]
 
原有完整曲线与联合非劣区域保留为离线增强验证链：

\[
\text{第一次联合可能状态}
\rightarrow
\text{第二点三分支}
\rightarrow
\left(C_B^{\mathrm{rob}}(t),G_{\mathrm{rob}}(B),H_{\mathrm{rob}}(B)\right)
\rightarrow
\begin{cases}
\text{全局曲线非劣区域},\\
\text{严格接收安全非劣区域}.
\end{cases}
\]

正式答案至少应给出：

1. 随第一点和第一次示向度变化的保守安全候选区域；
2. 最坏后验直径的定义及第二检测点选择策略；
3. 经过稀疏搜索与局部二次求解得到的推荐点或推荐集合；
4. 推荐结果的最坏直径、最小包围圆和移动距离；
5. 完整曲线与联合状态安全条件给出的离线增强验证。

## 2. 纯角域交会接口

设 \(\mathcal W(P,\theta)\) 表示以检测点 \(P\) 为顶点、中心方向为 \(\theta\)、半角为测向误差上界 \(\varepsilon\) 的前向角域。

第一点为 \(A\)，第一次实测示向度为 \(\hat\theta_1\)。若第二点 \(B\) 获得实测示向度 \(\hat\theta_2\)，题面意义下的两点交会区域为

\[
\mathcal R_{\angle}(B,\hat\theta_2)
=
\mathcal W(A,\hat\theta_1)
\cap
\mathcal W(B,\hat\theta_2).
\]

定义扩展直径

\[
D_{\angle}(B,\hat\theta_2)
=
\operatorname{diam}
\left(
\mathcal R_{\angle}(B,\hat\theta_2)
\right).
\]

若交会区域无界，则规定

\[
D_{\angle}(B,\hat\theta_2)=+\infty.
\]

\(\mathcal R_{\angle}\) 不与目标圆、接收圆或近场圆裁剪。它严格沿用 Q1 的纯测向交会语义，作为后验更新的几何基础和离线曲线验证对象；Q2 主目标使用结合既有状态边界后的实际后验位置域直径。

## 3. 第一次观测后的联合状态

### 3.1 参数与未知状态

设：

- \(\mathcal D=\{x\in\mathbb R^2:\|x-O\|\le1800\}\) 为干扰源目标圆域；
- \(A\in\mathbb R^2\) 为第一检测点；
- \(\hat\theta_1\) 为第一次实测示向度；
- \(\varepsilon=1^\circ\) 为测向误差上界；
- \(r_0=5\ \mathrm m\) 为近场半径；
- \(R\in[R_{\min},R_{\max}]=[1000,1500]\ \mathrm m\) 为该源固定但未知的有效接收半径；
- \(s\in\mathcal D\) 为固定但未知的真实源位置；
- \(B\in\mathbb R^2\) 为第二检测点。

目标圆只约束干扰源，不约束机器狗第二点。源位置 \(s\)、接收半径 \(R\) 和测向误差均按可能状态或有界扰动处理，不解释为随机变量。

### 3.2 联合可能状态

给定接收半径 \(R\)，第一次返回 direction 后仍可能的源位置集合为

\[
\mathcal S_1(R)
=
\left\{
s\in\mathcal D:
r_0<\|s-A\|\le R,\ 
s\in\mathcal W(A,\hat\theta_1)
\right\}.
\]

为区分逻辑可能性与面积比例的可定义性，先定义逻辑相容接收半径集合

\[
\mathcal I_1^{\mathrm{poss}}
=
\left\{
R\in[R_{\min},R_{\max}]:
\mathcal S_1(R)\ne\varnothing
\right\},
\]

以及正面积相容接收半径集合

\[
\mathcal I_1^{\mathrm{area}}
=
\left\{
R\in\mathcal I_1^{\mathrm{poss}}:
|\mathcal S_1(R)|>0
\right\}.
\]

前者保留相切、单点和退化线段等零测度但逻辑上可能的边界状态；后者只服务于以面积为分母的几何汇总。显然

\[
\mathcal I_1^{\mathrm{area}}
\subseteq
\mathcal I_1^{\mathrm{poss}}.
\]

联合可能状态为

\[
\Omega_1
=
\left\{
(s,R):
R\in\mathcal I_1^{\mathrm{poss}},\qquad
s\in\mathcal S_1(R)
\right\}.
\]

其位置投影为

\[
\mathcal K_1
=
\operatorname{proj}_s(\Omega_1)
=
\bigcup_{R\in\mathcal I_1^{\mathrm{poss}}}\mathcal S_1(R).
\]

该表示保留 \(s\) 与 \(R\) 的耦合关系；计算位置投影不意味着二者独立。若 \(\mathcal I_1^{\mathrm{poss}}\ne\varnothing\) 而 \(\mathcal I_1^{\mathrm{area}}=\varnothing\)，则第一次观测只留下低维退化状态。此时保留逻辑状态与安全判断，但不定义后续面积比例和曲线非劣区域，并将场景单列为退化输入。

### 3.3 第二点有限候选域

若第二点到 \(\mathcal K_1\) 中所有可能源位置的距离均超过 \(R_{\max}\)，任何状态下都不会取得有效反馈。因此可无损地限制

\[
\mathcal B_0
=
\left(
\mathcal K_1
\oplus
\overline B(0,R_{\max})
\right)
\setminus\{A\}.
\]

\(\mathcal B_0\) 是有信息价值的有限决策域，不是机器狗物理活动边界。排除 \(B=A\) 是因为同地点重复检测误差不变，不能提供新的独立交会几何。

## 4. 第二点三分支与可评价域

对 \(B\in\mathcal B_0\) 和 \(R\in\mathcal I_1^{\mathrm{poss}}\)，定义

\[
\mathcal N_B(R)
=
\left\{
s\in\mathcal S_1(R):
\|s-B\|\le r_0
\right\},
\]

\[
\mathcal G_B(R)
=
\left\{
s\in\mathcal S_1(R):
r_0<\|s-B\|\le R
\right\},
\]

\[
\mathcal F_B(R)
=
\left\{
s\in\mathcal S_1(R):
\|s-B\|>R
\right\}.
\]

三者两两不交且并为 \(\mathcal S_1(R)\)，分别对应：

- \(\mathcal N_B(R)\)：返回 near，直接进入近场光学定位；
- \(\mathcal G_B(R)\)：返回 direction，形成第二条示向信息；
- \(\mathcal F_B(R)\)：返回 no_signal，本次两点交会未取得第二条示向信息。

定义存在 direction 评价意义的候选域

\[
\mathcal B_{\mathrm{eval}}
=
\left\{
B\in\mathcal B_0:
\exists R\in\mathcal I_1^{\mathrm{area}},\qquad
|\mathcal G_B(R)|>0
\right\}.
\]

对不属于 \(\mathcal B_{\mathrm{eval}}\)、但某些状态下可能直接近场成功的点，定义

\[
\mathcal B_{\mathrm{near}}
=
\left\{
B\in
\mathcal B_0\setminus\mathcal B_{\mathrm{eval}}:
\exists R\in\mathcal I_1^{\mathrm{area}},\qquad
|\mathcal N_B(R)|>0
\right\}.
\]

\(\mathcal B_{\mathrm{near}}\) 不具有纯交会定位曲线，不参加全局曲线支配，只作为特殊近场候选单列。

## 5. 主选点模型：保守安全区域与最坏后验直径
 
为避免与离线增强评价中的候选点 \(B\) 混淆，主模型记第一次观测后的源位置投影为 \(\mathcal P_1:=\mathcal K_1\)，并以 \(q\in\mathcal B_0\) 表示待选择的第二检测位置。
 
保守接收余量定义为
 
$$
 \Delta_1(q)=\sup_{z\in\mathcal P_1}\|q-z\|.
$$
 
相应的保守安全候选区域为
 
$$
 \mathcal A_1=\{q\in\mathcal B_0:\Delta_1(q)\le R_{\min}\}.
$$
 
对任意 \(q\in\mathcal A_1\) 和任意 \((z,R)\in\Omega_1\)，都有 \(\|q-z\|\le R_{\min}\le R\)。因此，已确认存活的全向源在该区域内不会因距离返回 `no_signal`，只可能返回 `near` 或 `direction`。该条件是接收安全的充分条件而非必要条件；当 \(\mathcal P_1\) 是凸多边形时，\(\Delta_1(q)\) 的最大值只需在多边形顶点上检查。
 
设 \(\mathcal Y_1(q)\) 为候选点 \(q\) 在全部相容状态下可能产生的反馈集合，\(\mathscr U(\mathcal P_1,q,y)\) 为调用 Q1 几何接口后的后验位置域。两个安全分支分别为：
 
- 若 \(y=\texttt{near}\)，则后验位置域为 \(\mathcal P_1\cap\overline B(q,r_0)\)，并且当前位置已满足清除距离条件；
- 若 \(y=\texttt{direction}(\hat\theta_2)\)，则后验位置域为 \(\mathcal P_1\cap\mathcal W(q,\hat\theta_2)\)，同时继续保留目标圆和已有距离约束。
 
将 `near` 作为终止反馈并令其损失为零；对 `direction`，损失定义为后验位置域直径。于是
 
$$
 \ell(q,y)=0\quad\text{if }y=\texttt{near},
$$
 
$$
 \ell(q,y)=\operatorname{diam}[\mathscr U(\mathcal P_1,q,y)]
 \quad\text{if }y=\texttt{direction}.
$$
 
第二点的最坏后验直径为
 
$$
 \Phi(q)=\sup_{y\in\mathcal Y_1(q)}\ell(q,y),
 \qquad q\in\mathcal A_1.
$$
 
主推荐集合定义为
 
$$
 \mathcal Q^*=\operatorname*{arg\,min}_{q\in\mathcal A_1}\Phi(q).
$$
 
该目标不使用概率、期望或定位—移动加权和。数值精度下存在多个不可区分的最优点时，全部保留为推荐集合，再以移动距离 \(\|q-A\|\) 作为次级选择。若 \(\mathcal A_1=\varnothing\)，不得伪造安全解；此时才调用第 8 节的联合状态安全增强条件，或向 Q3 返回需要恢复策略的状态。
 
## 6. 离线增强：最坏纯角域曲线与覆盖分析

### 6.1 单状态最坏交会直径

若真实源位置为 \(s\in\mathcal G_B(R)\)，第二次实测示向度可表示为

\[
\hat\theta_2
=
\arg(s-B)+e_2,
\qquad
|e_2|\le\varepsilon.
\]

定义该状态在第二次误差区间内的最坏纯交会直径

\[
D_{\angle}^{\mathrm{worst}}(B,s)
=
\sup_{|e_2|\le\varepsilon}
D_{\angle}
\left(
B,\arg(s-B)+e_2
\right).
\]

只要误差区间内存在无界交会，或有限交会直径没有统一有限上界，就有

\[
D_{\angle}^{\mathrm{worst}}(B,s)=+\infty.
\]

目标圆和接收圆不能将这一无界状态改写成有限定位效果。

### 6.2 固定接收半径的几何达到率

对 \(R\in\mathcal I_1^{\mathrm{area}}\)、\(t\ge0\) 且 \(|\mathcal G_B(R)|>0\)，定义

\[
C_B(t;R)
=
\frac{
\left|
\left\{
s\in\mathcal G_B(R):
D_{\angle}^{\mathrm{worst}}(B,s)\le t
\right\}
\right|
}{
|\mathcal G_B(R)|
}.
\]

\(C_B(t;R)\) 表示 direction 状态集合中，最坏纯交会直径不超过 \(t\) 的状态空间面积比例，称为几何达到率。它采用 Lebesgue 面积作为几何汇总测度，意味着单位面积等权，但不代表成功概率、经验分布或源位置先验。

若 \(|\mathcal G_B(R)|=0\)，则 \(C_B(t;R)\) 未定义，不记为 0 或 1；该半径下的结果由 near、no_signal 及覆盖指标解释。

### 6.3 未知接收半径下的稳健曲线

对 \(B\in\mathcal B_{\mathrm{eval}}\)，定义

\[
\mathcal I_B^{\mathrm{dir}}
=
\left\{
R\in\mathcal I_1^{\mathrm{area}}:
|\mathcal G_B(R)|>0
\right\}.
\]

稳健几何达到曲线为

\[
C_B^{\mathrm{rob}}(t)
=
\inf_{R\in\mathcal I_B^{\mathrm{dir}}}
C_B(t;R),
\qquad t\ge0.
\]

它是所有相容且 direction 非空的接收半径曲线的点态下包络。不同 \(t\) 处的最不利值可以来自不同 \(R\)，所以它不对应某一个固定接收半径下的真实状态分布。

### 6.4 有效覆盖与近场覆盖

对 \(R\in\mathcal I_1^{\mathrm{area}}\)，定义

\[
G(B;R)
=
\frac{
|\mathcal N_B(R)\cup\mathcal G_B(R)|
}{
|\mathcal S_1(R)|
}
=
1-
\frac{
|\mathcal F_B(R)|
}{
|\mathcal S_1(R)|
},
\]

\[
G_{\mathrm{rob}}(B)
=
\inf_{R\in\mathcal I_1^{\mathrm{area}}}G(B;R).
\]

\(G_{\mathrm{rob}}\) 衡量未知接收半径下最不利的有效反馈面积比例。它仍是几何面积比例，而不是概率。

近场覆盖定义为

\[
H(B;R)
=
\frac{
|\mathcal N_B(R)|
}{
|\mathcal S_1(R)|
},
\qquad
H_{\mathrm{rob}}(B)
=
\inf_{R\in\mathcal I_1^{\mathrm{area}}}H(B;R).
\]

\(H_{\mathrm{rob}}\) 衡量未知接收半径下最不利的近场直接终止面积比例。它与 \(G_{\mathrm{rob}}\) 一样是几何面积比例，不是成功概率。由于 near 比普通 direction 更接近任务终止，\(H_{\mathrm{rob}}\) 进入正式支配关系，但不与定位曲线或有效覆盖加权合并。

## 7. 离线增强：全局曲线非劣候选区域

对 \(B_1,B_2\in\mathcal B_{\mathrm{eval}}\)，若

\[
C_{B_1}^{\mathrm{rob}}(t)
\ge
C_{B_2}^{\mathrm{rob}}(t),
\qquad
\forall t\ge0,
\]

同时

\[
G_{\mathrm{rob}}(B_1)
\ge
G_{\mathrm{rob}}(B_2),
\]

以及

\[
H_{\mathrm{rob}}(B_1)
\ge
H_{\mathrm{rob}}(B_2),
\]

且曲线、有效覆盖或近场覆盖至少一处严格更好，则称 \(B_1\) 全局曲线支配 \(B_2\)。

全局非劣候选区域定义为

\[
\mathcal B^*
=
\left\{
B\in\mathcal B_{\mathrm{eval}}:
\nexists B'\in\mathcal B_{\mathrm{eval}}
\text{ 全局曲线支配 }B
\right\}.
\]

曲线交叉时两个候选均保留。该支配关系不设定位直径阈值，不把定位曲线、有效覆盖、近场覆盖和移动距离压成加权总分。\(\mathcal B^*\) 可以是曲线、窄带、不连通集合或具有正面积的区域，不预设为单个点或连续二维区域。

## 8. 联合状态安全增强与安全非劣区域
 
第 5 节的 \(\mathcal A_1\) 仅使用 \(R_{\min}\)，计算简单且便于在线递归。本节利用第一次接收事实保留的位置—半径耦合关系，可认证部分位于 \(\mathcal A_1\) 外的额外安全点。它是保守安全区域为空时的后备方案，也是衡量主模型保守性的离线增强，不进入默认在线主循环。

### 8.1 接收安全余量

定义

\[
\Gamma(B)
=
\sup_{(s,R)\in\Omega_1}
\left(
\|s-B\|-R
\right).
\]

对固定 \(s\in\mathcal K_1\)，与第一次观测相容的最小接收半径为

\[
R_{\mathrm{low}}(s)
=
\max
\left\{
R_{\min},\|s-A\|
\right\}.
\]

因而

\[
\Gamma(B)
=
\sup_{s\in\mathcal K_1}
\left[
\|s-B\|
-
\max
\left\{
R_{\min},\|s-A\|
\right\}
\right].
\]

由于题面有效接收条件包含距离等于 \(R\) 的边界，

\[
\Gamma(B)\le0
\]

当且仅当第二点对所有相容联合状态都不会 no_signal。该集合全称条件强于 \(G_{\mathrm{rob}}(B)=1\)：后者仍可能允许面积为零但非空的失败状态。

### 8.2 安全集合的三层输出

全部接收安全点定义为

\[
\mathcal S_{\mathrm{safe}}
=
\left\{
B\in\mathcal B_0:
\Gamma(B)\le0
\right\}.
\]

其中能够进行 direction 曲线评价的安全点为

\[
\mathcal S_{\mathrm{safe}}^{\mathrm{dir}}
=
\mathcal S_{\mathrm{safe}}
\cap
\mathcal B_{\mathrm{eval}}.
\]

在安全点内部，若

\[
C_{B_1}^{\mathrm{rob}}(t)
\ge
C_{B_2}^{\mathrm{rob}}(t),
\qquad
\forall t\ge0,
\]

同时

\[
H_{\mathrm{rob}}(B_1)
\ge
H_{\mathrm{rob}}(B_2),
\]

且曲线或近场覆盖至少一处严格，则称安全点 \(B_1\) 曲线支配安全点 \(B_2\)。安全集合内已有 \(G_{\mathrm{rob}}=1\)，无需重复用有效覆盖比例排序，但仍需保留 near 直接终止收益。

安全非劣区域定义为

\[
\mathcal B_{\mathrm{safe}}^*
=
\left\{
B\in\mathcal S_{\mathrm{safe}}^{\mathrm{dir}}:
\nexists B'\in\mathcal S_{\mathrm{safe}}^{\mathrm{dir}}
\text{ 曲线支配 }B
\right\}.
\]

全局前沿中同时严格安全的部分为

\[
\mathcal B_{\mathrm{global,safe}}^*
=
\mathcal B^*
\cap
\mathcal S_{\mathrm{safe}}^{\mathrm{dir}}.
\]

纯近场安全集合为

\[
\mathcal S_{\mathrm{safe}}^{\mathrm{near}}
=
\left\{
B\in\mathcal S_{\mathrm{safe}}:
\mathcal G_B(R)=\varnothing,\qquad
\forall R\in\mathcal I_1^{\mathrm{poss}}
\right\}.
\]

该定义是逐状态的纯近场条件，不以 direction 分支面积为零替代 direction 分支为空，因此不会把只含零测度 direction 状态的候选误称为纯近场安全点。

\(\mathcal B_{\mathrm{safe}}^*\) 与 \(\mathcal B_{\mathrm{global,safe}}^*\) 不能互相替代：前者保证即使安全点被带有边界风险的全局候选支配，也仍保留安全方案内部的最佳选择。

## 9. 离线曲线尾部与代表集合

### 9.1 固定半径无界状态

定义

\[
\mathcal U_B(R)
=
\left\{
s\in\mathcal G_B(R):
D_{\angle}^{\mathrm{worst}}(B,s)=+\infty
\right\},
\]

\[
u_B(R)
=
\frac{
|\mathcal U_B(R)|
}{
|\mathcal G_B(R)|
}.
\]

对固定 \(R\) 有

\[
\lim_{t\to+\infty}C_B(t;R)
=
1-u_B(R).
\]

\(u_B(R)\) 才是固定接收半径下无界交会状态的面积比例。

### 9.2 稳健曲线平台

定义

\[
p_\infty(B)
=
\lim_{t\to+\infty}
C_B^{\mathrm{rob}}(t)
=
\sup_{0\le t<\infty}
\inf_{R\in\mathcal I_B^{\mathrm{dir}}}
C_B(t;R).
\]

其严格含义为

\[
\forall p\in[0,p_\infty(B)),
\quad
\exists t_p<\infty,
\quad
\forall R\in\mathcal I_B^{\mathrm{dir}},
\quad
C_B(t_p;R)\ge p.
\]

因此 \(p_\infty(B)\) 是通过不断放宽一个统一有限定位尺度所能逼近的最大稳健达到水平。它不保证在有限 \(t\) 处真正取得，也不等于某个固定 \(R\) 下有限状态比例的简单最坏值。

定义

\[
d_{\mathrm{tail}}(B)
=
\inf
\left\{
t<\infty:
C_B^{\mathrm{rob}}(t)=p_\infty(B)
\right\},
\]

并约定集合为空时

\[
d_{\mathrm{tail}}(B)=+\infty.
\]

### 9.3 代表结果允许为集合

覆盖优先代表集合为

\[
\mathcal R_G
=
\operatorname*{arg\,max}_{B\in\mathcal B^*}
G_{\mathrm{rob}}(B).
\]

近场终止优先代表集合为

\[
\mathcal R_H
=
\operatorname*{arg\,max}_{B\in\mathcal B^*}
H_{\mathrm{rob}}(B).
\]

尾部优先代表集合按字典序定义为

\[
\mathcal R_{\mathrm{tail}}
=
\operatorname*{arg\,lex\,max}_{B\in\mathcal B^*}
\left(
p_\infty(B),-d_{\mathrm{tail}}(B)
\right).
\]

安全代表集合可在 \(\mathcal B_{\mathrm{safe}}^*\) 内分别按近场终止优先和同一尾部顺序构造。上述集合均允许包含多个点或区域；模型不保证存在唯一代表点，也不保证连续候选域上的上确界一定取得。上述 arg max 或字典序 arg max 只在相应极值取得时定义；否则由 METHOD.md 在有限数值候选集上报告逼近代表集合。面积均值、曲线面积或有限分位点若用于展示，只能作为预先声明的辅助规则，不能改变正式候选区域。

## 10. 状态一致域与实际可清除性

若第二点获得示向度 \(\hat\theta_2\)，定义结合全部已知边界后的状态一致位置域

\[
\begin{aligned}
\mathcal K_2(B,\hat\theta_2)
=
\{x\in\mathcal D:\;&
x\in
\mathcal W(A,\hat\theta_1)
\cap
\mathcal W(B,\hat\theta_2),\\
&
r_0<\|x-A\|\le R_{\max},\\
&
r_0<\|x-B\|\le R_{\max}
\}.
\end{aligned}
\]

\(\mathcal K_2\subseteq\mathcal K_1\)，回答利用目标圆、历史状态和第二次示向后还剩多少实际可能位置。它是第 5 节后验更新算子在 `direction` 分支下的具体实现，也是最坏后验直径的直接评价对象；纯角域 \(\mathcal R_\angle\) 继续用于 Q1 几何求交和离线曲线对照。

对代表点可报告：

- \(\operatorname{diam}\mathcal K_2\)；
- 最小包围圆半径
  \[
  \rho(P)=\min_c\max_{x\in P}\|x-c\|;
  \]
- \(H_{\mathrm{rob}}\)；
- 移动距离
  \[
  M(B)=\|B-A\|.
  \]

只有 \(\rho(P)\le20\ \mathrm m\) 才能保证存在一点距全部剩余可能源位置不超过 20 m。一般不能由区域直径不超过 40 m 直接推出该结论。

若 \(|\mathcal G_B(R)\setminus\mathcal U_B(R)|>0\)，且下式积分存在，固定 \(R\) 下有限交会状态的真实几何均值可定义为

\[
\mu_{\mathrm{fin}}(B;R)
=
\frac{
\displaystyle
\int_{\mathcal G_B(R)\setminus\mathcal U_B(R)}
D_{\angle}^{\mathrm{worst}}(B,s)\,ds
}{
|\mathcal G_B(R)\setminus\mathcal U_B(R)|
},
\]

但必须按 \(R\) 报告，并允许积分不存在或发散。稳健曲线归一化后的面积不能解释为这一条件均值。

## 11. 约束、适用边界与后续接口

模型保留：

- 声源在两次检测间静止；
- 每个源的 \(R\) 固定但未知；
- 三分支由真实距离严格决定；
- 测向误差只有界，不假设独立、均匀或正态；
- 角度按模 \(360^\circ\) 处理；
- 近共线、无界、相切、空分支和目标圆边界状态；
- 第二点可以位于目标圆外。

模型不引入：

- 源位置或接收半径概率；
- 定位、覆盖和移动距离的加权总分；
- 固定交会角、固定移动距离或人为定位阈值；
- 道路、地形、障碍物和机器狗活动圆域；
- 多源调度、频道管理或定向辐射状态。

Q2 向 Q3 提供可重复调用的轻量选点算子：输入当前的位置可行域及必要历史约束，输出保守安全区域、少量推荐测点和最坏后验直径。Q3 每次调用 Q1 更新定位状态后，可重新调用该算子，但仍需自行处理多源调度、移动时间和频道切换。完整曲线与全域多分辨率求解器只作离线对照，不得进入每一步在线循环。

Q4 可以继承后验更新—候选生成—局部求解的接口框架，以及取得 `direction` 后的 Q1 角域更新；定向源的 `no_signal` 还可能由发射方向造成，必须扩展位置—方向状态并重新定义安全候选，不能直接继承 Q2 的 \(\mathcal A_1\)。

本模型不依赖某一组 Q1 数值实例；当前实现已复用经过验证的 Q1 纯角域求交、无界判定和直径计算接口。
