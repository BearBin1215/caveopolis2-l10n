"""生成 FTB 任务书的 zh_cn 语言目录。"""

from __future__ import annotations

import json
from pathlib import Path

import json5ish
from common import CONFIG, EXTRACTED, write_json

EN_ROOT = EXTRACTED / "quests" / "en_us"
ZH_ROOT = CONFIG / "ftbquests" / "quests" / "lang" / "zh_cn"
QUEST_ZH = Path(__file__).resolve().parent / "quests_zh"
DIVIDER = "&8" + "─" * 15

TITLES = {
    "Not Alone": "不再孤单",
    "Cave Sweet Cave": "洞穴之家",
    "The Depths": "深处",
    "Information": "信息",
    "End of the Line": "终点",
    "Kitchen": "厨房",
    "Tips and Tricks": "技巧与提示",
    "Energy": "能量",
    "Heating Up": "升温",
    "Charging": "充能",
    "The Heights": "高处",
    "Seedy": "种子",
    "Caveopolis": "Caveopolis",
    "Caveopolis 2": "Caveopolis 2",
    "Camol": "Camol",
    "Functional Storage": "功能性存储",
    "Easy Storage": "简易存储",
    "Planks": "木板",
    "Sapling": "树苗",
    "Leaves": "树叶",
    "Logs": "原木",
    "More Leaf Piles": "更多落叶堆",
    "Unlocks new Shop Items...": "解锁新的商店物品……",
    "Endgame": "终局",
    "The End": "终章",
    "Tier 3 Seeds": "3 级种子",
    "Molten Blaze": "熔融烈焰",
    "One of the Depth Charms": "深度护符之一",
    "Shop": "商店",
    "The World": "世界",
    "Trader": "商人",
    "Welcome To Caveopolis 2": "欢迎来到 Caveopolis 2",
    "Public Server": "公共服务器",
    "Quests": "任务",
    "Ultimine": "连锁挖掘",
    "Shaders": "光影",
    "Resource Packs": "资源包",
    "Sniffer": "嗅探兽",
    "Counter": "厨柜",
    "Sniffy Sniffer": "灵敏嗅探兽",
    "Unlocks new Trades...": "解锁新的交易……",
    "Mystical Enlightment": "神秘启示",
    "Mystical Enlightenment": "神秘启示",
    "Wither Skeleton": "凋灵骷髅",
    "Easy Piglins": "轻松搬运猪灵",
    "Piglins": "猪灵",
    "Piglin Trading": "猪灵交易",
    "Tier 4 Seeds": "4 级种子",
    "The Wither": "凋灵",
    "Villagers": "村民",
    "Molten Experience": "熔融经验",
    "Friend?": "朋友？",
    "First Alloys": "最初的合金",
    "Breaking and Placing": "破坏与放置",
    "Routers": "路由器",
    "Silicon": "硅",
    "The Next Tier of Seeds": "下一级种子",
    "First Mystical Seeds": "最初的神秘种子",
    "Reinforced Deepslate": "强化深板岩",
    "Colored Shimmer Crystals": "彩色微光水晶",
    "Tier 5 Seeds": "5 级种子",
    "Creating Geores": "制造矿晶母岩",
    "The Warden": "监守者",
    "Combination Crafting": "组合合成",
    "You Did It": "你做到了",
    "Ender Crafting": "末影合成",
    "Tier 6 Seeds": "6 级种子",
    "GG": "GG",
    "The Ultimate Tools": "终极工具",
    "Planet Locator: Asteroid": "行星定位器：小行星",
    "Spyglass": "望远镜",
    "Flux Crafting": "通量合成",
    "Meshes": "滤网",
    "Construction Sticks": "建筑棒",
    "Dyes": "染料",
    "get ge ores": "获取矿晶",
}

def load_descriptions() -> dict[str, dict[str, list[str]]]:
    result: dict[str, dict[str, list[str]]] = {}
    for path in sorted(QUEST_ZH.glob("*.json")):
        result[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return result


TAG_NAMES = {
    "#minecraft:leaves": "树叶",
    "#minecraft:logs": "原木",
    "#minecraft:planks": "木板",
    "#minecraft:saplings": "树苗",
    "#c:chests/wooden": "木箱",
    "#c:dyes": "染料",
    "#c:silicon": "硅",
    "#strainers:meshes": "滤网",
    "#functionalstorage:drawer": "抽屉",
    "#cookingforblockheads:counters": "厨柜",
    "#geore:spyglasses": "矿晶望远镜",
    "#caveopolis:colored_shimmer_crystals": "彩色微光水晶",
    "#caveopolis:mystical_seed_1": "1 级神秘种子",
    "#caveopolis:mystical_seed_2": "2 级神秘种子",
    "#caveopolis:mystical_seed_3": "3 级神秘种子",
    "#caveopolis:mystical_seed_4": "4 级神秘种子",
    "#caveopolis:mystical_seed_5": "5 级神秘种子",
    "#caveopolis:mystical_seed_6": "6 级神秘种子",
}


def translate_title(english: str) -> str | None:
    if english in TITLES:
        return TITLES[english]
    if english.startswith("Any #"):
        tag = english[4:]
        name = TAG_NAMES.get(tag)
        if name:
            separator = " " if name[:1].isascii() else ""
            return "任意" + separator + name
        return "任意 " + tag
    return None


def bilingual(chinese: list[str], english: list[str]) -> list[str]:
    result: list[str] = []
    for group in (chinese, english):
        if not group:
            continue
        if result:
            result.extend(["", DIVIDER, ""])
        for index, line in enumerate(group):
            if index:
                result.append("")
            result.append(line)
    return result


def main() -> None:
    descriptions = load_descriptions()
    for en_path in sorted(EN_ROOT.rglob("*.json5")):
        relative = en_path.relative_to(EN_ROOT)
        chapter = en_path.stem
        en = json5ish.load(en_path)
        zh: dict[str, object] = {}
        for key, value in en.items():
            if key.endswith((".title", ".quest_subtitle")):
                translated = translate_title(str(value))
                if translated:
                    zh[key] = translated
            elif key.endswith(".quest_desc"):
                chinese = descriptions.get(chapter, {}).get(key)
                if chinese is None:
                    raise SystemExit(f"缺少译文：{chapter}/{key}")
                english = [line for line in value if line]
                zh[key] = bilingual(chinese, english)
        out = ZH_ROOT / relative
        write_json(out, zh)
        print(f"{relative}: {len(zh)} 条")


if __name__ == "__main__":
    main()
