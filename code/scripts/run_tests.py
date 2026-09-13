"""在不依赖外部测试框架的情况下运行模拟器测试套件。"""

from __future__ import annotations

import unittest


def main() -> None:
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
