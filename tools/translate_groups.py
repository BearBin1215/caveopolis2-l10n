"""按名称规则生成折叠分组名的中文。"""

from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path

from common import CONFIG, EXTRACTED, read_json, write_json

COLORS = {
    "Black": "黑色",
    "Blue": "蓝色",
    "Brown": "棕色",
    "Cyan": "青色",
    "Gray": "灰色",
    "Green": "绿色",
    "Light Blue": "淡蓝色",
    "Light Gray": "淡灰色",
    "Lime": "黄绿色",
    "Magenta": "品红色",
    "Orange": "橙色",
    "Pink": "粉红色",
    "Purple": "紫色",
    "Red": "红色",
    "White": "白色",
    "Yellow": "黄色",
}

WOODS = {
    "Oak": "橡木",
    "Spruce": "云杉木",
    "Birch": "白桦木",
    "Jungle": "丛林木",
    "Acacia": "金合欢木",
    "Dark Oak": "深色橡木",
    "Mangrove": "红树木",
    "Cherry": "樱花木",
    "Bamboo": "竹",
    "Crimson": "绯红菌",
    "Warped": "诡异菌",
}

METALS = {
    "Aluminum": "铝",
    "Bronze": "青铜",
    "Cobalt": "钴",
    "Electrum": "琥珀金",
    "Invar": "殷钢",
    "Nickel": "镍",
    "Platinum": "铂",
    "Silver": "银",
    "Steel": "钢",
    "Tin": "锡",
    "Uranium": "铀",
}

EXACT = {
    # 折叠分组的同形词与官方方块组名
    "Lead Blocks": "铅块",
    "Crimson Bookshelf": "绯红木书架",
    "Warped Bookshelf": "诡异木书架",
    # 原版方块
    "Acacia Door": "金合欢木门", "Acacia Leaves": "金合欢树叶", "Acacia Log": "金合欢原木",
    "Acacia Planks": "金合欢木板", "Acacia Trapdoor": "金合欢木活板门",
    "Birch Door": "白桦木门", "Birch Leaves": "白桦树叶", "Birch Log": "白桦原木",
    "Birch Planks": "白桦木板", "Birch Trapdoor": "白桦木活板门",
    "Cherry Door": "樱花木门", "Cherry Log": "樱花原木", "Cherry Trapdoor": "樱花木活板门",
    "Crimson Door": "绯红木门", "Crimson Fungus": "绯红菌", "Crimson Roots": "绯红菌索",
    "Crimson Stem": "绯红菌柄", "Crimson Trapdoor": "绯红木活板门",
    "Dark Oak Door": "深色橡木门", "Dark Oak Leaves": "深色橡树叶", "Dark Oak Log": "深色橡木原木",
    "Dark Oak Trapdoor": "深色橡木活板门",
    "Jungle Door": "丛林木门", "Jungle Leaves": "丛林树叶", "Jungle Log": "丛林原木",
    "Jungle Trapdoor": "丛林木活板门",
    "Mangrove Door": "红树木门", "Mangrove Log": "红树原木", "Mangrove Roots": "红树根",
    "Mangrove Trapdoor": "红树木活板门",
    "Oak Door": "橡木门", "Oak Leaves": "橡树叶", "Oak Log": "橡木原木", "Oak Trapdoor": "橡木活板门",
    "Spruce Door": "云杉木门", "Spruce Leaves": "云杉树叶", "Spruce Log": "云杉原木",
    "Spruce Trapdoor": "云杉木活板门",
    "Warped Door": "诡异木门", "Warped Fungus": "诡异菌", "Warped Roots": "诡异菌索",
    "Warped Stem": "诡异菌柄", "Warped Trapdoor": "诡异木活板门",
    "Stripped Acacia Log": "去皮金合欢原木", "Stripped Birch Log": "去皮白桦原木",
    "Stripped Cherry Log": "去皮樱花原木", "Stripped Crimson Stem": "去皮绯红菌柄",
    "Stripped Dark Oak Log": "去皮深色橡木原木", "Stripped Jungle Log": "去皮丛林原木",
    "Stripped Mangrove Log": "去皮红树原木", "Stripped Oak Log": "去皮橡木原木",
    "Stripped Spruce Log": "去皮云杉原木", "Stripped Warped Stem": "去皮诡异菌柄",
    "Ancient Debris": "远古残骸", "Amethyst Block": "紫水晶块", "Andesite": "安山岩",
    "Antiblock": "反方块", "Barrel": "木桶", "Basalt": "玄武岩", "Blackstone": "黑石",
    "Blue Ice": "蓝冰", "Bone Block": "骨块", "Bookshelf": "书架",
    "Borderless Bricks": "无边框砖块", "Bricks": "砖块", "Brown Mushroom": "棕色蘑菇",
    "Brown Mushroom Block": "棕色蘑菇方块", "Brownstone": "棕石", "Calcite": "方解石",
    "Carved Pumpkin": "雕刻南瓜", "Charcoal": "木炭", "Clay": "黏土", "Cloud": "云",
    "Coal": "煤炭", "Coal Block": "煤炭块", "Cobbled Deepslate": "深板岩圆石",
    "Cobblestone": "圆石", "Cobweb": "蜘蛛网", "Copper Block": "铜块", "Crimson Planks": "绯红木板",
    "Crying Obsidian": "哭泣的黑曜石", "Cubits": "立方拼片", "Deepslate": "深板岩",
    "Diabase": "辉绿岩", "Diamond": "钻石", "Diamond Block": "钻石块", "Diorite": "闪长岩",
    "Dirt": "泥土", "Dried Kelp Block": "干海带块", "Dripstone Block": "滴水石块",
    "Emerald": "绿宝石", "Emerald Block": "绿宝石块", "End Stone": "末地石",
    "Factory": "工厂风格", "Fantasy": "奇幻风格", "Fantasy 2": "奇幻风格 2",
    "Futura": "未来风格", "Gilded Blackstone": "镶金黑石", "Glass": "玻璃",
    "Glass Pane": "玻璃板", "Glowstone": "荧石", "Gold": "金", "Gold Block": "金块",
    "Granite": "花岗岩", "Gravel": "沙砾", "Hay Block": "干草块", "Holystone": "圣石",
    "Ice": "冰", "Ice Pillar": "冰柱", "Iron": "铁", "Iron Bars": "铁栏杆",
    "Iron Block": "铁块", "Iron Pane": "铁栏杆", "Jack O Lantern": "南瓜灯",
    "Laboratory": "实验室风格", "Ladder": "梯子", "Lantern": "灯笼", "Lapis": "青金石",
    "Lapis Block": "青金石块", "Lavastone": "熔岩石", "Limestone": "石灰岩",
    "Lily Pad": "睡莲", "Lodestone": "磁石", "Magma Block": "岩浆块", "Marble": "大理石",
    "Marble Pillar": "大理石柱", "Melon": "西瓜", "Moss Block": "苔藓块",
    "Mossy Cobblestone": "苔石", "Mossy Stone Bricks": "苔石砖", "Mud": "泥",
    "Mud Bricks": "泥砖", "Mushroom Stem": "蘑菇柄", "Nether Brick": "下界砖",
    "Nether Bricks": "下界砖块", "Nether Sprouts": "下界苗", "Nether Wart Block": "下界疣块",
    "Netherite Block": "下界合金块", "Netherrack": "下界岩", "Obsidian": "黑曜石",
    "Ochre Froglight": "赭黄蛙明灯", "Packed Ice": "浮冰", "Packed Mud": "泥坯",
    "Paper": "纸", "Pearlescent Froglight": "珠光蛙明灯", "Pointed Dripstone": "滴水石锥",
    "Prismarine": "海晶石", "Prismarine Bricks": "海晶石砖", "Pumpkin": "南瓜",
    "Purpur": "紫珀", "Purpur Block": "紫珀块", "Quartz": "石英", "Quartz Block": "石英块",
    "Raw Copper Block": "粗铜块", "Raw Gold Block": "粗金块", "Raw Iron Block": "粗铁块",
    "Red Mushroom": "红色蘑菇", "Red Mushroom Block": "红色蘑菇方块",
    "Red Nether Bricks": "红色下界砖块", "Red Sandstone": "红砂岩",
    "Red Sandstone Scribbles": "红砂岩涂鸦", "Redstone": "红石", "Redstone Block": "红石块",
    "Redstone Lamp": "红石灯", "Redstone Torch": "红石火把", "Sand": "沙子",
    "Sandstone": "砂岩", "Sandstone Scribbles": "砂岩涂鸦", "Sea Lantern": "海晶灯",
    "Shroomlight": "菌光体", "Smooth Stone": "平滑石头", "Snow Block": "雪块",
    "Soul Lantern": "灵魂灯笼", "Soul Sand": "灵魂沙", "Special Lantern": "特殊灯笼",
    "Special Soul Lantern": "特殊灵魂灯笼", "Sponge": "海绵", "Spruce Planks": "云杉木板",
    "Stone": "石头", "Stone Bricks": "石砖", "Technical": "科技风格", "Temple": "神庙风格",
    "Mossy Temple": "苔藓神庙风格", "Terracotta": "陶瓦", "Tuff": "凝灰岩",
    "Tyrian": "泰尔紫风格", "Valentines": "情人节风格", "Vine": "藤蔓", "Voidstone": "虚空石",
    "Voidstone Runic": "虚空符文石", "Voidstone Runic (Anim)": "虚空符文石（动态）",
    "Wall Torch": "墙上的火把", "Warning": "警告标志", "Warped Planks": "诡异木板",
    "Warped Wart Block": "诡异疣块", "Waterstone": "水石", "Waxed Copper Block": "涂蜡的铜块",
    "Waxed Exposed Copper Block": "涂蜡的斑驳铜块", "Waxed Oxidized Copper": "涂蜡的氧化铜块",
    "Waxed Weathered Copper": "涂蜡的锈蚀铜块",
    # 分类
    "Abyssal Shroud Scrolls": "深渊庇佑卷轴", "Acid Orb Scrolls": "酸液球卷轴",
    "Acupuncture Scrolls": "猩红刺狱卷轴", "Angel Wing Scrolls": "天使之翼卷轴",
    "Arrow Volley Scrolls": "万箭齐发卷轴", "Ascension Scrolls": "飞升卷轴",
    "Ball Lightning Scrolls": "闪电球卷轴", "Black Hole Scrolls": "黑洞卷轴",
    "Blaze Storm Scrolls": "烈焰风暴卷轴", "Blessing of Life Scrolls": "生命祝福卷轴",
    "Blight Scrolls": "枯萎术卷轴", "Blood Needles Scrolls": "猩红之刺卷轴",
    "Blood Slash Scrolls": "猩红斩击卷轴", "Blood Step Scrolls": "血步卷轴",
    "Burning Dash Scrolls": "烈焰冲锋卷轴", "Chain Creeper Scrolls": "苦力怕之环卷轴",
    "Chain Lightning Scrolls": "连锁闪电卷轴", "Charge Scrolls": "超负荷卷轴",
    "Cleanse Scrolls": "净化卷轴", "Cloud of Regeneration Scrolls": "再生云域卷轴",
    "Cone of Cold Scrolls": "刺骨寒风卷轴", "Counterspell Scrolls": "法术反制卷轴",
    "Devour Scrolls": "嗜血啃咬卷轴", "Divine Smite Scrolls": "神圣打击卷轴",
    "Dragon Breath Scrolls": "龙息卷轴", "Earthquake Scrolls": "地震卷轴",
    "Echoing Strikes Scrolls": "回响打击卷轴", "Eldritch Blast Scrolls": "邪术冲击波卷轴",
    "Electrocute Scrolls": "电刑卷轴", "Evasion Scrolls": "末影闪避卷轴",
    "Fang Strike Scrolls": "唤魔尖牙卷轴", "Fang Ward Scrolls": "尖牙之环卷轴",
    "Fire Arrow Scrolls": "爆裂炽焰箭卷轴", "Fire Breath Scrolls": "火焰吐息卷轴",
    "Fireball Scrolls": "火球术卷轴", "Firebolt Scrolls": "火焰箭卷轴",
    "Firecracker Scrolls": "烟火四射卷轴", "Firefly Swarm Scrolls": "萤火虫群卷轴",
    "Flaming Barrage Scrolls": "炽焰追踪弹幕卷轴", "Flaming Strike Scrolls": "炽焰斩击卷轴",
    "Fortify Scrolls": "神圣守护卷轴", "Frost Step Scrolls": "霜步卷轴",
    "Frostbite Scrolls": "霜噬卷轴", "Frostwave Scrolls": "冰浪卷轴",
    "Gluttony Scrolls": "暴食卷轴", "Greater Heal Scrolls": "强效治疗卷轴",
    "Guiding Bolt Scrolls": "曳光弹卷轴", "Gust Scrolls": "呼啸之风卷轴",
    "Haste Scrolls": "急迫卷轴", "Heal Scrolls": "治疗卷轴",
    "Healing Circle Scrolls": "治愈之环卷轴", "Heartstop Scrolls": "止心术卷轴",
    "Heat Surge Scrolls": "焰涌卷轴", "Ice Block Scrolls": "霜降卷轴",
    "Ice Spikes Scrolls": "冰霜尖刺卷轴", "Ice Tomb Scrolls": "冰霜之墓卷轴",
    "Icicle Scrolls": "冰霜箭卷轴", "Invisibility Scrolls": "隐身术卷轴",
    "Lightning Bolt Scrolls": "落雷卷轴", "Lightning Lance Scrolls": "雷鸣长枪卷轴",
    "Lob Creeper Scrolls": "苦力怕迫击炮卷轴", "Magic Arrow Scrolls": "魔法箭卷轴",
    "Magic Missile Scrolls": "魔法飞弹卷轴", "Magma Bomb Scrolls": "岩浆炸弹卷轴",
    "Oakskin Scrolls": "橡肤卷轴", "Planar Sight Scrolls": "位面视觉卷轴",
    "Pocket Dimension Scrolls": "口袋维度卷轴", "Poison Arrow Scrolls": "毒箭射击卷轴",
    "Poison Breath Scrolls": "毒气吐息卷轴", "Poison Splash Scrolls": "毒液飞溅卷轴",
    "Portal Scrolls": "传送门卷轴", "Raise Dead Scrolls": "驱役亡灵卷轴",
    "Raise Hell Scrolls": "地狱浮现卷轴", "Ray of Frost Scrolls": "冰霜射线卷轴",
    "Ray of Siphoning Scrolls": "血吸光束卷轴", "Recall Scrolls": "回溯卷轴",
    "Root Scrolls": "纠缠根须卷轴", "Sacrifice Scrolls": "献祭卷轴",
    "Scorch Scrolls": "灼烧卷轴", "Sculk Tentacles Scrolls": "幽匿之触卷轴",
    "Shadow Slash Scrolls": "暗影斩击卷轴", "Shield Scrolls": "护盾术卷轴",
    "Shockwave Scrolls": "震荡波卷轴", "Slow Scrolls": "迟缓卷轴",
    "Snowball Scrolls": "雪球术卷轴", "Sonic Boom Scrolls": "音爆卷轴",
    "Spectral Hammer Scrolls": "幽冥锤卷轴", "Spider Aspect Scrolls": "蛛毒之相卷轴",
    "Starfall Scrolls": "星海落瀑卷轴", "Stomp Scrolls": "践踏卷轴",
    "Summon Ender Chest Scrolls": "召唤末影箱卷轴", "Summon Horse Scrolls": "召唤骏马卷轴",
    "Summon Polar Bear Scrolls": "召唤北极熊卷轴", "Summon Swords Scrolls": "召唤利剑卷轴",
    "Summon Vex Scrolls": "召唤恼鬼卷轴", "Sunbeam Scrolls": "烈阳射线卷轴",
    "Telekinesis Scrolls": "念力卷轴", "Teleport Scrolls": "传送术卷轴",
    "Throw Scrolls": "投掷卷轴", "Thunder Step Scrolls": "雷步卷轴",
    "Thunderstorm Scrolls": "雷暴卷轴", "Touch Dig Scrolls": "点石成掘卷轴",
    "Volt Strike Scrolls": "伏特打击卷轴", "Wall of Fire Scrolls": "火墙术卷轴",
    "Wisp Scrolls": "圣灵卷轴", "Wither Skull Scrolls": "凋灵之首卷轴",
    "Wololo Scrolls": "Wololo 卷轴",
    # 宝石
    "Ballast Gems": "稳定宝石", "Brawler's Gems": "斗争宝石", "Breach Gems": "突破宝石",
    "Combatant Gems": "战斗宝石", "Guardian Gems": "护卫宝石", "Lightning Gems": "闪电宝石",
    "Lunar Gems": "月华宝石", "Samurai Gems": "武士宝石", "Slipstream Gems": "逸流宝石",
    "Solar Gems": "阳炎宝石", "Splendor Gems": "辉煌宝石", "Tyrannical Gems": "暴君宝石",
    "Warlord Gems": "战神宝石", "Earth Gems": "大地宝石", "Royalty Gems": "王室宝石",
    "Verdant Ruin Gems": "翠殒宝石", "Endersurge Gems": "影激宝石",
    "Mageslayer Gems": "法师克星宝石", "Blood Lord Gems": "嗜血领主宝石", "Inferno Gems": "炽狱宝石",
    "Molten Breach Gems": "熔融突破宝石", "TwilightForest Gems": "暮色森林宝石",
    "Frozen Queen Gems": "冰雪女王宝石", "Potion Charms": "药水护符",
    # AE2 与 RS2
    "Colored Covered Cables": "彩色包层线缆", "Colored Dense Covered Cables": "彩色致密包层线缆",
    "Colored Glass Cables": "彩色玻璃线缆", "Colored Smart Cables": "彩色智能线缆",
    "Colored Dense Smart Cables": "彩色致密智能线缆", "Lumen Paint Balls": "光通染色球",
    "Paint Balls": "染色球", "Colored Autocrafter Managers": "彩色自动合成仓管理器",
    "Colored Autocrafters": "彩色自动合成仓", "Colored Autocrafting Monitors": "彩色合成监视器",
    "Colored Cables": "彩色线缆", "Colored Constructors": "彩色成型面板",
    "Colored Controllers": "彩色控制器", "Colored Crafting Grids": "彩色合成终端",
    "Colored Creative Controllers": "彩色创造控制器", "Colored Destructors": "彩色破坏面板",
    "Colored Detectors": "彩色网络物品检测器", "Colored Disk Interfaces": "彩色磁盘接口",
    "Colored Exporters": "彩色输出总线", "Colored External Storages": "彩色外部存储总线",
    "Colored Grids": "彩色终端", "Colored Importers": "彩色输入总线",
    "Colored Network Receivers": "彩色网络接收器", "Colored Network Transmitters": "彩色网络变送器",
    "Colored Pattern Grids": "彩色样板终端", "Colored Relays": "彩色中继器",
    "Colored Security Managers": "彩色权限管理器", "Colored Wireless Transmitters": "彩色无线访问点",
    "Enchanted Books": "附魔书", "Clear Glasses": "纯净玻璃", "Filled Soul vials": "装满的灵魂瓶",
    "Fused Quartzs": "石英玻璃", "Music Discs": "音乐唱片", "Paintings": "画",
    "Potions": "药水", "Pottery Sherds": "陶片", "Lingering Potions": "滞留药水",
    "Splash Potions": "喷溅药水", "Tipped Arrows": "药箭",
    "Vanilla Banners": "原版旗帜", "Vanilla Beds": "原版床", "Vanilla Candles": "原版蜡烛",
    "Vanilla Carpets": "原版地毯", "Vanilla Colored Glass Blocks": "原版染色玻璃",
    "Vanilla Colored Glass Panes": "原版染色玻璃板", "Vanilla Colored Shulker Boxes": "原版彩色潜影盒",
    "Vanilla Concrete Powders": "原版混凝土粉末", "Vanilla Concretes": "原版混凝土",
    "Vanilla Glazed Terracottas": "原版带釉陶瓦", "Vanilla Terracottas": "原版陶瓦",
    "Vanilla Wools": "原版羊毛",
}

SUFFIXES = {
    "Blocks": "块",
    "Doors": "门",
    "Trapdoors": "活板门",
    "Bridges": "桥",
    "Piers": "桥梁支架",
    "Stairs": "楼梯",
    "Fences": "栅栏",
    "Walls": "墙",
    "Paths": "路径",
    "Roofs": "屋顶",
    "Windows": "窗户",
    "Lights": "灯",
    "Lamps": "灯",
    "Torches": "火把",
    "Lanterns": "灯笼",
    "Gates": "大门",
    "Grids": "终端",
    "Scrolls": "卷轴",
    "Gems": "宝石",
}

MODIFIERS = {
    "Bamboo": "竹",
    "Glass": "玻璃",
    "Log": "原木",
    "Metal": "金属",
    "Rail": "铁轨",
    "Rope": "绳",
    "Special": "特殊",
    "Stone": "石",
    "Wooden": "木",
    "Bark": "树皮",
    "Barn": "谷仓",
    "Beach": "海滩",
    "Classic": "经典",
    "Cottage": "小屋",
    "Four Panel": "四格",
    "Garage": "车库",
    "Modern": "现代",
    "Mystic": "神秘",
    "Nether": "下界",
    "Paper": "纸",
    "Shoji": "障子",
    "Shoji Whole": "整面障子",
    "Stable": "马厩",
    "Stable Head": "马厩半截",
    "Swamp": "沼泽",
    "Tropical": "热带",
    "Waffle": "华夫",
    "Western": "西部",
    "Whispering": "低语",
    "Barred": "栅栏",
    "Barrel": "木桶",
    "Blossom": "花绽",
    "Ranch": "牧场",
    "Attic": "阁楼",
    "Gutter": "檐槽",
    "Lower": "下层",
    "Upper": "上层",
    "Steep": "陡坡",
    "Striped": "条纹",
    "Top": "顶层",
    "Bulk": "宽体",
    "Compact": "紧凑",
    "Loft": "阁楼",
    "Skyline": "天际",
    "Terrace": "露台",
}

PREFIXES = {
    "Chipped": "Chipped",
    "Chisel": "Chisel",
    "Rechiseled": "Rechiseled",
    "AE2": "AE2",
    "RS2": "RS2",
    "Macaw's Bridges": "Macaw's Bridges",
    "Macaw's Doors": "Macaw's Doors",
    "Macaw's Fences": "Macaw's Fences",
    "Macaw's Furnitures": "Macaw's Furnitures",
    "Macaw's Lights": "Macaw's Lights",
    "Macaw's Paths": "Macaw's Paths",
    "Macaw's Roofs": "Macaw's Roofs",
    "Macaw's Stairs": "Macaw's Stairs",
    "Macaw's Trapdoors": "Macaw's Trapdoors",
    "Macaw's Windows": "Macaw's Windows",
}

# Macaw's 系列分类直接给出译名，避免逐词拼接得到不自然的名称。
MACAW = {
    "Bamboo Bridges": "竹桥", "Bamboo Piers": "竹桥墩", "Bamboo Stairs": "竹楼梯",
    "Glass Bridges": "玻璃桥", "Log Bridges": "原木桥", "Log Stairs": "原木楼梯",
    "Metal Bridges": "金属桥", "Rail Bridges": "铁轨桥", "Rope Bridges": "绳桥",
    "Rope Stairs": "绳索桥阶梯", "Special Bridges": "特殊桥", "Stone Bridges": "石桥",
    "Stone Piers": "石制桥墩", "Stone Stairs": "石楼梯", "Wooden Piers": "木桥墩",
    "Bamboo Doors": "竹门", "Bark Glass Doors": "树皮玻璃门", "Barn Doors": "谷仓门",
    "Barn Glass Doors": "谷仓玻璃门", "Beach Doors": "海滩门", "Classic Doors": "经典门",
    "Cottage Doors": "小屋门", "Four Panel Doors": "四格门", "Garage Doors": "车库门",
    "Glass Doors": "玻璃门", "Metal Doors": "金属门", "Modern Doors": "现代门",
    "Mystic Doors": "神秘门", "Nether Doors": "下界门", "Paper Doors": "纸门",
    "Portcullis": "吊闸", "Shoji Doors": "障子门", "Shoji Whole Doors": "整面障子门",
    "Special Doors": "特殊门", "Stable Doors": "马厩门", "Stable Head Doors": "马厩半截门",
    "Swamp Doors": "沼泽门", "Tropical Doors": "热带门", "Waffle Doors": "华夫门",
    "Western Doors": "西部门", "Whispering Doors": "低语门",
    "Cheval De Frise": "拒马", "Curved Double Gates": "弧形双开大门",
    "Grass Topped Walls": "草顶墙", "Hedges": "树篱", "Highley Gates": "海利门",
    "Horse Fences": "马匹栅栏", "Metal Double Gates": "金属双开大门", "Metal Fences": "金属栅栏",
    "Modern Walls": "现代墙", "Picket Fences": "尖桩栅栏", "Pillar Walls": "柱墙",
    "Pyramid Gates": "金字塔门", "Railing Gates": "栏杆大门", "Railing Walls": "栏杆墙",
    "Stockade Fences": "栅栏围墙", "Wired Fences": "铁丝栅栏",
    "Bookshelf Cupboard": "书架橱柜", "Bookshelf Drawer": "书架抽屉", "Cabinet": "橱柜",
    "Chair": "椅子", "Chaise": "躺椅", "Coffee Table": "咖啡桌", "Couch": "沙发",
    "Counter": "柜台", "Covered Desk": "带罩书桌", "Cupboard Counter": "橱柜柜台",
    "Desk": "书桌", "Double Drawer": "双抽屉", "Double Drawer Counter": "双抽屉柜台",
    "Double Wardrobe": "双门衣柜", "Drawer": "抽屉", "Drawer Counter": "抽屉柜台",
    "End Table": "边桌", "Glass Table": "玻璃桌", "Kitchen Sink": "厨房水槽",
    "Large Drawer": "大抽屉", "Lower Bookshelf Drawer": "下层书架抽屉",
    "Lower Triple Drawer": "下层三抽屉", "Modern Chair": "现代椅子",
    "Modern Desk": "现代书桌", "Modern Wardrobe": "现代衣柜", "Stool Chair": "凳子",
    "Striped Chair": "条纹椅子", "Table": "桌子", "Triple Drawer": "三抽屉",
    "Wardrobe": "衣柜",
    "Candle Holders": "烛台", "Ceiling Fan Lights": "吊扇灯", "Ceiling Lights": "吸顶灯",
    "Chains": "链条", "Chandeliers": "吊灯", "Garden Lights": "花园灯", "Lamps": "灯",
    "Lanterns": "灯笼", "Lava Lamps": "熔岩灯", "Paper Lamps": "纸灯",
    "Slab Lights": "台阶灯", "Soul Street Lamps": "灵魂路灯",
    "Soul Tiki Torches": "灵魂提基火把", "Street Lamps": "路灯", "Tiki Torches": "提基火把",
    "Torches": "火把", "Wall Lamps": "壁灯", "Wall Lanterns": "壁挂灯笼",
    "Path Stairs": "路径楼梯", "Slab Paths": "台阶路径", "Soil Paths": "泥土路径",
    "Stone Engraved Blocks": "石雕方块", "Stone Paths": "石路径",
    "Stone Pavings": "石铺路", "Wooden Paths": "木路径",
    "Attic Roofs": "天窗屋顶", "Gutter Bases": "檐槽底座", "Gutter Middles": "檐槽中段",
    "Lower Roofs": "平缓屋顶底端", "Roof Blocks": "屋顶方块", "Roof Slabs": "屋顶台阶",
    "Roofs": "屋顶", "Steep Roofs": "陡峭屋顶底端", "Striped Awnings": "条纹遮阳篷",
    "Top Roofs": "屋顶顶端", "Upper Lower Roofs": "平缓屋顶顶端",
    "Upper Steep Roofs": "陡峭屋顶顶端",
    "Balconies": "阳台", "Bulk Stairs": "厚重型楼梯", "Compact Stairs": "紧凑楼梯",
    "Loft Stairs": "阁楼楼梯", "Platforms": "平台", "Railings": "栏杆",
    "Skyline Stairs": "天际楼梯", "Terrace Stairs": "露台楼梯",
    "Bamboo Trapdoors": "竹活板门", "Bark Trapdoors": "树皮活板门",
    "Barn Trapdoors": "谷仓活板门", "Barred Trapdoors": "栅栏活板门",
    "Barrel Trapdoors": "木桶活板门", "Beach Trapdoors": "海滩活板门",
    "Blossom Trapdoors": "花绽活板门", "Classic Trapdoors": "经典活板门",
    "Cottage Trapdoors": "小屋活板门", "Four Panel Trapdoors": "四格活板门",
    "Glass Trapdoors": "玻璃活板门", "Metal Trapdoors": "金属活板门",
    "Mystic Trapdoors": "神秘活板门", "Paper Trapdoors": "纸活板门",
    "Ranch Trapdoors": "牧场活板门", "Swamp Trapdoors": "沼泽活板门",
    "Tropical Trapdoors": "热带活板门", "Whispering Trapdoors": "低语活板门",
    "Arrow Slit": "箭缝", "Blinds": "百叶窗", "Curtain Rods": "窗帘杆",
    "Curtains": "窗帘", "Gothic": "哥特式窗户", "Mosaic Glass": "马赛克玻璃",
    "Mosaic Glass Pane": "马赛克玻璃板", "Pane Windows": "玻璃板窗",
    "Parapets": "女儿墙", "Shutters": "窗扇", "Windows": "窗户",
    "Four Windows": "四格窗", "Two Windows": "双格窗",
}


def vanilla_langs() -> tuple[dict, dict]:
    zh_path = os.environ.get("MC_LANG_ZH")
    en_path = os.environ.get("MC_LANG_EN")
    if zh_path and en_path:
        return read_json(Path(zh_path)), read_json(Path(en_path))

    prism_dir = os.environ.get("PRISM_DIR")
    if not prism_dir:
        raise SystemExit("请设置 PRISM_DIR，或把 MC_LANG_ZH / MC_LANG_EN 指向原版语言文件")
    root = Path(prism_dir)
    if not root.exists():
        raise SystemExit(f"PRISM_DIR 不存在：{root}")

    indexes = sorted(
        (root / "assets" / "indexes").glob("*.json"),
        key=lambda path: int(path.stem) if path.stem.isdigit() else -1,
    )
    if not indexes:
        raise SystemExit(f"{root} 下没有资源索引")
    entry = read_json(indexes[-1])["objects"]["minecraft/lang/zh_cn.json"]
    vanilla_zh = read_json(root / "assets" / "objects" / entry["hash"][:2] / entry["hash"])

    client = Path(os.environ.get("MC_CLIENT_JAR", ""))
    if not client.is_file():
        jars = sorted(
            (root / "libraries" / "net" / "neoforged" / "minecraft-client-patched").glob(
                "*/minecraft-client-patched-*.jar"
            ),
            key=lambda path: path.stat().st_mtime,
        )
        if not jars:
            raise SystemExit(f"{root} 下没有 minecraft-client-patched jar，可用 MC_CLIENT_JAR 指定 jar 路径")
        client = jars[-1]
    with zipfile.ZipFile(client) as archive:
        vanilla_en = json.loads(archive.read("assets/minecraft/lang/en_us.json"))
    return vanilla_zh, vanilla_en


def build_name_map() -> dict[str, str]:
    vanilla_zh, vanilla_en = vanilla_langs()
    mapping: dict[str, str] = {}
    for key, english in vanilla_en.items():
        if key.startswith(("block.minecraft.", "item.minecraft.", "entity.minecraft.")):
            if isinstance(english, str) and vanilla_zh.get(key):
                mapping.setdefault(english, vanilla_zh[key])
    for namespace in EXTRACTED.joinpath("mods").iterdir():
        en_path = namespace / "en_us.json"
        i18n_path = EXTRACTED / "i18n" / f"{namespace.name}.json"
        if not en_path.exists() or not i18n_path.exists():
            continue
        en = read_json(en_path)
        zh = read_json(i18n_path)
        for key, english in en.items():
            if isinstance(english, str) and zh.get(key):
                mapping.setdefault(english, zh[key])
    return mapping


def translate_part(part: str, name_map: dict[str, str]) -> str | None:
    if part in EXACT:
        return EXACT[part]
    if part in name_map:
        return name_map[part]
    if part in MACAW:
        return MACAW[part]
    for color, color_zh in COLORS.items():
        prefix = f"{color} "
        if part.startswith(prefix):
            rest = translate_part(part[len(prefix) :], name_map)
            if rest:
                return color_zh + rest
    for wood, wood_zh in WOODS.items():
        prefix = f"{wood} "
        if part.startswith(prefix):
            rest = translate_part(part[len(prefix) :], name_map)
            if rest:
                return wood_zh + rest
    for color, color_zh in COLORS.items():
        if part == f"{color} Dyed Glass":
            return color_zh + "染色玻璃"
        if part == f"{color} Dyed Glass Pane":
            return color_zh + "染色玻璃板"
        if part == f"{color} Hexplating":
            return color_zh + "六边形板"
    words = part.split()
    if len(words) == 2 and words[0] in METALS and words[1] == "Blocks":
        return METALS[words[0]] + "块"
    words = part.split()
    if len(words) >= 2 and words[-1] in SUFFIXES:
        modifier = " ".join(words[:-1])
        translated = MODIFIERS.get(modifier) or translate_part(modifier, name_map)
        if translated:
            suffix = SUFFIXES[words[-1]]
            if suffix in ("块", "门", "墙", "桥"):
                return translated + suffix
            return translated + suffix
    if part.endswith("s"):
        singular = part[:-1]
        translated = translate_part(singular, name_map)
        if translated:
            return translated
    return None


def main() -> None:
    data = read_json(EXTRACTED / "collapsiblegroups" / "en_us.json")
    name_map = build_name_map()
    result = {}
    missing = []
    for key, english in data.items():
        if ": " in english:
            prefix, part = english.split(": ", 1)
            prefix_zh = PREFIXES.get(prefix, prefix)
            translated = translate_part(part, name_map)
            if translated:
                result[key] = f"{prefix_zh}：{translated}"
            else:
                missing.append((key, english))
                result[key] = english
        else:
            translated = translate_part(english, name_map)
            if translated:
                result[key] = translated
            else:
                missing.append((key, english))
                result[key] = english
    out = CONFIG / "collapsiblegroups" / "lang" / "zh_cn.json"
    write_json(out, result)
    print(f"生成 {len(result)} 条，未翻译 {len(missing)} 条")
    for key, english in missing:
        print(f"  {english}")


if __name__ == "__main__":
    main()
