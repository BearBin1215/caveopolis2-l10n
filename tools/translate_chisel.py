"""生成 Chisel 的 zh_cn 语言文件。

Chisel 的 38,008 个键只包含 370 个不同方块名和 1,263 条不同说明，
因此先翻译去重后的字符串，再映射回全部键。手册引导文本另存于 chisel_guide_zh.json。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from chisel_data import EXACT, TOKENS
from common import RESOURCEPACK, WORK, find_jar, jar_lang, read_json, write_json

GUIDE_ZH = Path(__file__).resolve().parent / "chisel_guide_zh.json"

NAMES = {
    "Acacia Bookshelf": "金合欢木书架",
    "Acacia Planks": "金合欢木板",
    "Aluminum": "铝",
    "Ancient Debris": "远古残骸",
    "Ancient Stone": "远古石",
    "Andesite": "安山岩",
    "Antiblock": "反方块",
    "Arcane": "奥术石",
    "Auto Chisel": "自动凿子",
    "Bamboo Bookshelf": "竹书架",
    "Bamboo Planks": "竹板",
    "Basalt": "玄武岩",
    "Birch Bookshelf": "白桦木书架",
    "Birch Planks": "白桦木板",
    "Black Concrete": "黑色混凝土",
    "Black Light": "黑色光源",
    "Black Oak Framed Stained Glass": "黑色橡木边框染色玻璃",
    "Black Stained Glass": "黑色染色玻璃",
    "Black Stained Glass Pane": "黑色染色玻璃板",
    "Black Steel Framed Stained Glass": "黑色钢边框染色玻璃",
    "Black Wool": "黑色羊毛",
    "Blackstone": "黑石",
    "Blank Rune": "空白符文",
    "Block of Amethyst": "紫水晶块",
    "Block of Copper": "铜块",
    "Block of Diamond": "钻石块",
    "Block of Emerald": "绿宝石块",
    "Block of Gold": "金块",
    "Block of Iron": "铁块",
    "Block of Lapis Lazuli": "青金石块",
    "Block of Netherite": "下界合金块",
    "Block of Quartz": "石英块",
    "Block of Raw Copper": "粗铜块",
    "Block of Raw Gold": "粗金块",
    "Block of Raw Iron": "粗铁块",
    "Block of Redstone": "红石块",
    "Blue Concrete": "蓝色混凝土",
    "Blue Ice": "蓝冰",
    "Blue Light": "蓝色光源",
    "Blue Oak Framed Stained Glass": "蓝色橡木边框染色玻璃",
    "Blue Stained Glass": "蓝色染色玻璃",
    "Blue Stained Glass Pane": "蓝色染色玻璃板",
    "Blue Steel Framed Stained Glass": "蓝色钢边框染色玻璃",
    "Blue Wool": "蓝色羊毛",
    "Bone Block": "骨块",
    "Bricks": "砖块",
    "Bright Glass": "明亮玻璃",
    "Bronze": "青铜",
    "Brown Concrete": "棕色混凝土",
    "Brown Light": "棕色光源",
    "Brown Oak Framed Stained Glass": "棕色橡木边框染色玻璃",
    "Brown Stained Glass": "棕色染色玻璃",
    "Brown Stained Glass Pane": "棕色染色玻璃板",
    "Brown Steel Framed Stained Glass": "棕色钢边框染色玻璃",
    "Brown Wool": "棕色羊毛",
    "Builders Guide": "建筑师指南",
    "Calcite": "方解石",
    "Certus Quartz": "赛特斯石英",
    "Charcoal": "木炭",
    "Cherry Bookshelf": "樱花木书架",
    "Cherry Planks": "樱花木板",
    "Clay": "黏土",
    "Cloud": "云",
    "Coal Block": "煤炭块",
    "Coal Coke": "焦炭",
    "Cobalt": "钴",
    "Cobbled Deepslate": "深板岩圆石",
    "Cobblestone": "圆石",
    "Concrete": "混凝土",
    "Crimson Bookshelf": "绯红木书架",
    "Crimson Planks": "绯红木板",
    "Crying Obsidian": "哭泣的黑曜石",
    "Cyan Concrete": "青色混凝土",
    "Cyan Light": "青色光源",
    "Cyan Oak Framed Stained Glass": "青色橡木边框染色玻璃",
    "Cyan Stained Glass": "青色染色玻璃",
    "Cyan Stained Glass Pane": "青色染色玻璃板",
    "Cyan Steel Framed Stained Glass": "青色钢边框染色玻璃",
    "Cyan Wool": "青色羊毛",
    "Dark Oak Bookshelf": "深色橡木书架",
    "Dark Oak Planks": "深色橡木木板",
    "Dark Prismarine": "暗海晶石",
    "Deepslate": "深板岩",
    "Diorite": "闪长岩",
    "Dirt": "泥土",
    "Dripstone Block": "滴水石块",
    "Electrum": "琥珀金",
    "End Stone": "末地石",
    "Energized Voidstone": "充能虚空石",
    "Exposed Copper": "斑驳的铜块",
    "Factory Block": "工厂方块",
    "Futura Block": "未来方块",
    "Gilded Blackstone": "镶金黑石",
    "Glass": "玻璃",
    "Glass Pane": "玻璃板",
    "Glowstone": "荧石",
    "Granite": "花岗岩",
    "Gray Concrete": "灰色混凝土",
    "Gray Light": "灰色光源",
    "Gray Oak Framed Stained Glass": "灰色橡木边框染色玻璃",
    "Gray Stained Glass": "灰色染色玻璃",
    "Gray Stained Glass Pane": "灰色染色玻璃板",
    "Gray Steel Framed Stained Glass": "灰色钢边框染色玻璃",
    "Gray Wool": "灰色羊毛",
    "Green Concrete": "绿色混凝土",
    "Green Light": "绿色光源",
    "Green Oak Framed Stained Glass": "绿色橡木边框染色玻璃",
    "Green Stained Glass": "绿色染色玻璃",
    "Green Stained Glass Pane": "绿色染色玻璃板",
    "Green Steel Framed Stained Glass": "绿色钢边框染色玻璃",
    "Green Wool": "绿色羊毛",
    "Grimstone": "阴森石",
    "Hex Plating": "六边形板",
    "Holystone": "圣石",
    "Ice": "冰",
    "Invar": "殷钢",
    "Iron Bars": "铁栏杆",
    "Jack o'Lantern": "南瓜灯",
    "Jungle Bookshelf": "丛林木书架",
    "Jungle Planks": "丛林木板",
    "Kitchen Block": "厨房方块",
    "Laboratory Block": "实验室方块",
    "Lavastone": "熔岩石",
    "Lead": "铅",
    "Leaf Block": "树叶块",
    "Light Blue Concrete": "淡蓝色混凝土",
    "Light Blue Light": "淡蓝色光源",
    "Light Blue Oak Framed Stained Glass": "淡蓝色橡木边框染色玻璃",
    "Light Blue Stained Glass": "淡蓝色染色玻璃",
    "Light Blue Stained Glass Pane": "淡蓝色染色玻璃板",
    "Light Blue Steel Framed Stained Glass": "淡蓝色钢边框染色玻璃",
    "Light Blue Wool": "淡蓝色羊毛",
    "Light Gray Concrete": "淡灰色混凝土",
    "Light Gray Light": "淡灰色光源",
    "Light Gray Oak Framed Stained Glass": "淡灰色橡木边框染色玻璃",
    "Light Gray Stained Glass": "淡灰色染色玻璃",
    "Light Gray Stained Glass Pane": "淡灰色染色玻璃板",
    "Light Gray Steel Framed Stained Glass": "淡灰色钢边框染色玻璃",
    "Light Gray Wool": "淡灰色羊毛",
    "Lime Concrete": "黄绿色混凝土",
    "Lime Light": "黄绿色光源",
    "Lime Oak Framed Stained Glass": "黄绿色橡木边框染色玻璃",
    "Lime Stained Glass": "黄绿色染色玻璃",
    "Lime Stained Glass Pane": "黄绿色染色玻璃板",
    "Lime Steel Framed Stained Glass": "黄绿色钢边框染色玻璃",
    "Lime Wool": "黄绿色羊毛",
    "Limestone": "石灰岩",
    "Liminal Block": "阈限方块",
    "Magenta Concrete": "品红色混凝土",
    "Magenta Light": "品红色光源",
    "Magenta Oak Framed Stained Glass": "品红色橡木边框染色玻璃",
    "Magenta Stained Glass": "品红色染色玻璃",
    "Magenta Stained Glass Pane": "品红色染色玻璃板",
    "Magenta Steel Framed Stained Glass": "品红色钢边框染色玻璃",
    "Magenta Wool": "品红色羊毛",
    "Magma": "岩浆块",
    "Mangrove Bookshelf": "红树木书架",
    "Mangrove Planks": "红树木板",
    "Marble": "大理石",
    "Military": "军用",
    "Mossy Blackstone": "苔藓黑石",
    "Mossy Cobblestone": "苔石",
    "Mossy Deepslate": "苔藓深板岩",
    "Mossy Stone": "苔藓石头",
    "Mossy Temple Block": "苔藓神庙方块",
    "Mud": "泥",
    "Nether Brick": "下界砖",
    "Nether Bricks": "下界砖块",
    "Netherrack": "下界岩",
    "Nexus Block": "枢纽方块",
    "Nickel": "镍",
    "Oak Bookshelf": "橡木书架",
    "Oak Framed Glass": "橡木边框玻璃",
    "Oak Planks": "橡木木板",
    "Obsidian": "黑曜石",
    "Orange Concrete": "橙色混凝土",
    "Orange Light": "橙色光源",
    "Orange Oak Framed Stained Glass": "橙色橡木边框染色玻璃",
    "Orange Stained Glass": "橙色染色玻璃",
    "Orange Stained Glass Pane": "橙色染色玻璃板",
    "Orange Steel Framed Stained Glass": "橙色钢边框染色玻璃",
    "Orange Wool": "橙色羊毛",
    "Oxidized Copper": "氧化铜块",
    "Packed Ice": "浮冰",
    "Packed Mud": "泥坯",
    "Pale Oak Bookshelf": "苍白橡木书架",
    "Pale Oak Planks": "苍白橡木木板",
    "Paperwall": "纸墙",
    "Pink Concrete": "粉红色混凝土",
    "Pink Light": "粉红色光源",
    "Pink Oak Framed Stained Glass": "粉红色橡木边框染色玻璃",
    "Pink Stained Glass": "粉红色染色玻璃",
    "Pink Stained Glass Pane": "粉红色染色玻璃板",
    "Pink Steel Framed Stained Glass": "粉红色钢边框染色玻璃",
    "Pink Wool": "粉红色羊毛",
    "Platinum": "铂",
    "Prismarine": "海晶石",
    "Prismarine Bricks": "海晶石砖",
    "Pumpkin": "南瓜",
    "Purple Concrete": "紫色混凝土",
    "Purple Light": "紫色光源",
    "Purple Oak Framed Stained Glass": "紫色橡木边框染色玻璃",
    "Purple Stained Glass": "紫色染色玻璃",
    "Purple Stained Glass Pane": "紫色染色玻璃板",
    "Purple Steel Framed Stained Glass": "紫色钢边框染色玻璃",
    "Purple Wool": "紫色羊毛",
    "Purpur": "紫珀块",
    "Red Concrete": "红色混凝土",
    "Red Light": "红色光源",
    "Red Nether Bricks": "红色下界砖块",
    "Red Oak Framed Stained Glass": "红色橡木边框染色玻璃",
    "Red Sandstone": "红砂岩",
    "Red Stained Glass": "红色染色玻璃",
    "Red Stained Glass Pane": "红色染色玻璃板",
    "Red Steel Framed Stained Glass": "红色钢边框染色玻璃",
    "Red Wool": "红色羊毛",
    "Redstone Lamp": "红石灯",
    "Resin": "树脂",
    "Road Lines": "道路标线",
    "Sandstone": "砂岩",
    "Sculk": "幽匿块",
    "Sea Lantern": "海晶灯",
    "Shingles": "屋瓦",
    "Silver": "银",
    "Sky Stone": "陨石",
    "Smooth Stone": "平滑石头",
    "Snow Block": "雪块",
    "Soul Soil": "灵魂土",
    "Spruce Bookshelf": "云杉木书架",
    "Spruce Planks": "云杉木板",
    "Steel": "钢",
    "Steel Framed Glass": "钢边框玻璃",
    "Stone": "石头",
    "Stone Bricks": "石砖",
    "Tallow": "动物油脂",
    "Technical Block": "科技方块",
    "Temple Block": "神庙方块",
    "Terracotta": "陶瓦",
    "Thaumium": "神秘金属",
    "Tin": "锡",
    "Torch": "火把",
    "Tuff": "凝灰岩",
    "Tyrian": "泰尔紫",
    "Uranium": "铀",
    "Valentine's Block": "情人节方块",
    "Voidstone": "虚空石",
    "Warning Sign": "警告标志",
    "Warped Bookshelf": "诡异木书架",
    "Warped Planks": "诡异木板",
    "Waterstone": "水石",
    "Waxed Block of Copper": "涂蜡的铜块",
    "Waxed Exposed Copper": "涂蜡的斑驳铜块",
    "Waxed Oxidized Copper": "涂蜡的氧化铜块",
    "Waxed Weathered Copper": "涂蜡的锈蚀铜块",
    "Weathered Copper": "锈蚀的铜块",
    "White Concrete": "白色混凝土",
    "White Light": "白色光源",
    "White Oak Framed Stained Glass": "白色橡木边框染色玻璃",
    "White Stained Glass": "白色染色玻璃",
    "White Stained Glass Pane": "白色染色玻璃板",
    "White Steel Framed Stained Glass": "白色钢边框染色玻璃",
    "White Wool": "白色羊毛",
    "Woolen Clay": "羊毛黏土",
    "Yellow Concrete": "黄色混凝土",
    "Yellow Light": "黄色光源",
    "Yellow Oak Framed Stained Glass": "黄色橡木边框染色玻璃",
    "Yellow Stained Glass": "黄色染色玻璃",
    "Yellow Stained Glass Pane": "黄色染色玻璃板",
    "Yellow Steel Framed Stained Glass": "黄色钢边框染色玻璃",
    "Yellow Wool": "黄色羊毛",
}

_COLOR_ZH = {
    "Black": "黑色", "Blue": "蓝色", "Brown": "棕色", "Cyan": "青色",
    "Gray": "灰色", "Green": "绿色", "Light Blue": "淡蓝色",
    "Light Gray": "淡灰色", "Lime": "黄绿色", "Magenta": "品红色",
    "Orange": "橙色", "Pink": "粉红色", "Purple": "紫色", "Red": "红色",
    "White": "白色", "Yellow": "黄色",
    "Amber": "琥珀色", "Aquamarine": "海蓝色", "Bubblegum": "泡泡糖色",
    "Cherenkov": "切伦科夫色", "Conifer": "针叶色", "Fluorescent": "荧光色",
    "Honey": "蜂蜜色", "Icy Blue": "冰蓝色", "Lavender": "薰衣草色",
    "Maroon": "栗色", "Mint": "薄荷色", "Navy": "藏青色", "Peach": "桃色",
    "Persimmon": "柿子色", "Rose": "玫瑰色", "Spring Green": "春绿色",
    "Ultramarine": "群青色", "Wine": "酒红色",
}
for _color, _zh in _COLOR_ZH.items():
    NAMES.setdefault(f"{_color} Concrete", f"{_zh}混凝土")
    NAMES.setdefault(f"{_color} Stained Glass", f"{_zh}染色玻璃")
    NAMES[f"{_color} Oak Framed Stained Glass"] = f"橡木边框{_zh}染色玻璃"
    NAMES[f"{_color} Steel Framed Stained Glass"] = f"钢边框{_zh}染色玻璃"

METALS = {
    "Aluminum": "铝", "Bronze": "青铜", "Charcoal": "木炭", "Coal Coke": "焦炭",
    "Cobalt": "钴", "Electrum": "琥珀金", "Invar": "殷钢", "Lead": "铅",
    "Nickel": "镍", "Platinum": "铂", "Resin": "树脂", "Silver": "银",
    "Steel": "钢", "Tallow": "动物油脂", "Thaumium": "神秘金属", "Tin": "锡",
    "Uranium": "铀",
    "Antimony": "锑", "Brass": "黄铜", "Chromium": "铬", "Cinnabar": "朱砂",
    "Constantan": "康铜", "Enderium": "末影", "Fluorite": "氟石",
    "Graphite": "石墨", "Iridium": "铱", "Lumium": "流明",
    "Osmium": "锇", "Peridot": "橄榄石", "Plutonium": "钚",
    "Rose Quartz": "玫瑰石英", "Ruby": "红宝石", "Salt": "盐",
    "Sapphire": "蓝宝石", "Signalum": "信素", "Silicon": "硅",
    "Stainless Steel": "不锈钢", "Sulfur": "硫磺", "Titanium": "钛",
    "Tungsten": "钨", "Zinc": "锌",
}
for _english, _zh in METALS.items():
    NAMES[_english] = _zh + "块"

NAMES["Technical Block"] = "技术方块"
NAMES["Builder's Guide"] = "建筑师指南"
NAMES["Fantasy Block"] = "幻想方块"
NAMES["Fluix Block"] = "福鲁伊克斯方块"
NAMES["Redstone Sea Lamp"] = "红石海晶灯"
NAMES["Steampunk Block"] = "蒸汽朋克方块"

OTHER = {
    "chisel.builders_guide.mode_changed": "模式已切换为",
    "chisel.builders_guide.size_changed": "尺寸已切换为",
    "chisel.building_mode.chisel:axes": "轴",
    "chisel.building_mode.chisel:cuboid": "长方体（棱）",
    "chisel.building_mode.chisel:cylinder": "圆柱体",
    "chisel.building_mode.chisel:dome": "穹顶",
    "chisel.building_mode.chisel:full_cuboid": "长方体（面）",
    "chisel.building_mode.chisel:hexagon": "六边形",
    "chisel.building_mode.chisel:octagon": "八边形",
    "chisel.building_mode.chisel:pentagon": "五边形",
    "chisel.building_mode.chisel:planes": "平面",
    "chisel.building_mode.chisel:sphere": "球体",
    "chisel.building_mode.chisel:triangle": "三角形",
    "chisel.gui.no_variants": "没有匹配的变体",
    "chisel.gui.search": "搜索：",
    "chisel.mode.column": "柱状",
    "chisel.mode.panel": "镶板",
    "chisel.mode.row": "横排",
    "chisel.mode.shapeless": "无序",
    "chisel.mode.shapeless_exact": "无序精确",
    "chisel.mode.shapeless_flat": "无序平铺",
    "chisel.mode.shapeless_flat_exact": "无序平铺精确",
    "chisel.mode.single": "单个",
    "chisel.preview.column": "柱状",
    "chisel.preview.donut": "环形",
    "chisel.preview.panel": "镶板",
    "chisel.preview.plus": "十字",
    "chisel.preview.row": "横排",
    "chisel.preview.single": "单个",
    "chisel.search": "搜索",
    "config.jade.plugin_chisel.jade_plugin": "Chisel 描述",
    "container.auto_chisel": "自动凿子",
    "container.chisel": "凿子",
    "item.chisel.auto_chisel": "自动凿子",
    "item.chisel.ball_o_moss.desc": "右击投掷，会把多种方块变成对应的苔藓版本",
    "item.chisel.ballomoss": "苔藓球",
    "item.chisel.builders_guide": "建筑师指南",
    "item.chisel.chisel.desc1": "右击打开界面",
    "item.chisel.chisel.desc2": "左击可为世界中的方块凿刻",
    "item.chisel.chisel.desc3": "把方块放入凿子槽位即可将其设为目标",
    "item.chisel.chisel_diamond": "钻石凿子",
    "item.chisel.chisel_iron": "凿子",
    "item.chisel.chisel_obsidian": "黑曜石凿子",
    "item.chisel.cloud_in_a_bottle.desc": "右击投掷，撞击时生成云",
    "item.chisel.cloudinabottle": "瓶装云",
    "item.chisel.measuring_tape": "卷尺",
    "item.chisel.offset_tool": "末影偏移魔杖",
    "item.chisel.offset_tool.desc": "右击高亮方向以偏移纹理",
    "item.chisel.offset_tool.desc2": "只高亮可偏移的纹理",
    "item.chisel.smashing_rock.desc": "右击投掷，撞击时粉碎方块",
    "item.chisel.smashingrock": "粉碎石",
    "item.chisel.upgrade_automation": "自动化升级",
    "item.chisel.upgrade_reversion": "还原升级",
    "item.chisel.upgrade_speed": "速度升级",
    "item.chisel.upgrade_stack": "堆叠升级",
    "itemGroup.tabChisel": "凿子物品",
    "itemGroup.tabMetalChiselBlocks": "金属凿刻方块",
    "itemGroup.tabModdedChiselBlocks": "模组凿刻方块",
    "itemGroup.tabOtherChiselBlocks": "其他凿刻方块",
    "itemGroup.tabStoneChiselBlocks": "石质凿刻方块",
    "itemGroup.tabWoodChiselBlocks": "木质凿刻方块",
    "key.category.chisel.chisel": "Chisel",
    "key.chisel.mode_select": "选择凿子模式",
    "stat.chisel.blocks_chiseled": "已凿刻方块数",
    "tooltip.chisel.builders_guide.height_desc": "右击顶面或底面以更改高度",
    "tooltip.chisel.builders_guide.length_desc": "右击北面或南面以更改长度",
    "tooltip.chisel.builders_guide.mode_desc": "Shift + 右击以更改模式",
    "tooltip.chisel.builders_guide.place_desc": "手持方块右击以按形状放置",
    "tooltip.chisel.builders_guide.width_desc": "右击东面或西面以更改宽度",
}

OTHER.update({
    "item.chisel.chisel.desc2": "左击可凿刻世界中的方块",
    "itemGroup.tabChisel": "凿子物品",
    "tooltip.chisel.builders_guide.mode_desc": "Shift + 右击以更改模式",
    "config.jade.plugin_chisel.jade_plugin": "Chisel 方块描述",
})

WORD_JOIN = re.compile(r"(?<=[\u4e00-\u9fff])(?=\d)|(?<=\d)(?=[\u4e00-\u9fff])")
LATIN_SPACE = re.compile(r"(?<=[\u4e00-\u9fff])(?=[A-Za-z])|(?<=[A-Za-z])(?=[\u4e00-\u9fff])")
OAK_WOOD = re.compile(r"\b(?:Dark Oak|Pale Oak|Oak) Wood ")


def translate_desc(text: str) -> str | None:
    if text in EXACT:
        return EXACT[text]
    text = OAK_WOOD.sub(lambda match: match.group(0)[:-5], text)
    words = text.split()
    parts: list[str] = []
    index = 0
    while index < len(words):
        for size in (4, 3, 2, 1):
            candidate = " ".join(words[index : index + size])
            if candidate.isdigit():
                parts.append(candidate)
                index += size
                break
            if candidate in TOKENS:
                parts.append(TOKENS[candidate])
                index += size
                break
        else:
            return None
    result = "".join(parts)
    result = WORD_JOIN.sub(" ", result)
    return LATIN_SPACE.sub(" ", result)


def build() -> dict[str, str]:
    jar = find_jar("chisel")
    en = jar_lang(jar, "chisel", "en_us")
    assert en
    result = dict(OTHER)
    result.update(read_json(GUIDE_ZH))
    missing: set[str] = set()
    for key, english in en.items():
        if key.startswith("block.chisel.") and key.endswith(".desc"):
            translated = translate_desc(english)
        elif key.startswith("block.chisel."):
            translated = NAMES.get(english)
        else:
            continue
        if translated is None:
            missing.add(english)
            continue
        result[key] = translated
    if missing:
        (WORK / "chisel_missing.txt").write_text(
            "\n".join(sorted(missing)) + "\n", encoding="utf-8", newline="\n"
        )
        raise SystemExit(f"未翻译 {len(missing)} 条，见 work/chisel_missing.txt")
    output = RESOURCEPACK / "assets" / "chisel" / "lang" / "zh_cn.json"
    write_json(output, result)
    print(f"Chisel：{len(result)} 条，{len(en)} 个键")
    return result


if __name__ == "__main__":
    build()
