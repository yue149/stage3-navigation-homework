# 作业报告

- 姓名：yue149（GitHub 用户名；真实姓名未提供）
- 方向：自主导航与网格路径规划
- 实际使用环境与依赖版本：Windows，Python 3.12.10，Pillow 13.0.0

## 安装和运行

在仓库根目录运行：

```powershell
python -m pip install -r requirements.txt
python src/navigation.py
```

默认按第一问到第五问依次生成 `outputs/q1/` 至 `outputs/q5/` 中的 JSON 和 PNG。也可只运行一问，例如 `python src/navigation.py --question 4`。第一至第四问可以用 `--input` 更换输入地图，例如：

```powershell
python src/navigation.py --question 4 --input materials/map_open.json
```

输出文件名取输入 JSON 的文件名（不带扩展名）。第五问按 `materials/updates.json` 的事件顺序运行，基础地图由该文件的 `base_map` 指定。原始输入文件不会被修改。

## 各问结果

| 题目 | 完成情况与结果路径 | 一句说明或发现的问题 |
| --- | --- | --- |
| 第一问 | `outputs/q1/map_open.png`、`outputs/q1/map.png` | 两图均为宽 12、高 10，起点 `[1,1]`、终点 `[10,1]`；图中 x 向右、y 向下。 |
| 第二问 | `outputs/q2/` 内两组 JSON 和访问区域图 | 主地图可达，访问空地 74 格；无路地图不可达，访问空地 32 格。 |
| 第三问 | `outputs/q3/` 内两组路径 JSON 和图 | 主地图最短路径 15 步；无路地图返回空路径和 `null` 步数。 |
| 第四问 | `outputs/q4/` 内四组路径 JSON 和图 | `map_open`：找到，9 步；`map`：找到，15 步；`map_blocked`：未找到；`map_same_point`：找到，0 步。 |
| 第五问 | `outputs/q5/replans.json` 与 `update_0.png`、`update_1.png` | 事件 0 从当前位置 `[3,3]` 经下方通道到达目标，19 步；事件 1 累积封堵后无路。 |

## 关键概念与局限

- 坐标 `[x,y]` 对应 `grid[y][x]`。合法邻居只允许上下左右移动，同时检查边界与障碍。
- 第二问要记录已访问格子，避免绕圈和重复入队，使搜索能够结束且每个格子最多处理一次。
- 访问区域包括 BFS 探索到的所有可达格子；最终路径只包括由目标沿前驱回溯到起点的格子，所以两者不同。
- BFS 用队列逐层探索；每步代价都是 1，首次到达目标时得到最少步数。第三、四、五问使用同一个 `plan` 函数。
- 无路是实际观察到的边界案例：`map_blocked` 和第二次更新均返回 `found=false`、空路径、`steps=null`。起终点相同则返回单点路径和 0 步。
- 局限：机器人按单格点处理，未考虑实际宽度、转弯半径和动态移动过程；第五问只在每次地图更新后重新规划。

## AI 与参考资料

使用 ChatGPT/Codex 协助编写 Python 源码、绘图和报告。检查方式：运行程序生成实际输出；逐项核对四张地图的可达性和步数、更新后的通道选择，并检查路径上的相邻坐标、障碍与边界。参考资料为本仓库的 [README.md](README.md) 和 `materials/` 中的原始 JSON；未使用其他资料。
