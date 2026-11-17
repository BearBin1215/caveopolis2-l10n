# Colors 与折叠分组命名规则

`config/collapsiblegroups/lang/zh_cn.json` 的 871 条分组名由 `tools/translate_groups.py` 按规则生成，规则按优先级排列如下。

## 1. 精确表（EXACT）

原版和常见模组的固定译名直接写入 `EXACT` 表，不再拼接。例如：

- `Oak Door` → 橡木门，`Stripped Cherry Log` → 去皮樱花原木
- `Vanilla Wools` → 原版羊毛，`Vanilla Glazed Terracottas` → 原版带釉陶瓦
- `AE2` 的 `Colored Covered Cables` → 彩色包层线缆
- 法术卷轴、宝石、药水护符等成组条目整表登记

如果规则拼接的结果不自然，优先把整条译名加入 `EXACT` 表。

## 2. Macaw's 系列（MACAW）

Macaw's 系列的 Bridges、Doors、Fences、Furnitures、Lights、Paths、Roofs、Stairs、Trapdoors、Windows 分类整表登记，避免逐词拼接。例如：

- `Bamboo Bridges` → 竹桥，`Rope Stairs` → 绳索桥阶梯
- `Shoji Doors` → 障子门，`Stable Head Doors` → 马厩半截门
- `Ceiling Fan Lights` → 吊扇灯，`Roof Slabs` → 屋顶台阶

前缀如 `Macaw's Bridges:` 保留英文，并把冒号改为全角。

## 3. 颜色前缀（COLORS）

| 英文 | 中文 | 英文 | 中文 |
|---|---|---|---|
| Black | 黑色 | Orange | 橙色 |
| Blue | 蓝色 | Pink | 粉红色 |
| Brown | 棕色 | Purple | 紫色 |
| Cyan | 青色 | Red | 红色 |
| Gray | 灰色 | White | 白色 |
| Green | 绿色 | Yellow | 黄色 |
| Light Blue | 淡蓝色 | Lime | 黄绿色 |
| Light Gray | 淡灰色 | Magenta | 品红色 |

颜色前缀与基础名直接相连，不加“的”：`White Stone` → 白色石头，`Light Blue Planks` → 淡蓝色木板。

特例：

- `<Color> Dyed Glass` → `<颜色>染色玻璃`
- `<Color> Dyed Glass Pane` → `<颜色>染色玻璃板`
- `<Color> Hexplating` → `<颜色>六边形板`

## 4. 木质前缀（WOODS）

Oak 橡木、Spruce 云杉木、Birch 白桦木、Jungle 丛林木、Acacia 金合欢木、Dark Oak 深色橡木、Mangrove 红树木、Cherry 樱花木、Bamboo 竹、Crimson 绯红菌、Warped 诡异菌。

## 5. 金属材料（METALS）

Aluminum 铝、Bronze 青铜、Cobalt 钴、Electrum 琥珀金、Invar 殷钢、Nickel 镍、Platinum 铂、Silver 银、Steel 钢、Tin 锡、Uranium 铀。

`<Metal> Blocks` → `<金属>块`，例如 `Steel Blocks` → 钢块。

## 6. 后缀（SUFFIXES）

常见复数后缀：Blocks 块、Doors 门、Trapdoors 活板门、Bridges 桥、Piers 桥墩、Stairs 楼梯、Fences 栅栏、Walls 墙、Paths 路径、Roofs 屋顶、Windows 窗户、Lights/Lamps 灯、Torches 火把、Lanterns 灯笼、Gates 大门、Grids 终端、Scrolls 卷轴、Gems 宝石。

## 7. 修饰词（MODIFIERS）

用于后缀前的修饰词，例如 Modern 现代、Mystic 神秘、Nether 下界、Shoji 障子、Waffle 华夫、Western 西部、Barred 栅栏、Upper 上层、Lower 下层、Steep 陡坡、Skyline 天际、Terrace 露台。

## 8. 兜底顺序

1. 优先查整条精确表。
2. 再按前缀表处理（颜色 → 木质 → 金属）。
3. 再按后缀拆分（修饰词 + 后缀）。
4. 去掉复数后缀后重试。
5. 如果仍然失败，保留英文并计入 `未翻译`；脚本会打印该条目，供补充规则表。

生成命令：

```bash
python tools/translate_groups.py
```

当前状态：871 条分组已全部译出，未翻译 0 条。若整合包新增分组，重新运行脚本，并按输出结果补充到 `EXACT` 表。
