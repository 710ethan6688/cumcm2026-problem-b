"""可复现的隐藏场景生成器。"""

from __future__ import annotations

from math import cos, pi, sin, sqrt
from random import Random

from radio_sim.domain.models import Position
from radio_sim.scenario.config import ScenarioConfig
from radio_sim.scenario.models import Scenario, Source, SourceType


class ScenarioGenerator:
    def generate(self, seed: int, config: ScenarioConfig) -> Scenario:
        rng = Random(seed)
        source_count = rng.randint(config.source_count_min, config.source_count_max)
        channels = rng.sample(
            range(config.channel_min, config.channel_max + 1),
            source_count,
        )
        source_types = self._source_types(rng, source_count, config)

        sources: list[Source] = []
        for channel, source_type in zip(channels, source_types, strict=True):
            radius = config.arena_radius_m * sqrt(rng.random())
            theta = 2.0 * pi * rng.random()
            position = Position(radius * cos(theta), radius * sin(theta))
            receive_radius = rng.uniform(
                config.receive_radius_min_m,
                config.receive_radius_max_m,
            )
            direction = rng.uniform(0.0, 360.0) if source_type is SourceType.DIRECTIONAL else None
            sources.append(
                Source(
                    channel=channel,
                    position=position,
                    receive_radius_m=receive_radius,
                    source_type=source_type,
                    direction_deg=direction,
                )
            )

        return Scenario(seed=seed, problem=config.problem, sources=tuple(sources))

    @staticmethod
    def _source_types(
        rng: Random,
        source_count: int,
        config: ScenarioConfig,
    ) -> list[SourceType]:
        if config.problem.value == "Q3":
            return [SourceType.OMNIDIRECTIONAL] * source_count

        directional_count = rng.randint(1, source_count - 1)
        result = [SourceType.DIRECTIONAL] * directional_count
        result.extend([SourceType.OMNIDIRECTIONAL] * (source_count - directional_count))
        rng.shuffle(result)
        return result
