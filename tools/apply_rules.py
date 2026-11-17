"""按命名规则生成 Colors 模组的剩余中文条目。"""

from __future__ import annotations

import json

from common import EXTRACTED, RESOURCEPACK, read_json, write_json

COLORS = {
    "black": "黑色",
    "blue": "蓝色",
    "brown": "棕色",
    "cyan": "青色",
    "gray": "灰色",
    "green": "绿色",
    "light_blue": "淡蓝色",
    "light_gray": "淡灰色",
    "lime": "黄绿色",
    "magenta": "品红色",
    "orange": "橙色",
    "pink": "粉红色",
    "purple": "紫色",
    "red": "红色",
    "white": "白色",
    "yellow": "黄色",
}

SUFFIXES = {
    "chest": "箱子",
    "sand": "沙子",
    "sandstone": "砂岩",
    "sandstone_button": "砂岩按钮",
    "sandstone_pressure_plate": "砂岩压力板",
    "sandstone_slab": "砂岩台阶",
    "sandstone_stairs": "砂岩楼梯",
    "sandstone_wall": "砂岩墙",
    "bamboo_mosaic_sign": "竹马赛克告示牌",
    "bamboo_mosaic_wall_sign": "墙上的竹马赛克告示牌",
    "bamboo_mosaic_hanging_sign": "悬挂式竹马赛克告示牌",
    "bamboo_mosaic_wall_hanging_sign": "墙上的悬挂式竹马赛克告示牌",
    "bamboo_plank_sign": "竹板告示牌",
    "bamboo_plank_wall_sign": "墙上的竹板告示牌",
    "bamboo_plank_hanging_sign": "悬挂式竹板告示牌",
    "bamboo_plank_wall_hanging_sign": "墙上的悬挂式竹板告示牌",
    "plank_sign": "木告示牌",
    "plank_wall_sign": "墙上的木告示牌",
    "plank_hanging_sign": "悬挂式木告示牌",
    "plank_wall_hanging_sign": "墙上的悬挂式木告示牌",
}


def apply_fixes(zh: dict[str, str]) -> int:
    fixed = 0
    for key, value in list(zh.items()):
        replacement = value
        if key.endswith(("_chaotic_stairs", "_bamboo_plank_stairs")):
            replacement = value.replace("台阶", "楼梯")
        elif key.endswith("_cracked_stone_brick_slab"):
            replacement = value.replace("楼梯", "台阶")
        elif key.endswith("_road_button") and not value.endswith("按钮"):
            replacement = value + "按钮"
        elif key.endswith("_tiles") and value.endswith("石瓦墙"):
            replacement = value[:-1]
        elif key.startswith("block.colors.red_sandstone"):
            replacement = value.replace("红色砂岩", "红砂岩")
        elif key.endswith("_polished_wall"):
            replacement = value.replace("磨制石头墙", "磨制石墙")
        elif key == "block.colors.red_sand":
            replacement = "红沙"
        elif key.endswith(("_wall_sign", "_wall_hanging_sign")):
            for color_zh in COLORS.values():
                prefix = color_zh + "墙上的"
                if value.startswith(prefix):
                    replacement = "墙上的" + color_zh + value[len(prefix) :]
                    break
        if replacement != value:
            zh[key] = replacement
            fixed += 1
    return fixed


def main() -> None:
    en = read_json(EXTRACTED / "mods" / "colors" / "en_us.json")
    path = RESOURCEPACK / "assets" / "colors" / "lang" / "zh_cn.json"
    zh = read_json(path)
    added = 0
    unknown = []
    for key, english in en.items():
        if zh.get(key):
            continue
        name = key.removeprefix("block.colors.").removeprefix("item.colors.")
        for color, color_zh in COLORS.items():
            prefix = f"{color}_"
            if not name.startswith(prefix):
                continue
            suffix = name[len(prefix) :]
            if suffix not in SUFFIXES:
                unknown.append((key, english))
                break
            zh[key] = color_zh + SUFFIXES[suffix]
            added += 1
            break
        else:
            unknown.append((key, english))

    fixed = apply_fixes(zh)
    ordered = {key: zh[key] for key in en if key in zh}
    write_json(path, ordered)
    print(f"按规则生成 {added} 条，修正 {fixed} 条，仍未处理 {len(unknown)} 条")
    for key, english in unknown:
        print(f"  未处理：{key} = {english}")


if __name__ == "__main__":
    main()
