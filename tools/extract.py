"""从参考资料提取待翻译文本。"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from common import (
    AUTHOR_MODS,
    EXTRACTED,
    I18N,
    MODS_WITHOUT_LANG,
    OVERRIDES,
    author_lang_files,
    ensure_dirs,
    jar_lang,
    write_json,
)
from strainers_patch import extra_en

COLORS = [
    "red",
    "green",
    "blue",
    "yellow",
    "purple",
    "cyan",
    "white",
    "orange",
    "magenta",
    "light_blue",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "black",
    "brown",
]

ROMAN = {
    "i": "I",
    "ii": "II",
    "iii": "III",
    "iv": "IV",
    "v": "V",
    "vi": "VI",
    "vii": "VII",
    "viii": "VIII",
    "ix": "IX",
    "x": "X",
}


def title_case(path: str) -> str:
    words = []
    for word in path.split("_"):
        words.append(ROMAN.get(word, word[:1].upper() + word[1:]))
    return " ".join(words)


def extract_author_mods() -> None:
    out = EXTRACTED / "mods"
    for namespace, jar in author_lang_files():
        folder = out / namespace
        folder.mkdir(parents=True, exist_ok=True)
        en = jar_lang(jar, namespace, "en_us")
        zh = jar_lang(jar, namespace, "zh_cn")
        if en is None:
            print(f"{namespace}: 没有 en_us 语言文件（{jar.name}）")
            (folder / "NO_EN_US").write_text("", encoding="utf-8")
            continue
        if namespace == "strainers":
            en.update(extra_en())
        write_json(folder / "en_us.json", en)
        if zh is not None:
            write_json(folder / "zh_cn.json", zh)
        print(f"{namespace}: en_us {len(en)} 条，自带中文 {len(zh or {})} 条")
    for namespace in MODS_WITHOUT_LANG:
        (out / namespace / "NO_LANG").parent.mkdir(parents=True, exist_ok=True)
        (out / namespace / "NO_LANG").write_text("", encoding="utf-8")


def extract_i18n() -> None:
    out = EXTRACTED / "i18n"
    count = 0
    for path in sorted((I18N / "assets").glob("*/lang/zh_cn.json")):
        namespace = path.parent.parent.name
        data = json.loads(path.read_text(encoding="utf-8"))
        write_json(out / f"{namespace}.json", data)
        count += 1
    print(f"i18n 资源包：{count} 个命名空间")


def extract_quests() -> None:
    src = OVERRIDES / "config" / "ftbquests" / "quests" / "lang" / "en_us"
    dst = EXTRACTED / "quests" / "en_us"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    total = sum(1 for _ in dst.rglob("*") if _.is_file())
    print(f"任务书：复制 {total} 个语言文件")


def extract_collapsiblegroups() -> None:
    src = OVERRIDES / "config" / "collapsiblegroups" / "lang" / "en_us.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    write_json(EXTRACTED / "collapsiblegroups" / "en_us.json", data)
    print(f"折叠分组：{len(data)} 条分组名")


def extract_translations_js() -> dict[str, str]:
    text = (OVERRIDES / "kubejs" / "client_scripts" / "Translations.js").read_text(encoding="utf-8")
    entries = {}
    for match in re.finditer(r'event\.add\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*\)', text):
        entries[match.group(1)] = match.group(2)
    return entries


def extract_items_js() -> list[dict]:
    text = (OVERRIDES / "kubejs" / "startup_scripts" / "Items.js").read_text(encoding="utf-8")
    items: dict[str, dict] = {}

    def add_item(item_id: str) -> dict:
        path = item_id.split(":", 1)[1]
        return items.setdefault(
            item_id,
            {
                "id": item_id,
                "key": f"item.caveopolis.{path}",
                "en": title_case(path),
                "display_name": None,
                "tooltip": None,
            },
        )

    starts = [match for match in re.finditer(r"event\.create\(\s*'([^']+)'", text)]
    for index, match in enumerate(starts):
        item_id = match.group(1)
        if not item_id.startswith("caveopolis:"):
            continue
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[match.start() : end]
        record = add_item(item_id)
        display = re.search(r"\.displayName\(\s*(?:'([^']*)'|\"([^\"]*)\")\s*\)", block)
        tooltip = re.search(r"\.tooltip\(\s*(?:'([^']*)'|\"([^\"]*)\")\s*\)", block)
        if display:
            record["display_name"] = display.group(1) or display.group(2)
        if tooltip:
            record["tooltip"] = tooltip.group(1) or tooltip.group(2)

    for color in COLORS:
        add_item(f"caveopolis:{color}_shimmer_crystal")

    return sorted(items.values(), key=lambda item: item["id"])


def extract_player_messages() -> list[dict]:
    text = (OVERRIDES / "kubejs" / "server_scripts" / "ServerEvents.js").read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    messages = []
    for match in re.finditer(r"player\.tell\(\s*(?:'([^']*)'|`([^`]*)`)\s*\)", text):
        messages.append({"en": match.group(1) or match.group(2)})
    return messages


def extract_jei_groups() -> list[dict]:
    root = OVERRIDES / "kubejs" / "assets" / "caveopolis" / "jei_groups"
    groups = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        groups.append(
            {
                "file": str(path.relative_to(OVERRIDES)),
                "name": data.get("name", ""),
                "icon": data.get("icon", ""),
            }
        )
    return groups


def extract_singularities() -> list[dict]:
    root = OVERRIDES / "config" / "singularities"
    singularities = []
    for path in sorted(root.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        singularities.append(
            {
                "file": str(path.relative_to(OVERRIDES)),
                "id": path.stem,
                "name": data.get("name", ""),
            }
        )
    return singularities


def extract_traders() -> list[dict]:
    path = OVERRIDES / "kubejs" / "data" / "shops" / "data_maps" / "block" / "trader_names.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        {"block": block, "name": name}
        for block, names in data.get("values", {}).items()
        for name in names
    ]


def extract_shop_custom_names() -> list[dict]:
    text = (OVERRIDES / "kubejs" / "server_scripts" / "mods" / "Shops.js").read_text(encoding="utf-8")
    names = []
    for match in re.finditer(r'custom_name="([^"]+)"', text):
        names.append({"en": match.group(1)})
    return names


def extract_custom() -> None:
    inventory = {
        "translations_js": extract_translations_js(),
        "items": extract_items_js(),
        "player_messages": extract_player_messages(),
        "jei_groups": extract_jei_groups(),
        "singularities": extract_singularities(),
        "traders": extract_traders(),
        "shop_custom_names": extract_shop_custom_names(),
    }
    write_json(EXTRACTED / "custom" / "inventory.json", inventory)
    print(
        "自定义内容："
        f"{len(inventory['translations_js'])} 条客户端语言，"
        f"{len(inventory['items'])} 个物品，"
        f"{len(inventory['player_messages'])} 条玩家提示，"
        f"{len(inventory['jei_groups'])} 个 JEI 分组，"
        f"{len(inventory['singularities'])} 个奇点，"
        f"{len(inventory['traders'])} 个交易员名称，"
        f"{len(inventory['shop_custom_names'])} 个商店自定义名称"
    )


def main() -> None:
    ensure_dirs()
    extract_author_mods()
    extract_i18n()
    extract_quests()
    extract_collapsiblegroups()
    extract_custom()


if __name__ == "__main__":
    main()
