"""Check path legality and the required edge cases against supplied maps."""

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from navigation import neighbors, plan  # noqa: E402


def load(name):
    return json.loads((ROOT / "materials" / f"{name}.json").read_text(encoding="utf-8"))


class NavigationTests(unittest.TestCase):
    def check_path(self, grid, start, goal, result):
        path = result["path"]
        if not result["found"]:
            self.assertEqual(path, [])
            self.assertIsNone(result["steps"])
            return
        self.assertEqual(path[0], list(start))
        self.assertEqual(path[-1], list(goal))
        self.assertEqual(result["steps"], len(path) - 1)
        for x, y in path:
            self.assertTrue(0 <= y < len(grid) and 0 <= x < len(grid[0]))
            self.assertEqual(grid[y][x], 0)
        for before, after in zip(path, path[1:]):
            self.assertEqual(abs(before[0] - after[0]) + abs(before[1] - after[1]), 1)

    def test_four_maps(self):
        expected = {"map_open": 9, "map": 15, "map_blocked": None, "map_same_point": 0}
        for name, steps in expected.items():
            with self.subTest(name=name):
                data = load(name)
                result = plan(data["grid"], tuple(data["start"]), tuple(data["goal"]))
                self.assertEqual(result["steps"], steps)
                self.check_path(data["grid"], data["start"], data["goal"], result)

    def test_neighbors_respect_xy_and_walls(self):
        grid = [[0, 1, 0], [0, 0, 0]]
        self.assertEqual(set(neighbors(grid, (0, 0))), {(0, 1)})

    def test_accumulated_updates(self):
        data = load("map")
        updates = load("updates")
        grid = [row.copy() for row in data["grid"]]
        for event, expected_steps in zip(updates["updates"], (19, None)):
            for x, y in event["add_obstacles"]:
                grid[y][x] = 1
            result = plan(grid, tuple(event["current"]), tuple(data["goal"]))
            self.assertEqual(result["steps"], expected_steps)
            self.check_path(grid, event["current"], data["goal"], result)
        self.assertEqual(data["grid"][4][5], 0)


if __name__ == "__main__":
    unittest.main()
