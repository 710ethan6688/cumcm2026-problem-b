# 问题 3 和问题 4 本地仿真环境

本目录提供一个轻量、可复现的本地 Monte Carlo 环境，用于开发和比较问题 3、问题 4 的搜索、定位与清除策略。它复现题面中的物理规则、动作语义和虚拟时间，并提供与同一环境协议兼容的官方 HTTP 适配器。

## 架构与依赖方向

```text
ScenarioGenerator -> hidden Scenario -> LocalEnvironment
                                          |
Strategy --------> Environment protocol <-+
    |
    +-- cannot import LocalEnvironment, ScenarioGenerator, or ground truth

Evaluator -> constructs runs and reads aggregate diagnostics
```

主要目录：

- `radio_sim/domain/`：Strategy 可使用的公开数据对象。
- `radio_sim/scenario/`：隐藏场景、生成配置和固定 seed 生成器。
- `radio_sim/environment/`：统一协议、本地环境和未来官方适配器骨架。
- `radio_sim/strategy/`：薄策略协议及只用于环境自检的 SmokeTestStrategy。
- `radio_sim/evaluation/`：单次、批量运行和指标计算。
- `radio_sim/utils/`：几何和稳定的确定性测向误差。
- `tests/`：物理边界、计时、复现性和依赖隔离测试。
- `scripts/`：命令行入口。

Strategy 唯一应依赖的环境类型是 `radio_sim.environment.base.Environment`。`test_dependency_boundaries.py` 会检查策略模块是否错误导入本地环境或场景真值。

## 已实现的题目规则

- 圆形目标区域半径为 1800 米，干扰源位于区域内。
- 每个场景有 10 至 16 个干扰源，频道来自 1 至 20 且互不重复。
- 问题 3 仅有全向源；问题 4 同时包含全向源和定向源。
- 各源有效接收半径在 1000 至 1500 米之间。
- 定向源覆盖其定向方向左右各 90 度，包含边界。
- 示向度采用正东为 0 度、逆时针为正、范围 `[0, 360)` 的约定。
- 示向度误差在 `[-1, 1]` 度，同一场景、频道和坐标重复测量误差不变。
- 示向度返回值保留两位小数。
- 距离超过接收半径、频道不存在、源已清除或定向源未覆盖时，测量返回 `no_signal`。
- 距离不超过 5 米且处于有效覆盖范围时，测量返回 `near`，不返回角度。
- 每次合法测量耗时为移动时间、必要的 1 秒换频时间和 5 秒检测时间之和。
- 合法测量完成后，当前频道更新为测量频道，无论结果类型如何。
- 清除距离不超过 20 米时成功，且不受定向源朝向影响。
- 清除成功耗时为移动时间加 5 秒；失败为移动时间加 3 秒。
- 清除不改变当前测向频道，不产生频道切换时间。
- 同一干扰源只能清除一次。
- 机器狗初始位置为 `(0, 0)`，初始频道为 1；`enter` 和 `exit` 不增加虚拟时间。
- 坐标分量必须有限且绝对值不超过 2,000,000 米。
- 虚拟时间默认上限为 360,000 秒；已开始的动作先完成，之后环境结束。

## Simulation assumptions

以下概率分布不是题目或附件公布的官方场景生成规律，只用于本地 Monte Carlo 实验：

- 干扰源总数在 10 至 16 的整数中离散均匀抽取。
- 频道从 1 至 20 中均匀无放回抽取。
- 位置按圆盘面积均匀分布，使用 `r = 1800 * sqrt(U)`。
- 有效接收半径服从 `Uniform(1000, 1500)`。
- 问题 4 的定向源数量在 `1..(n-1)` 中离散均匀抽取，以保证两类源都存在。
- 定向源朝向在 `[0, 360)` 上均匀分布。
- 测向误差通过稳定 SHA-256 映射在 `[-1, 1]` 上生成；这只是满足同地点误差固定的本地机制。
- 定向源中心点的极角没有定义。本地环境约定该点处于有效覆盖内，因此测量返回 `near`。

所有这些设置集中在 `ScenarioConfig` 或明确注释的位置。增加 `edge`、`cluster`、`sparse`、`small_receive_radius`、`large_measure_error`、`adversarial` 等模式时，应扩展生成器，不得把随机逻辑写进 `LocalEnvironment`。

## 运行方式

以下命令均从本目录 `contest/2026mcm/code/` 执行，不需要安装第三方依赖。

运行完整测试：

```powershell
python -m scripts.run_tests
```

运行一个固定 seed：

```powershell
python -m scripts.run_single --seed 12345 --problem Q3
python -m scripts.run_single --seed 12345 --problem Q4
```

批量运行：

```powershell
python -m scripts.run_batch --start-seed 0 --count 1000 --problem Q3
```

只有显式提供 `--output` 时批量脚本才写 CSV：

```powershell
python -m scripts.run_batch --start-seed 0 --count 1000 --problem Q3 --output ../q3/output/simulation/baseline.csv
```

## Python 使用示例

```python
from radio_sim.environment.local import LocalEnvironment
from radio_sim.strategy import SmokeTestStrategy

env = LocalEnvironment.from_seed(seed=12345, problem="Q3")
result = SmokeTestStrategy().run(env)
```

批量评价：

```python
from radio_sim.evaluation import run_batch
from radio_sim.strategy import SmokeTestStrategy

results = run_batch(
    strategy=SmokeTestStrategy(),
    seeds=range(1000),
    problem="Q3",
)
```

`SmokeTestStrategy` 只验证动作闭环，不代表问题 3 或问题 4 的最终策略。

## 添加新策略

新策略实现以下接口，并且只导入环境抽象和公开 domain 对象：

```python
from radio_sim.domain.models import StrategyResult
from radio_sim.environment.base import Environment


class NewStrategy:
    def run(self, env: Environment) -> StrategyResult:
        env.enter()
        # 仅通过 env.measure、env.clear 和公开状态决策
        env.exit()
        return StrategyResult(strategy_name=type(self).__name__)
```

正式问题 3、问题 4 策略形成后，其研究、模型、方法和结果分别由 `q3/`、`q4/` 下的正式文档承载；共享仿真核心不因某个策略需要而改变规则。

## 评价指标

评价器记录：

- seed 和问题编号；
- 干扰源总数、成功清除数、清除比例和是否全部清除；
- 总虚拟时间和平均定位清除时间；
- 总移动距离；
- measure、clear、失败 clear 和频道切换次数；
- 策略完成状态和实际 Python 墙钟运行时间。

零清除时，平均定位清除时间记为 `None`，不伪造为 0。

## 尚未实现

- 问题 3、问题 4 的正式搜索与定位算法；
- `normal` 以外的场景生成模式；
- 并行批量运行和参数网格扫描；
- 官方场景分布校准。

`OfficialEnvironment` 负责 HTTP、JSON、幂等重试、现实时间余量和通信日志；Strategy 接口保持不变。
