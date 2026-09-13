from __future__ import annotations

import unittest

from radio_sim.domain.models import Position
from radio_sim.environment.local import LocalEnvironment


class ReproducibilityTests(unittest.TestCase):
    def test_from_seed_repeats_public_observations(self) -> None:
        def observe() -> list[tuple[str, float | None]]:
            env = LocalEnvironment.from_seed(seed=2468, problem="Q4")
            env.enter()
            observations = []
            for channel in range(1, 21):
                result = env.measure(Position(0, 0), channel)
                observations.append((result.status.value, result.angle_deg))
            env.exit()
            return observations

        self.assertEqual(observe(), observe())


if __name__ == "__main__":
    unittest.main()
