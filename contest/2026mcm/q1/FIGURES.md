# B 题 Q1 图表任务与复现说明

本文件记录 Q1 已完成图表的论文主张、数据来源、生成入口和使用边界。最终图统一保存在 `output/figures/`，不使用示意数据替代正式验证结果。

## 图 Q1-1：角度交会定位、直径圆判定与独立复核流程

- 图型：Mermaid 算法流程图。
- 拟支持的论文主张：正式求解依次完成前向半平面构造、凸多边形求交、旋转卡壳直径计算和直径圆盘覆盖判定；开发与验证模式另用交点枚举、穷举直径和圆心距离式进行独立复核。
- 权威依据：`MODEL.md`、`METHOD.md` 与 `code/q1_geometry.py`。
- 源文件：`code/q1_algorithm_flow.mmd`。
- 最终图：`output/figures/q1_algorithm_flow.png`。
- 生成工具：Mermaid CLI 11.12.0。
- 当前状态：已生成并完成视觉检查。
- 使用边界：独立复核链属于开发与验证模式，不应写成正式快速求解时必然执行的步骤。

建议图注：

> 图 Q1-1 角度交会定位区域、直径圆覆盖判定及独立复核流程。正式主链使用半平面交和旋转卡壳，验证模式以结构不同的参考算法复核顶点、直径和覆盖结论。

## 图 Q1-2：默认实例几何结果与随机验证覆盖余量

- 图型：UltraPlot 双面板定量结果图。
- 面板 a：默认对称实例的定位凸多边形、最远点对及以该点对为直径的圆盘；坐标单位为 m。
- 面板 b：固定种子 `20260911` 下 1000 个合成验证实例的最大相对半径超量，按数值从小到大排列；纵轴单位为 %，零线以下表示覆盖。
- 拟支持的论文主张：默认实例的定位区域被对应直径圆盘覆盖；同一判定程序在 1000 个合成实例中得到 347 个覆盖和 653 个不覆盖样本，并通过主线/复核线一致性检查。
- 原始结构化输入：`results/q1_example_result.json`、`results/q1_verification.json`。
- 绘图用派生数据：`results/q1_validation_cases.csv`。
- 数据生成入口：`code/prepare_q1_figure_data.py`。
- 绘图入口：`code/plot_q1_validation.py`。
- 最终图：`output/figures/q1_validation.png`。
- 生成环境：Conda 环境 `mcm-2026`，UltraPlot 2.5.0，Matplotlib 3.10.9；PNG 以 1000 dpi 导出。
- 当前状态：已生成并完成数据、尺寸与视觉检查。
- 使用边界：347/653 只描述当前合成验证生成器，不是题目真实场景的覆盖概率，也不是论文应外推的统计结论。

建议图注：

> 图 Q1-2 定位区域的直径圆覆盖结果与随机实例验证。（a）默认实例中直径为 48.523 m，直径圆盘覆盖整个定位多边形；（b）固定种子生成的 1000 个合成实例按最大相对半径超量排序，其中 347 个满足覆盖条件、653 个不满足。该比例仅用于展示判定器同时识别正、反实例。

## 复现命令

在 `q1/code/` 下执行：

```powershell
conda run -n mcm-2026 python -B prepare_q1_figure_data.py
conda run -n mcm-2026 python -B plot_q1_validation.py
npx --yes --package @mermaid-js/mermaid-cli@11.12.0 mmdc -i q1_algorithm_flow.mmd -o ../output/figures/q1_algorithm_flow.png -w 3200 -H 1800 -b white -s 2
```
