from __future__ import annotations

import unittest
from math import hypot

from radio_sim.domain.models import ProblemType
from radio_sim.scenario.config import ScenarioConfig
from radio_sim.scenario.generator import ScenarioGenerator
from radio_sim.scenario.models import SourceType


class ScenarioGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = ScenarioGenerator()

    def test_same_seed_and_config_are_identical(self) -> None:
        config = ScenarioConfig.for_problem("Q3")
        self.assertEqual(
            self.generator.generate(10086, config),
            self.generator.generate(10086, config),
        )

    def test_different_seed_changes_scenario(self) -> None:
        config = ScenarioConfig.for_problem("Q3")
        self.assertNotEqual(
            self.generator.generate(10086, config),
            self.generator.generate(10087, config),
        )

    def test_normal_scenario_obeys_ranges(self) -> None:
        config = ScenarioConfig.for_problem("Q3")
        for seed in range(100):
            scenario = self.generator.generate(seed, config)
            self.assertGreaterEqual(len(scenario.sources), 10)
            self.assertLessEqual(len(scenario.sources), 16)
            channels = [source.channel for source in scenario.sources]
            self.assertEqual(len(channels), len(set(channels)))
            for source in scenario.sources:
                self.assertLessEqual(hypot(source.position.x, source.position.y), 1800.0)
                self.assertGreaterEqual(source.receive_radius_m, 1000.0)
                self.assertLessEqual(source.receive_radius_m, 1500.0)

    def test_q3_has_only_omnidirectional_sources(self) -> None:
        scenario = self.generator.generate(5, ScenarioConfig.for_problem(ProblemType.Q3))
        self.assertTrue(
            all(source.source_type is SourceType.OMNIDIRECTIONAL for source in scenario.sources)
        )

    def test_q4_has_nonempty_mix(self) -> None:
        for seed in range(30):
            scenario = self.generator.generate(seed, ScenarioConfig.for_problem(ProblemType.Q4))
            types = {source.source_type for source in scenario.sources}
            self.assertEqual(types, {SourceType.OMNIDIRECTIONAL, SourceType.DIRECTIONAL})

    def test_unimplemented_mode_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "only scenario mode"):
            ScenarioConfig(mode="edge")


if __name__ == "__main__":
    unittest.main()
