# Q1 论文正文与代码一致性联合审查简报（致 Codex）

> **【Token 限额硬性约束与阅读指引】**
> 1. **严禁读取 PDF 或大型图像**：所有审查内容均已转为纯文本 Markdown，请直接阅读同目录下的 [`Q1_paper_section.md`](Q1_paper_section.md)！
> 2. **严格控制 Token 消耗**：请务必保留 5 小时限额的 **20% 以上** Token 配额，尽量精炼输出审查要点，无需冗长客套。
> 3. **核心任务**：对齐模型与代码（`q1_geometry.py`），核验数据表与结论严谨性，给出最终是否达到冻结标准的决议。

---

## 一、审查标的与代码对应文件

- **Q1 正文 Markdown**：`contest/2026mcm/paper/Q1_paper_section.md`
- **底层算法实现**：`contest/2026mcm/q1/code/q1_geometry.py`
- **基准算例真实输出**：`contest/2026mcm/q1/results/q1_example_result.json`
- **千例验证统计**：`contest/2026mcm/q1/results/q1_verification.json`
- **单元与属性测试**：`contest/2026mcm/q1/code/tests/test_q1_geometry.py`（15 个测试全部通过）

---

## 二、Gemini / Antigravity 预审结论汇总

经逐行核对正文与底层代码，我们提取了以下对齐细节供你快速复核：

### 1. 模型范围界定（Model Scope）
- **正文表述**（第 2 节）：明确指出定位区域 $\mathcal{R}$ 为纯角度交会凸多边形；题设覆盖半径（$1000\sim 1500\text{ m}$）、近场 5 米盲区与 1800 米边界属于上游观测激发条件，不作为几何圆弧截断 $\mathcal{R}$。
- **代码对齐**：`q1_geometry.py` 严格遵循该范围（见 docstring 第 9–11 行：“The implementation deliberately does not add a range disk, the 1800 m target disk, a near-field exclusion disk, or a bounding box”），二者完全一致。

### 2. 向量半平面与误差角域定义
- **正文公式**：
  $$
  \mathbf{u}_i^- = [\cos(\hat\theta_i - \varepsilon), \sin(\hat\theta_i - \varepsilon)]^\top, \quad
  \mathbf{u}_i^+ = [\cos(\hat\theta_i + \varepsilon), \sin(\hat\theta_i + \varepsilon)]^\top
  $$
  $$
  \mathcal{W}_i = \left\{ \mathbf{x} \in \mathbb{R}^2 : \det(\mathbf{u}_i^-, \mathbf{x}-\mathbf{p}_i) \ge 0, \quad \det(\mathbf{x}-\mathbf{p}_i, \mathbf{u}_i^+) \ge 0 \right\}
  $$
- **代码对齐**：`bearing_halfplanes()` 生成 `make_halfplane(q, lower)` 与 `make_halfplane(q, -upper)`，半平面判据为 $\text{cross}(d, x - q) \ge 0$。经展开，下界为 $\det(\mathbf{u}_i^-, \mathbf{x}-\mathbf{p}_i) \ge 0$，上界为 $\det(-\mathbf{u}_i^+, \mathbf{x}-\mathbf{p}_i) \ge 0 \iff \det(\mathbf{x}-\mathbf{p}_i, \mathbf{u}_i^+) \ge 0$，数学等价性严格成立。

### 3. 直径定理与算法复杂度
- **正文定理 1**：凸多边形直径必在极点对处取得（附范数三角不等式与凸组合展开证明）。
- **算法对齐**：旋转卡壳 $O(h)$，双端队列半平面交 $O(n\log n)$，与暴力对照算法 $O(h^2)$ 和 $O(n^3)$ 一致。

### 4. 直径圆盘覆盖判定与反例
- **代数检验式**：$(\mathbf{x} - \mathbf{a}^*) \cdot (\mathbf{x} - \mathbf{b}^*) \le 0 \iff \|\mathbf{x} - \mathbf{c}^*\|_2^2 \le D^2/4$。
- **理论反例**：边长为 $D$ 的正三角形，其中心高 $h = \frac{\sqrt{3}}{2}D \approx 0.8660D > 0.5D$；并引用荣格定理（$R_{\min} \le \frac{\sqrt{3}}{3}D \approx 0.5774D$），逻辑严密。
- **代码对齐**：`coverage_by_dot_product()` 与 `coverage_by_center_distance()` 判定完全一致。

### 5. 基准算例（表 2）数值完全核准
- 4 观测站对称工况（$(1000,0), (0,1000), (-1000,0), (0,-1000)$）：
  - 极点数 $h = 8$
  - 覆盖面积 $S = 1197.81\text{ m}^2$（归一化面积 $0.0011978093 \times 1000^2$）
  - 几何直径 $D = 48.523\text{ m}$（精确值 $48.5234000095\text{ m}$）
  - 直径圆盘圆心 $\mathbf{c}^* = (0, 0)\text{ m}$，半径 $R = 24.262\text{ m}$
  - 最大点积违规量 $g_{\text{viol}} = 9.64 \times 10^{-12}\text{ m}^2$
  - 判定结果 $\kappa = \text{True}$
  - **全部数值与 `q1_example_result.json` 严格吻合！**

### 6. 大规模复核统计（表 3）与蒙特卡洛分析完全核准
- 1000 组随机算例（种子 `20260911`）：
  - 覆盖率：347 例完全覆盖（$34.7\%$），653 例外突未覆盖（$65.3\%$）
  - 乱序不变性：1000 次 $\Delta D = 0.0\text{ m}$
  - 冗余约束幂等：1000 次通过
  - 刚体空间变换：100 次通过
  - 单调性检验：8443 次逐步增约束全部通过
  - 耗时：1000 例全套复核总耗时 4.64 s（单例 4.64 ms）
  - **全部数值与 `q1_verification.json` 严格吻合！**

---

## 三、待讨论或微调的小项（供 Codex 确认）

1. **表 3 题注字样**：
   - 当前 LaTeX 源码中写为 `\caption{主算与复核对照及大规模检验统计表}`，漏掉了“法”字（变成了“主算”）。
   - 建议微调为：`\caption{主算法与复核对照及大规模检验统计表}`。
2. **退化状态输出声明**：
   - 正文 6.4 节列出了 `EMPTY`, `UNBOUNDED`, `DEGENERATE`, `NUMERICALLY_UNCERTAIN`，与代码中 `RegionStatus` 枚举命名严格对应。

---

## 四、请 Codex 协助确认的事项

1. 是否认可上述 Q1 正文在模型、公式、证明、算例数值、统计指标上与代码的全面一致性？
2. 除了表 3 题注的“主算”微调外，是否还有其他潜在学术表述或逻辑漏洞需要修订？
3. 若无异议，是否同意将 Q1 正文同步正式冻结？
