from __future__ import annotations

import ast
import importlib
import unittest
from pathlib import Path

from tests.helpers import make_env


class DependencyBoundaryTests(unittest.TestCase):
    def test_strategy_modules_do_not_import_ground_truth_or_local_env(self) -> None:
        strategy_dir = Path(__file__).parents[1] / "radio_sim" / "strategy"
        forbidden = (
            "radio_sim.environment.local",
            "radio_sim.scenario",
        )
        violations: list[str] = []
        for path in strategy_dir.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                for module in modules:
                    if module.startswith(forbidden):
                        violations.append(f"{path.name}: {module}")
        self.assertEqual(violations, [])

    def test_local_environment_public_surface_contains_no_ground_truth(self) -> None:
        env = make_env()
        public_names = {name for name in dir(env) if not name.startswith('_')}
        allowed = {
            'clear',
            'current_channel',
            'current_position',
            'enter',
            'exit',
            'from_seed',
            'measure',
            'state',
            'virtual_time_s',
        }
        self.assertEqual(public_names, allowed)

    def test_environment_package_does_not_export_local_implementation(self) -> None:
        package = importlib.import_module("radio_sim.environment")
        self.assertFalse(hasattr(package, "LocalEnvironment"))
        self.assertFalse(hasattr(package, "PhysicsConfig"))


if __name__ == "__main__":
    unittest.main()
