# B 题 Q1 工作入口

Q1 已完成问题理解、数学模型、求解方法和第一版代码验证。当前实现面向题目定义的角度交会定位多边形，不加入接收距离、目标圆域、近场排除区域或人工边界框。

| 内容 | 权威文件 | 当前状态 |
|---|---|---|
| 题意判断与模型边界 | [`RESEARCH.md`](RESEARCH.md) | 已确认 |
| 数学模型与判定命题 | [`MODEL.md`](MODEL.md) | 已确认 |
| 正式算法与验证要求 | [`METHOD.md`](METHOD.md) | 已确认 |
| Python 实现与命令 | [`code/README.md`](code/README.md) | 第一版已验证 |
| 实际验证证据 | [`RESULTS.md`](RESULTS.md) | 固定种子验证通过 |
| 结构化验证摘要 | [`results/q1_verification.json`](results/q1_verification.json) | 当前正式摘要 |
| 图表任务、图注与复现 | [`FIGURES.md`](FIGURES.md) | 两张图已生成并检查 |

当前没有官方固定数值实例，因此已保存的是算法正确性、差分一致性和性质测试证据，不是某一组官方数据的数值答案。最终图见 [`output/figures/`](output/figures/)。
