# Q3 code

本目录存放问题 3 的动态搜索、主动定位与保证清除代码。

- `q3_strategy.py`：七点严格覆盖、滚动任务调度、轻量Q2选点、完整观测账本、认证区域健康状态、结构化完成证书和网格兜底策略。
- `run_q3.py`：单个随机种子入口，默认写入 `../results/`。
- `run_q3_batch.py`：批量随机种子入口，默认写入 `../results/`。
- `run_q3_official.py`：连接官方HTTP模拟器，记录逐请求JSONL，并输出待决请求与完成证书。
- `tests/`：搜索覆盖、严格外包、方向定位、缺席证据、区域降级、近场清除和网格兜底测试。

在本目录运行：

```powershell
python run_q3.py --seed 12345
python run_q3_batch.py --start-seed 0 --count 10
python run_q3_official.py --robot-id <参赛队号>
python -m unittest discover -s tests -v
```

使用 `--no-write` 可以只打印结果而不创建结果文件；默认文件名带微秒级时间戳，不会覆盖已有结果。

官方通信适配器在响应未知时保留原请求及`request_id`并阻断所有新动作；策略只允许重放该请求。无法恢复时结果为`INCOMPLETE`，不会把会话结束冒充完整清除。
