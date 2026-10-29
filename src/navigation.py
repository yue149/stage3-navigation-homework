"""Grid-map drawing, breadth-first search, shortest paths, and replanning."""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "materials"
OUTPUTS = ROOT / "outputs"
MAP_NAMES = ("map_open", "map", "map_blocked", "map_same_point")
Point = tuple[int, int]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def neighbors(grid: list[list[int]], point: Point):
    """Yield in-bounds, obstacle-free four-connected neighbors."""
    x, y = point
    height, width = len(grid), len(grid[0])
    for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0:
            yield nx, ny


def bfs(grid: list[list[int]], start: Point, goal: Point, *, explore_all: bool = False):
    """Return visited cells and predecessors; a queue gives shortest unit-cost routes."""
    queue = deque([start])
    predecessors: dict[Point, Point | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal and not explore_all:
            break
        for nxt in neighbors(grid, current):
            if nxt not in predecessors:
                predecessors[nxt] = current
                queue.append(nxt)
    return predecessors


def plan(grid: list[list[int]], start: Point, goal: Point) -> dict:
    """Reconstruct a shortest path from BFS predecessors, or report no route."""
    predecessors = bfs(grid, start, goal)
    if goal not in predecessors:
        return {"found": False, "path": [], "steps": None}
    path: list[Point] = []
    point: Point | None = goal
    while point is not None:
        path.append(point)
        point = predecessors[point]
    path.reverse()
    return {"found": True, "path": [list(p) for p in path], "steps": len(path) - 1}


def draw_map(
    grid: list[list[int]], start: Point, goal: Point, output: Path,
    *, visited=(), path=(), title: str = "Grid map",
) -> None:
    """Draw grid[y][x] with x rightward and y downward."""
    cell, left, top = 46, 62, 66
    height, width = len(grid), len(grid[0])
    image = Image.new("RGB", (left + width * cell + 28, top + height * cell + 28), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((left, 16), title, fill="#17212b", font=font)
    draw.text((left, 39), "x ->", fill="#17212b", font=font)
    draw.text((9, top), "y", fill="#17212b", font=font)
    draw.text((9, top + 15), "v", fill="#17212b", font=font)
    visited_set = set(map(tuple, visited))
    path_set = set(map(tuple, path))
    for y, row in enumerate(grid):
        draw.text((32, top + y * cell + 17), str(y), fill="#465366", font=font)
        for x, value in enumerate(row):
            if y == 0:
                draw.text((left + x * cell + 18, 51), str(x), fill="#465366", font=font)
            point = (x, y)
            color = "#344054" if value else "#f8fafc"
            if point in visited_set and not value:
                color = "#a9dcf0"
            if point in path_set and not value:
                color = "#f9c66b"
            x0, y0 = left + x * cell, top + y * cell
            draw.rectangle((x0, y0, x0 + cell - 1, y0 + cell - 1),
                           fill=color, outline="#c5cdd7", width=1)
    if len(path) > 1:
        centers = [(left + x * cell + cell // 2, top + y * cell + cell // 2)
                   for x, y in path]
        draw.line(centers, fill="#e07a19", width=5, joint="curve")
    for point, label, color in ((start, "S", "#117d4f"), (goal, "G", "#ad2747")):
        x, y = point
        x0, y0 = left + x * cell, top + y * cell
        draw.ellipse((x0 + 9, y0 + 9, x0 + cell - 10, y0 + cell - 10), fill=color)
        draw.text((x0 + 19, y0 + 17), label, fill="white", font=font)
    if start == goal:
        x, y = start
        draw.text((left + x * cell + 4, top + y * cell + 3), "S=G", fill="#17212b", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def map_data(path: Path):
    data = read_json(path)
    return data["grid"], tuple(data["start"]), tuple(data["goal"])


def run_question(question: int, input_path: Path | None = None) -> None:
    if question == 1:
        paths = [input_path] if input_path else [MATERIALS / f"{name}.json" for name in ("map_open", "map")]
        for source in paths:
            grid, start, goal = map_data(source)
            print(f"{source.name}: width={len(grid[0])}, height={len(grid)}, start={list(start)}, goal={list(goal)}")
            draw_map(grid, start, goal, OUTPUTS / "q1" / f"{source.stem}.png", title=source.stem)
    elif question == 2:
        paths = [input_path] if input_path else [MATERIALS / f"{name}.json" for name in ("map", "map_blocked")]
        for source in paths:
            grid, start, goal = map_data(source)
            visited = bfs(grid, start, goal, explore_all=True)
            reachable = goal in visited
            save_json(OUTPUTS / "q2" / f"{source.stem}.json", {"reachable": reachable})
            draw_map(grid, start, goal, OUTPUTS / "q2" / f"{source.stem}.png",
                     visited=visited, title=f"{source.stem}: reachable={reachable}")
            print(f"{source.stem}: reachable={reachable}, visited={len(visited)}")
    elif question in (3, 4):
        names = ("map", "map_blocked") if question == 3 else MAP_NAMES
        paths = [input_path] if input_path else [MATERIALS / f"{name}.json" for name in names]
        for source in paths:
            grid, start, goal = map_data(source)
            result = plan(grid, start, goal)
            folder = OUTPUTS / f"q{question}"
            save_json(folder / f"{source.stem}.json", result)
            draw_map(grid, start, goal, folder / f"{source.stem}.png",
                     path=result["path"], title=f"{source.stem}: steps={result['steps']}")
            print(f"{source.stem}: found={result['found']}, steps={result['steps']}")
    elif question == 5:
        updates = read_json(MATERIALS / "updates.json")
        base = MATERIALS / updates["base_map"]
        grid, _, goal = map_data(base)
        grid = [row.copy() for row in grid]
        results = []
        for event in updates["updates"]:
            for x, y in event["add_obstacles"]:
                grid[y][x] = 1
            start = tuple(event["current"])
            result = plan(grid, start, goal)
            results.append({"id": event["id"], **result})
            draw_map(grid, start, goal, OUTPUTS / "q5" / f"update_{event['id']}.png",
                     path=result["path"], title=f"update {event['id']}: steps={result['steps']}")
            print(f"update {event['id']}: current={list(start)}, found={result['found']}, steps={result['steps']}")
        save_json(OUTPUTS / "q5" / "replans.json", results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the navigation homework questions.")
    parser.add_argument("--question", type=int, choices=range(1, 6),
                        help="Question 1-5; omit to generate all required outputs")
    parser.add_argument("--input", type=Path, help="Alternate map JSON for questions 1-4")
    args = parser.parse_args()
    if args.input and args.question not in (1, 2, 3, 4):
        parser.error("--input requires --question 1, 2, 3, or 4")
    for question in ([args.question] if args.question else range(1, 6)):
        run_question(question, args.input)


if __name__ == "__main__":
    main()
