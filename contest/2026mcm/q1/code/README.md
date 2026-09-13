# Q1 几何定位实现

本目录实现 `MODEL.md` 与 `METHOD.md` 确认的 Q1 主链：示向角域半平面交、凸多边形直径及直径圆盘覆盖判定。正式顶点算法为角度排序双端队列半平面交，开发验证同时运行两两边界交点枚举；正式直径算法为旋转卡壳，验证使用全顶点对穷举。

核心求解与验证实现只使用 Python 标准库，不加入接收圆、目标圆域、近场排除区域或人工边界框。绘图脚本单独使用 Conda 环境 `mcm-2026` 中的 NumPy、Matplotlib 和 UltraPlot。

## 运行示例

在本目录执行：

```powershell
python run_q1.py
```

自定义输入采用 UTF-8 JSON：

```json
{
  "observations": [
    {"x": 1000.0, "y": 0.0, "bearing_deg": 180.0},
    {"x": 0.0, "y": 1000.0, "bearing_deg": 270.0},
    {"x": -1000.0, "y": 0.0, "bearing_deg": 0.0}
  ]
}
```

运行命令：

```powershell
python run_q1.py --input observations.json --output result.json
```

非 `VALID` 状态返回退出码 2，且不会伪装输出普通直径或覆盖结论。

## 验证

```powershell
python -m unittest discover -s tests -v
python verify_q1.py --random-cases 1000 --seed 20260911
```

第二条命令执行固定随机种子的主线/复核线差分、观测顺序、重复约束、增加约束、刚体变换和容差敏感性检查，并将结构化摘要写入 `../results/q1_verification.json`。

## 图表复现

在本目录执行：

```powershell
conda run -n mcm-2026 python -B prepare_q1_figure_data.py
conda run -n mcm-2026 python -B plot_q1_validation.py
npx --yes --package @mermaid-js/mermaid-cli@11.12.0 mmdc -i q1_algorithm_flow.mmd -o ../output/figures/q1_algorithm_flow.png -w 3200 -H 1800 -b white -s 2
```

前两条命令分别重建 1000 例绘图用派生数据和 UltraPlot 验证图；第三条命令从 Mermaid 源文件重建算法流程图。图表主张、图注和使用边界见 [`../FIGURES.md`](../FIGURES.md)。
