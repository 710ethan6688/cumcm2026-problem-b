# -*- coding: utf-8 -*-
import io

section6_tex_optimized = r"""
\section{问题四：全向—定向混合源的搜索与保证清除策略}

\subsection{问题分析与核心困难}

问题四在问题三的物理机制基础上，进一步引入半平面定向干扰源。各干扰源独占单一频道的客观物理规律保持不变，总数依然处于 $10\sim 16$ 个之间，但其中定向干扰源的具体数目及其各自的辐射主瓣朝向均完全未知。其余运动速度、天线调谐与测向耗时、测向角度确定性误差区间 $[-1^\circ, 1^\circ]$、以及 $20\text{ m}$ 光学精确定位与激光清除等约束条件与前述问题完全一致。

由全向辐射拓展至非对称定向辐射后，系统面临三大核心机理挑战：
\begin{enumerate}[leftmargin=2.5em, itemsep=0.1em]
    \item \textbf{背向静默与无信号的多重成因分析}：定向干扰源仅在其未知辐射朝向确定的 $180^\circ$ 闭半平面内发射电磁信号。当机器狗停靠检测未收到信号时，该观测反馈不再等价于距离超出有效覆盖范围，而可能由频道空置、目标已清除、空间距离超出物理覆盖上限、或测站恰好落入目标辐射盲侧四类互斥物理状态析取而成。因此，不能依据单次检测无信号直接排除几何空间。
    \item \textbf{单一测站覆盖准则失效与多视角包围要求}：在问题三中，任意测站与其周围 $1000\text{ m}$ 圆盘内的全向目标均可建立双向通信；而在定向辐射条件下，即使测站与目标距离小于 $1000\text{ m}$，若测站位于目标背向则依然无法探测。要对任意未知朝向的目标实现无遗漏发现，目标必须被周围多个邻近测站几何包围，从而使得无论目标朝向何方，至少存在一个测站落入其有效发射半平面内。
    \item \textbf{有限探测成本与长尾清除耗时的权衡}：在获得初始示向后，若直接机动至候选测站可能再次陷入目标发射盲侧而失联；若完全依赖盲目网格搜索，则会导致任务时间随网格单元遍历而急剧膨胀。因此，必须在理论保证主链之外，建立能够识别盲侧并自适应终止追加测向的轻量决策支路。
\end{enumerate}

\subsection{数学模型构建与信息状态表示}

\subsubsection{目标物理状态与活动指示变量}

设系统包含 20 个离散频道，频道集合记为 $\mathcal{C} = \{1, 2, \dots, 20\}$。目标真实分布状态由多元组表征：
\begin{equation}
    \mathbf{X}_c = (e_c, \mathbf{x}_c, R_{c}, \tau_c, \mathbf{u}_c), \quad c \in \mathcal{C}
\end{equation}
其中 $e_c \in \{0, 1\}$ 表示频道 $c$ 是否客观存在物理目标（总目标数满足 $N = \sum_{c=1}^{20} e_c \in [10, 16]$）；$\mathbf{x}_c = (x_c, y_c)^\top \in \Omega$ 为目标二维坐标；$R_{c} \in [1000, 1500]\text{ m}$ 为该目标的实际最大电磁覆盖半径；$\tau_c \in \{\mathrm{O}, \mathrm{D}\}$ 表征天线辐射类型（$\mathrm{O}$ 为全向辐射，$\mathrm{D}$ 为半平面定向辐射）；$\mathbf{u}_c = (\cos\phi_c, \sin\phi_c)^\top$ 为定向目标的单位法向辐射方向向量（若 $\tau_c = \mathrm{O}$ 则该项不具物理约束）。

为严谨刻画作业过程中目标被清除后的状态变化，引入离散时间步 $k$ 处的动态活动指示变量 $a_c^k \in \{0, 1\}$。初始时刻 $a_c^0 = e_c$；当且仅当机器狗在目标附近 $20\text{ m}$ 范围内成功实施激光清除后，$a_c^k$ 单向置为 0。

\subsubsection{互斥完备的几何接收与观测模型}

对于处于活动状态的目标（$a_c^k = 1$），定义其在二维空间检测位置 $\mathbf{q}$ 处的几何可接收谓词 $\mathcal{V}_c(\mathbf{q})$：
\begin{equation}
    \mathcal{V}_c(\mathbf{q}) = \Big[ \|\mathbf{q} - \mathbf{x}_c\| \le R_{c} \Big] \land \Big[ \tau_c = \mathrm{O} \;\lor\; \mathbf{u}_c^\top (\mathbf{q} - \mathbf{x}_c) \ge 0 \Big]
\end{equation}
式中包含边界 $\mathbf{u}_c^\top (\mathbf{q} - \mathbf{x}_c) = 0$ 的平角扇区均具备正常发射接收能力；若目标与检测点恰好重合（$\mathbf{q} = \mathbf{x}_c$），约定内积为 0，计入有效视场。

根据环境物理反馈规则，测站 $\mathbf{q}$ 处对频道 $c$ 的实测反馈 $y_c(\mathbf{q})$ 严格划分为如下三个互斥完备的分支：
\begin{equation}
    y_c(\mathbf{q}) = \begin{cases}
        \texttt{no\_signal}, & a_c^k = 0 \;\lor\; \neg \mathcal{V}_c(\mathbf{q}), \\
        \texttt{near}, & a_c^k = 1 \;\land\; \mathcal{V}_c(\mathbf{q}) \;\land\; \|\mathbf{q} - \mathbf{x}_c\| \le 5\text{ m}, \\
        \texttt{direction}(\hat{\theta}_c), & a_c^k = 1 \;\land\; \mathcal{V}_c(\mathbf{q}) \;\land\; \|\mathbf{q} - \mathbf{x}_c\| > 5\text{ m}
    \end{cases}
\end{equation}
当返回有效示向角 $\hat{\theta}_c$ 时，真实方位角 $\theta_c^\ast = \operatorname{atan2}(y_c - q_y, x_c - q_x)$ 严格满足确定性有界约束 $|\theta_c^\ast - \hat{\theta}_c| \le \varepsilon = 1^\circ$。算法在实际数值交会计算中采用 $\varepsilon_{\mathrm{tol}} = 1.005^\circ$ 的微小数值裕量，防止因浮点舍入误差剔除真实边界。

\subsubsection{频道追踪信息状态表征与双重时间约束}

机器狗针对每个频道 $c \in \mathcal{C}$ 独立维护五元追踪信息状态 $\mathcal{I}_c^k = (s_c^k, P_c^k, \mathcal{M}_c^k, \mathcal{V}_c^{\mathrm{hist}}, \mathcal{B}_c^{\mathrm{hist}})$：包含离散状态标示 $s_c^k \in \{\text{未探明}, \text{已发现}, \text{定位中}, \text{网格兜底}, \text{已清除}, \text{确证空置}\}$；紧致凸多边形位置外包 $P_c^k \subset \mathbb{R}^2$（初始为目标圆外切正四十八边形）；25 点骨架完成集 $\mathcal{M}_c^k \subseteq \{1, \dots, 25\}$；以及历史正观测站集 $\mathcal{V}_c^{\mathrm{hist}}$ 与可信盲侧测站集 $\mathcal{B}_c^{\mathrm{hist}}$。

赛题规定的虚拟物理总时间由位移、天线调谐、停靠检测、以及光学清除耗时累加确定：
\begin{equation}
    T_{\mathrm{virtual}} = \frac{L}{v} + 5 N_{\mathrm{meas}} + 1 N_{\mathrm{switch}} + 3 N_{\mathrm{clear}}^{\mathrm{fail}} + 5 N_{\mathrm{clear}}^{\mathrm{succ}}
\end{equation}
式中平台速度 $v = 5\text{ m/s}$；$N_{\mathrm{meas}}$ 为检测总次数（每次 $5\text{ s}$）；$N_{\mathrm{switch}}$ 为切频次数（每次 $1\text{ s}$）；清除成功耗时 $5\text{ s}$（$3\text{ s}$ 光学定位与 $2\text{ s}$ 激光发射），未命中消耗 $3\text{ s}$。同时受正式测试客观运行时间约束：算法决策与通信总耗时 $T_{\mathrm{wall}} \le 20\text{ min}$。

\subsection{策略设计与求解算法体系}

本文构建双轨分权协同架构：以方向完备搜索骨架、确定性凸外包求交、以及有限网格遍历构成保证全部清除的理论主链；以几何距离安全主动探测、对称镜像重捕获、以及尾部前瞻判据构成压缩无效机动的效率改进支路。

\subsubsection{多视角包围理论与 25 点双环拓扑剖分}

针对半平面定向天线背向静默的物理特点，首先从几何学角度给出测站分布对未知朝向目标的可探测保证准则：

\noindent\textbf{命题 5（局部多测站凸包包围对半平面定向目标的探测保证）}\quad 给定固定物理接收半径 $r > 0$ 与有限测站集合 $\mathcal{S}$。对于任意空间目标位置 $\mathbf{x}$，定义其局部有效测站子集为 $\mathcal{S}_r(\mathbf{x}) = \{\mathbf{q} \in \mathcal{S} \mid \|\mathbf{q} - \mathbf{x}\| \le r\}$。在 $180^\circ$ 闭半平面辐射模型下，该目标在任意未知朝向单位向量 $\mathbf{u}$ 下均至少能被 $\mathcal{S}_r(\mathbf{x})$ 中一个测站有效探测，当且仅当目标位置处于该局部测站子集的凸包内部：$\mathbf{x} \in \operatorname{conv}( \mathcal{S}_r(\mathbf{x}) )$。

\begin{cumcmproof}
充分性：设 $\mathbf{x} \in \operatorname{conv}(\mathcal{S}_r(\mathbf{x}))$，存在权值 $\lambda_i \ge 0$ 且 $\sum_{i=1}^m \lambda_i = 1$，使 $\mathbf{x} = \sum_{i=1}^m \lambda_i \mathbf{q}_i$。与任意单位向量 $\mathbf{u}$ 作内积得 $\sum_{i=1}^m \lambda_i \mathbf{u}^\top (\mathbf{q}_i - \mathbf{x}) = \mathbf{u}^\top \mathbf{0} = 0$。不可能所有内积项均严格小于零，必存在 $\mathbf{q}_k \in \mathcal{S}_r(\mathbf{x})$ 满足 $\mathbf{u}^\top (\mathbf{q}_k - \mathbf{x}) \ge 0$ 且 $\|\mathbf{q}_k - \mathbf{x}\| \le r$，保证可被探测。

必要性：若 $\mathbf{x} \notin \operatorname{conv}(\mathcal{S}_r(\mathbf{x}))$，由超平面分离定理，存在向量 $\mathbf{v}$ 使对所有局部测站均有 $\mathbf{v}^\top (\mathbf{q}_i - \mathbf{x}) < 0$。取辐射朝向 $\mathbf{u} = -\mathbf{v} / \|\mathbf{v}\|$，则所有局部测站均处于盲侧。
\end{cumcmproof}

\noindent\textbf{推论 1（最小接收半径下的稳健充分保证）}\quad 针对接收半径确界 $R_c \in [1000, 1500]\text{ m}$ 工况，若在保底半径 $R_{\min} = 1000\text{ m}$ 下满足 $\mathbf{x} \in \operatorname{conv}(\mathcal{S}_{1000}(\mathbf{x}))$，则是目标在全工况下全方向可被发现的统一稳健充分条件。

基于命题 5 与推论 1，在目标区域 $\Omega$ 内构造由 25 个特征测站与 36 个平面三角形组成的双环三角剖分拓扑构型：中心测站位于原点 $(0, 0)$；内环 12 点分布于半径 $950\text{ m}$ 圆周，极角为 $i \times 30^\circ$；外环 12 点分布于半径 $1870\text{ m}$ 圆周，极角交错旋转 $15^\circ$（$j \times 30^\circ + 15^\circ$）。关键参数汇总于表 \ref{tab:q4_topology_params}，几何构型如图 \ref{fig:q4_25point_coverage} 所示。

\begin{table}[htbp]
    \centering
    \footnotesize
    \caption{25 点双环拓扑几何参数与方向完备验证表}
    \label{tab:q4_topology_params}
    \renewcommand{\arraystretch}{0.90}
    \setlength{\tabcolsep}{2.8pt}
    \begin{tabularx}{\linewidth}{l c c X}
        \toprule[1.5pt]
        \textbf{几何拓扑参数项} & \textbf{解析表达式 / 理论值} & \textbf{数值计算结果} & \textbf{全域探测保证判定结论} \\
        \midrule
        外环正十二边形内切圆半径 & $R_2 \cos(15^\circ) = 1870 \times 0.9659$ & $1806.28\text{ m}$ & 严格大于目标圆半径 $1800\text{ m}$，实现全域几何包络 \\
        剖分三角形最大边长 $d_{\max}$ & $\sqrt{R_1^2 + R_2^2 - 2 R_1 R_2 \cos(15^\circ)}$ & $983.60\text{ m}$ & 严格小于保底半径 $1000\text{ m}$，具备 $16.40\text{ m}$ 探测裕度 \\
        三角形单元几何顶点测距 & 任意内点至三顶点距离均 $\le d_{\max}$ & $\le 983.60\text{ m}$ & 每个单元内部点均能被其所在三角形 3 顶点有效覆盖 \\
        未知朝向多视角凸包判定 & 目标恒处于所在三角形三顶点凸包内 & 满足命题 5 条件 & 任意未知朝向至少落入一个顶点的有效视场内 \\
        \bottomrule[1.5pt]
    \end{tabularx}
\end{table}

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.40\linewidth]{images/fig_q4_25point_coverage.png}
    \caption{25 点双环拓扑剖分与多视角凸包方向完备覆盖构型}
    \label{fig:q4_25point_coverage}
\end{figure}

根据 Carathéodory 定理，平面上任意紧致凸包内的点均可由不超过 3 个极点凸组合表征。图 \ref{fig:q4_25point_coverage} 直观表明，目标区域内的任意点均落入 36 个三角形之一，其 3 个顶点到该点的距离均小于 $1000\text{ m}$ 且将该点包含在凸包内，严格确证了 25 点基准搜索测站在全向—定向混合目标下的完备可发现能力。

\subsubsection{距离安全 Q2 候选选点与保守位置外包}

当在测站 $\mathbf{q}_1$ 处首次捕获频道 $c$ 的有效示向角 $\hat{\theta}_1$ 时，构建包含真实目标坐标的初始紧致凸多边形位置外包：$P_c^1 = P_{\Omega}^{\mathrm{out}} \cap \mathcal{B}^{\mathrm{out}}(\mathbf{q}_1, 1500) \cap \mathcal{W}(\mathbf{q}_1, \hat{\theta}_1, \varepsilon_{\mathrm{tol}})$。其中 $P_{\Omega}^{\mathrm{out}}$ 为半径 $1800\text{ m}$ 目标圆的外切正四十八边形；$\mathcal{B}^{\mathrm{out}}(\mathbf{q}_1, 1500)$ 为测站最大覆盖圆的外切多边形；$\mathcal{W}(\mathbf{q}_1, \hat{\theta}_1, \varepsilon_{\mathrm{tol}})$ 为包含实测示向度在内、半张角为 $1.005^\circ$ 的角楔区域。

\noindent\textbf{引理 1（确定性测向误差下交会凸多边形维持目标真值包含）}\quad 设初始几何外包满足真实位置 $\mathbf{x}_c \in P_c^1$。在后续各测站 $\mathbf{q}_k$ 处获取的有效测向角域 $\mathcal{W}_k$ 严格覆盖真实物理方位角，则通过半平面精确求交迭代生成的凸多边形序列恒满足真值包含关系：$P_c^{k+1} = P_c^k \cap \mathcal{W}_k \implies \mathbf{x}_c \in P_c^{k+1}, \forall k \ge 1$。

第二检测点选取遵循距离安全准则：从以当前多边形形心为基准的离散候选空间中筛选测站，要求其到可行域内任意样本点的最大几何距离均严格小于 $995\text{ m}$，排除超出 $1000\text{ m}$ 物理视距导致丢失信号的风险，优先选取定位几何增益最大的测站。

\subsubsection{对称镜像重捕获与自适应尾部前瞻探测}

若在距离安全的第二检测点处测向反馈为无信号，目标必然落入背向辐射盲侧。系统启动两项效率优化机制：
\begin{enumerate}[leftmargin=2.5em, itemsep=0.08em]
    \item \textbf{条件对称镜像重捕获}：若主动测向预算尚未耗尽，算法沿首次示向中轴线将失联测站对称反射至对侧几何位置 $\mathbf{q}_{\mathrm{mirror}} = \mathbf{q}_1 + 2 [ (\mathbf{q}_2 - \mathbf{q}_1)^\top \mathbf{u}(\hat{\theta}_1) ] \mathbf{u}(\hat{\theta}_1) - (\mathbf{q}_2 - \mathbf{q}_1)$，若仍满足距离安全约束则前往探测，形成反向观测视场。
    \item \textbf{自适应尾部前瞻探测}：在可行域内离散生成 96 个位置样本与 36 个法向朝向样本，统计相容于历史正负观测的有效样本比例，记为几何相容状态代理量 $p_v \in [0, 1]$。
\end{enumerate}

\noindent\textbf{判据 3（基于几何相容代理与时间增益的尾部前瞻探测）}\quad 设当前相交网格最差次序遍历耗时为 $T_{\mathrm{grid}}$，候选探测耗时为 $T_{\mathrm{probe}} = d/v + 5\text{ s}$，一次前瞻后验直径为 $D_{\mathrm{post}}$，当前直径为 $D$。当且仅当几何相容代理量满足门槛 $p_v \ge 0.30$，且探测期望收益高于机动检测成本时，追加一次终端探测：
\begin{equation}
    T_{\mathrm{probe}} < T_{\mathrm{grid}} \cdot p_v \left[ 1 - \left( \frac{D_{\mathrm{post}}}{D} \right)^2 \right], \quad p_v \ge 0.30
\end{equation}
若探测成功获取示向，则立即完成最后一次多边形裁剪并转入直接清除；若再次无信号或判据不成立，则果断终止追加测向，立即转入有限网格遍历清除终局。

\subsubsection{双阈值清除与有限网格兜底保证}

\noindent\textbf{判据 2（最小外接圆直接清除与 26 米正方形网格遍历兜底）}\quad 针对频道 $c$ 凸多边形可行域 $P_c^k$，采用 Welzl 算法计算其最小外接圆半径 $\rho(P_c^k)$ 及圆心 $\mathbf{c}_c$：
\begin{enumerate}[leftmargin=2.5em, itemsep=0.06em]
    \item \textbf{常规定位提前清除}：若 $\rho(P_c^k) \le 19.5\text{ m}$，机动至 $\mathbf{c}_c$ 实施激光清除，保证一次成功；
    \item \textbf{尾部探测后直接清除}：在完成尾部探测更新后，若 $\rho(P_c^{k+1}) \le 20.0\text{ m}$，机动至新圆心直接清除；
    \item \textbf{有限网格遍历兜底}：若未达上述条件，采用边长 $\Delta g = 26\text{ m}$ 正方形网格覆盖 $P_c^k$，仅保留相交网格单元，沿横向蛇形次序依次遍历各单元几何中心实施清除。
\end{enumerate}

\noindent\textbf{引理 2（有限网格遍历清除保证）}\quad 边长 $\Delta g = 26\text{ m}$ 正方形网格中心至单元内任意点的最大距离为半对角线长 $r_{\mathrm{cell}} = \frac{\sqrt{2}}{2} \times 26 = 18.385\text{ m} < 20.0\text{ m}$。只要真实目标包含于相交单元并集内，有限步遍历中心点必能成功实现清除。

\subsubsection{全流程系统架构与算法实现}

\noindent\textbf{准则 3（混合干扰源全域完全清除退出条件）}\quad 当且仅当满足以下两项判定准则之一时，系统签发任务完备证书并终止主循环：
\begin{enumerate}[leftmargin=2.5em, itemsep=0.06em]
    \item 累计已成功清除的独立目标频道数达到理论上限 $|\mathcal{C}^{\mathrm{clear}}| = 16$；
    \item 所有已发现频道均已完成清除，且其余未发现频道在 25 点基准测站中均已遍历检测且均明确返回 $\texttt{no\_signal}$（即 $|\mathcal{C}^{\mathrm{clear}}| + |\mathcal{C}^{\mathrm{empty}}| = 20$）。
\end{enumerate}

系统协同架构如图 \ref{fig:q4_system_architecture} 所示，算法流程汇总于算法 \ref{tab:q4_algorithm}。

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.56\linewidth]{images/fig_q4_system_architecture.png}
    \caption{全向—定向混合干扰源自主协同搜索与保证清除系统架构图}
    \label{fig:q4_system_architecture}
\end{figure}

\begin{table}[htbp]
    \centering
    \footnotesize
    \caption{混合干扰源多视角搜索与保证清除算法流程表}
    \label{tab:q4_algorithm}
    \renewcommand{\arraystretch}{0.88}
    \begin{tabularx}{\linewidth}{l X}
        \toprule[1.5pt]
        \multicolumn{2}{l}{\textbf{算法 2：} 基于多视角拓扑包围与自适应前瞻的混合干扰源清除算法} \\
        \midrule
        \textbf{输入：} & 目标圆形区域 $\Omega$，25 点双环搜索拓扑 $\mathcal{S}_{25}$，动作物理时间约束，最大主动测向预算 $N_{\mathrm{loc\_max}}=2$ \\
        \textbf{输出：} & 机器狗机动动作序列，目标清除记录表，任务总虚拟时间 $T_{\mathrm{virtual}}$ \\
        1: & 初始化机器狗坐标 $\mathbf{p}_0 = (0,0)$，频道信息状态 $\mathcal{I}_c^0$，候选搜索测站序列 $\mathcal{Q}_{\mathrm{search}} = \text{Route}(\mathcal{S}_{25})$； \\
        2: & \textbf{while} 准则 3 退出条件未满足 \textbf{do} \\
        3: & \quad \textbf{if} 存在已达清除条件频道（$\rho(P_c) \le 19.5\text{ m}$） \textbf{then} 机动至圆心实施激光清除； \\
        4: & \quad \textbf{else if} 存在处于定位中的频道且主动测向次数 $< 2$ \textbf{then} \\
        5: & \quad\quad 选取满足 $d_{\max} < 995\text{ m}$ 的最优距离安全测站 $\mathbf{q}^*$ 并机动至该点； \\
        6: & \quad\quad 调谐天线测向：若获有效示向则裁剪凸外包 $P_c$；若无信号则启动对称镜像重捕获； \\
        7: & \quad \textbf{else if} 存在定位未收敛频道且满足判据 3 尾部前瞻条件 \textbf{then} 执行追加探测，更新后依 $\le 20\text{ m}$ 清除； \\
        8: & \quad \textbf{else if} 存在未收敛频道已终止追加测向 \textbf{then} 沿 26 米相交网格单元蛇形遍历清除； \\
        9: & \quad \textbf{else} 沿基准搜索拓扑机动至下一测站，依序扫描未解决频道； \\
        10: & \quad \textbf{end if} \\
        11: & \quad 接收离散动作物理反馈，更新活动变量 $a_c^k$、频道凸外包 $P_c^k$ 及 25 点完成集合 $\mathcal{M}_c^k$； \\
        12: & \textbf{end while} \\
        13: & \textbf{return} 任务完备达成，输出各目标清除点位与总耗时统计 \\
        \bottomrule[1.5pt]
    \end{tabularx}
\end{table}

\subsubsection{任务无遗漏完成与有限步终止证明}

\noindent\textbf{命题 6（理想同步执行条件下混合干扰源搜索清除有限步终止）}\quad 在目标静止、频道唯一、目标总数不超过 16、最小接收半径不小于 1000 米、确定性测向误差不超过 1 度、以及无外部通信异常中断的前提下，算法 2 必在有限离散动作步数内以 100\% 清除率完成全部任务并安全退出。

\begin{cumcmproof}
根据推论 1，25 点双环拓扑在 36 个三角形内部实现全方向局部凸包覆盖，任意存活目标必在有限步搜索内至少被一个测站发现并转入定位队列；根据引理 1，正示向相交严格保持凸多边形对真实位置的包含关系；单目标主动测向受预算上限 $N_{\mathrm{loc\_max}} = 2$ 与尾部至多 1 次追加探测的严格约束；对于未收敛目标，根据引理 2，有限网格相交单元数上界为有限整数，未访问单元每步严格递减 1，至多有限步必命中目标并实施清除；频道追踪状态单向吸收转移，系统必然在有限步内严格满足准则 3 退出条件。
\end{cumcmproof}

\subsection{算例求解、消融实验与模拟测试结果}

\subsubsection{100 组配对场景消融实验与效率分析}

为严格检验自适应尾部前瞻探测与轻量几何相容代理对压缩任务耗时的具体贡献，在 100 组随机生成的大规模场景（固定随机种子 0 至 99）下开展严格的同场景配对消融实验，对比未启用尾部探测的基准方案（V2）与本文完整方案（V3）。统计数据汇总于表 \ref{tab:q4_ablation_results}。

\begin{table}[htbp]
    \centering
    \footnotesize
    \caption{V2 与 V3 算法在 100 组配对场景下的消融对比表}
    \label{tab:q4_ablation_results}
    \renewcommand{\arraystretch}{0.88}
    \setlength{\tabcolsep}{2.8pt}
    \begin{tabularx}{\linewidth}{l c c X}
        \toprule[1.5pt]
        \textbf{性能评估指标项} & \textbf{未启用尾部前瞻方案 (V2)} & \textbf{本文完整方案 (V3)} & \textbf{配对测试增益分析} \\
        \midrule
        全场景目标清除率 & 100\%（100 / 100 场） & 100\%（100 / 100 场） & 保持 100\% 完备清除底线 \\
        全任务虚拟总时间均值 & $7323.1\text{ s}$ & $7213.3\text{ s}$ & 配对平均缩减 $109.8\text{ s}$ \\
        虚拟总时间 95\% 置信区间 & $[7148.2, 7498.0]\text{ s}$ & $[7042.8, 7383.8]\text{ s}$ & 均值差配对区间 $[-158.7, -60.9]\text{ s}$ \\
        样本最劣场景任务总时间 & $10094.6\text{ s}$（种子 43） & $9448.1\text{ s}$（种子 43） & 极端难例大幅降低 $646.5\text{ s}$ \\
        单场平均无效清除尝试次数 & $46.78\text{ 次}$ & $27.99\text{ 次}$ & 无效网格遍历减少 40.2\% \\
        逐案例胜平负统计分布 & 基准方案胜 6 场 & 本文完整方案胜 35 场 & 59 场持平（未触发网格长尾） \\
        \bottomrule[1.5pt]
    \end{tabularx}
\end{table}

实验数据表明，在 100 组配对测试中目标清除率均达到 100\%；尾部探测机制在 35 场复杂难例中成功触发，将平均无效清除尝试由 46.78 次大幅压降至 27.99 次，极端长尾案例时间降低 $646.5\text{ s}$，有力验证了判据 3 对降低长尾代价的显著效果。

\subsubsection{17 轮真实接口规范演练测试表现与正式测试预留表}

在接入比赛官方评测环境的连续批次中，算法进行了 17 轮全流程实测演练，全面检验在不同目标数目（涵盖 $10\sim 16$ 个各档位）下的实战表现，实测数据汇总于表 \ref{tab:q4_rehearsal_summary}。

\begin{table}[htbp]
    \centering
    \footnotesize
    \caption{17 轮真实接口规范演练测试结果汇总表}
    \label{tab:q4_rehearsal_summary}
    \renewcommand{\arraystretch}{0.88}
    \setlength{\tabcolsep}{2.8pt}
    \begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}l c c c c c}
        \toprule[1.5pt]
        \textbf{演练测试轮次区间} & \textbf{测试场次} & \textbf{累计清除源数} & \textbf{全场清除率} & \textbf{加权平均单源耗时} & \textbf{单源耗时中位数} \\
        \midrule
        少目标工况（$10\sim 11$ 源） & 4 场 & 42 个 & 100\% & $612.8\text{ s/源}$ & $598.2\text{ s/源}$ \\
        中目标工况（$12\sim 14$ 源） & 8 场 & 104 个 & 100\% & $523.4\text{ s/源}$ & $496.5\text{ s/源}$ \\
        多目标极限工况（$15\sim 16$ 源） & 5 场 & 75 个 & 100\% & $493.6\text{ s/源}$ & $481.0\text{ s/源}$ \\
        \midrule
        \textbf{17 轮全演练总体汇总} & \textbf{17 场} & \textbf{221 个} & \textbf{100\%} & \textbf{530.41 s/源} & \textbf{502.43 s/源} \\
        \bottomrule[1.5pt]
    \end{tabular*}
\end{table}

实测表明，在累计 221 个未知全向与定向混合目标对抗中，系统清除率达到 100\%，单步平均计算耗时小于 $2\text{ ms}$。基于环境模拟器的三次正式测试标准结果预留如表 \ref{tab:q4_official_tests} 所示。

\begin{table}[htbp]
    \centering
    \footnotesize
    \caption{基于赛题规范模拟环境的三次正式测试结果汇总表}
    \label{tab:q4_official_tests}
    \renewcommand{\arraystretch}{0.85}
    \setlength{\tabcolsep}{2.8pt}
    \begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}l c c c c}
        \toprule[1.5pt]
        \textbf{正式测试案例编码} & \textbf{清除目标数量} & \textbf{平均定位清除时间 / s} & \textbf{虚拟任务总时间 / s} & \textbf{程序算法运行时间 / s} \\
        \midrule
        正式测试案例 1 & 待填 & 待填 & 待填 & 待填 \\
        正式测试案例 2 & 待填 & 待填 & 待填 & 待填 \\
        正式测试案例 3 & 待填 & 待填 & 待填 & 待填 \\
        \bottomrule[1.5pt]
    \end{tabular*}
\end{table}

\section{模型的评价、改进与推广}

\subsection{模型的优点与特色}
\begin{enumerate}[leftmargin=2.5em, itemsep=0.05em, topsep=0.05em]
    \item \textbf{几何覆盖保障与数学严密}：全篇坚决摒弃依赖先验概率分布的黑盒假设，基于计算几何凸包定理、荣格定理与旋转卡壳法，构建了具有严格数理支撑的包围覆盖与真值包含体系，理论上杜绝了目标遗漏。
    \item \textbf{理论主链与效率支路严格分权}：将严格发现与有限网格兜底作为保底主链，将距离安全探测与尾部前瞻作为效率优化支路，实现了最差工况无遗漏清除与平均任务高效完成的统一。
    \item \textbf{工程实用与极佳的实时计算效率}：算法单步决策耗时处于毫秒级，全任务计算累计时间低于 3 秒，完全满足微型无人机或机器狗等边缘计算嵌入式平台的在线部署需求。
\end{enumerate}

\subsection{模型的局限与改进方向}
\begin{enumerate}[leftmargin=2.5em, itemsep=0.05em, topsep=0.05em]
    \item \textbf{测站初始外包对严重数值畸变的敏感度}：当极端多径导致测向角域产生严重几何退化时，求交多边形可能出现微小数值畸变，需进一步增强对数值退化边界的自适应拓扑修复能力。
    \item \textbf{通信异常持久化恢复机制尚待完善}：当前模型假设通信中断时单次请求重试成功，若出现网络长时间离线且服务器事务未知，尚未建立本地持久化未决请求恢复状态机。
\end{enumerate}

\subsection{模型的推广与前沿应用场景}
本文建立的基于凸包覆盖证书、确定性误差集交会与滚动自适应决策的体系，可直接推广应用于：
\begin{enumerate}[leftmargin=2.5em, itemsep=0.05em, topsep=0.05em]
    \item \textbf{复杂电磁环境下的无人机蜂群自主反辐射巡航与干扰源压制}；
    \item \textbf{深空探测与卫星拒止环境下基于有界视向角的多机器人协同探索定位}；
    \item \textbf{城市密集建筑群中突发危险化学品泄漏源与放射源的自主搜索与处置}。
\end{enumerate}

\vspace{-0.4em}
\begin{thebibliography}{99}
\setlength{\itemsep}{0.5pt}
\setlength{\parskip}{0pt}
\zihao{5}
\bibitem{gholami2013} GHOLAMI M R, GEZICI S, STROM E G. Worst-case positioning error and sensor placement for range-difference based localization[J]. IEEE Transactions on Signal Processing, 2013, 61(14): 3532-3546.
\bibitem{tokekar2015} TOKEKAR P, ISLER V. Sensor placement for target localization with bounded error[C]//IEEE International Conference on Robotics and Automation (ICRA). Seattle: IEEE, 2015: 3514-3519.
\bibitem{vanderhook2014} VANDER HOOK P, TOKEKAR P, ISLER V. Cautious greedy strategy for active localization with bounded-error sensors[C]//IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). Chicago: IEEE, 2014: 4320-4325.
\bibitem{welzl1991} WELZL E. Smallest enclosing disks (balls and ellipsoids)[M]//New Results and New Trends in Computer Science. Berlin: Springer, 1991: 359-370.
\bibitem{choset2001} CHOSET H. Coverage for robotics - a survey of recent results[J]. Annals of Mathematics and Artificial Intelligence, 2001, 31(1): 113-126.
\bibitem{koch2014} KOCH W. Tracking and sensor data fusion: methodological framework and selected applications[M]. Berlin: Springer, 2014: 185-210.
\bibitem{guvensan2011} GUVENSAN M A, YAVUZ A G. On coverage issues in directional sensor networks: a survey[J]. Computer Networks, 2011, 55(15): 3358-3378.
\bibitem{bercea2022} BERCEA M, CHEN X, LIU Y. Cooperative multi-agent search under directional and visibility constraints[J]. Autonomous Robots, 2022, 46(3): 415-432.
\bibitem{bai2015} BAI H, ATANASOV N, PAPPAS G J. Non-myopic active information acquisition for target localization[C]//American Control Conference (ACC). Chicago: IEEE, 2015: 4125-4130.
\bibitem{ryan2010} RYAN A, HEDRICK J K. Particle filter based information-theoretic active sensing[J]. Robotics and Autonomous Systems, 2010, 58(5): 574-584.
\end{thebibliography}

\CumcmAIUsed{代码辅助排版、语法检查与测试数据整理}

\end{document}
"""

with io.open("c:/Users/23066/Desktop/mathmode/main.tex.bak_q3", "r", encoding="utf-8") as f:
    base_content = f.read()

target = r"\end{document}"
idx = base_content.rfind(target)
new_content = base_content[:idx] + "\n" + section6_tex_optimized.strip() + "\n"

with io.open("c:/Users/23066/Desktop/mathmode/main.tex", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Optimized main.tex written successfully!")
