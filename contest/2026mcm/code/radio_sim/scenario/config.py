"""本地场景生成配置。

凡题目未说明其概率分布的默认参数，均在下方明确标记为仿真假设。
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from radio_sim.domain.models import ProblemType


@dataclass(frozen=True, slots=True)
class ScenarioConfig:
    problem: ProblemType = ProblemType.Q3
    mode: str = "normal"

    # 题目事实：允许范围与几何参数。
    source_count_min: int = 10
    source_count_max: int = 16
    channel_min: int = 1
    channel_max: int = 20
    arena_radius_m: float = 1800.0
    receive_radius_min_m: float = 1000.0
    receive_radius_max_m: float = 1500.0

    # 仿真假设：
    # - 干扰源数量在给定整数范围内服从离散均匀分布；
    # - 信道采用均匀无放回抽样；
    # - 位置在圆盘内按面积均匀分布；
    # - 接收半径在给定区间内服从连续均匀分布；
    # - Q4 定向源数量在 1..(n-1) 上服从离散均匀分布；
    # - 定向源朝向在 [0, 360) 上服从连续均匀分布。
    source_count_distribution: str = "discrete_uniform"
    channel_distribution: str = "uniform_without_replacement"
    position_distribution: str = "uniform_disk_area"
    receive_radius_distribution: str = "continuous_uniform"
    q4_directional_count_distribution: str = "discrete_uniform_nonempty_mix"
    direction_distribution: str = "continuous_uniform"

    def __post_init__(self) -> None:
        object.__setattr__(self, "problem", ProblemType.coerce(self.problem))
        if self.mode != "normal":
            raise ValueError("only scenario mode 'normal' is implemented")
        if not 1 <= self.source_count_min <= self.source_count_max <= 20:
            raise ValueError("source count range must satisfy 1 <= min <= max <= 20")
        if not 1 <= self.channel_min <= self.channel_max <= 20:
            raise ValueError("channel range must lie within 1..20")
        channel_slots = self.channel_max - self.channel_min + 1
        if self.source_count_max > channel_slots:
            raise ValueError("source count exceeds available unique channels")
        if self.arena_radius_m <= 0:
            raise ValueError("arena_radius_m must be positive")
        if not 0 < self.receive_radius_min_m <= self.receive_radius_max_m:
            raise ValueError("invalid receive radius range")

    @classmethod
    def for_problem(cls, problem: ProblemType | str, **changes: object) -> "ScenarioConfig":
        return cls(problem=ProblemType.coerce(problem), **changes)

    def with_problem(self, problem: ProblemType | str) -> "ScenarioConfig":
        return replace(self, problem=ProblemType.coerce(problem))
