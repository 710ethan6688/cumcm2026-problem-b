# Q4 code

本目录存放问题 4 的本地搜索、定位和清除策略。

正式采用版本为A0（V3），即默认参数运行。A1、A2相关开关仅为消融复现入口，默认关闭，不属于当前论文主算法。

- `q4_strategy.py`：25 点方向完备搜索、逐频道不存在认证、盲区失联后的镜像重捕获、高置信度自适应尾部探测，以及只扫描相交单元的有限清除网格。
- `run_q4.py`：单个本地随机种子入口。
- `run_q4_batch.py`：批量本地随机种子入口。
- `run_q4_official.py`：复用共享 HTTP 适配器连接官方模拟器，并保存逐请求 JSONL 与运行摘要 JSON。
- `tests/`：搜索骨架、Q3 反例、逐频道认证和清除回退测试。


在本目录运行：

```powershell
python run_q4.py --seed 12345
python run_q4_batch.py --start-seed 0 --count 10
python run_q4_batch.py --start-seed 0 --count 10 --no-adaptive-tail-probe
python -m unittest discover -s tests -v
python run_q4_official.py --robot-id <参赛队号>
```

结果默认写入 `../results/`。文件名包含精确到微秒的时间戳，不使用 UUID，也不会覆盖已有结果。本地入口使用 `--no-write` 可以只打印结果。

自适应尾部探测默认启用；带 `--no-adaptive-tail-probe` 的批量命令关闭该模块，用于生成同种子基线。方向感知网格仍为实验开关，默认关闭。

实验复现时，`--analytic-clear-terminal` 启用A1双清除终端；`--tail-terminal-linkage` 启用A2，并自动同时启用A1。A2只把尾部探测的兜底成本替换为两个认证终端中的较低值，不改变最终覆盖保证和原网格回退。两项升级均已验证但未被正式采用，结果见 `../EXPERIMENT_RESULTS.md`。

官方入口默认连接 `http://127.0.0.1:2026`。运行前请在官方模拟器中选择并启动问题 4；真实连接命令由参赛者执行。`q4_official_*.jsonl` 保留每次 HTTP 尝试，可用于后续分解移动、测量、换频和清除耗时。
