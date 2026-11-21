"""合并模组自带中文和 i18n 资源包，生成资源包基础文件和覆盖率报告。"""

from __future__ import annotations

import json
from pathlib import Path

from common import (
    AUTHOR_MODS,
    EXTRACTED,
    MODS_WITHOUT_LANG,
    REPORTS,
    RESOURCEPACK,
    asset_namespace,
    ensure_dirs,
    find_jar,
    jar_lang,
    read_json,
    write_json,
)
from strainers_patch import extra_en, extra_zh

SUPPLEMENTS = {
    "ftbteams": "ftb-teams-neoforge",
    "elevatorid": "elevatorid-neoforge",
    "compressium": "compressium",
    "camol": "camol",
    "chisel": "chisel",
    "framedblocks": "FramedBlocks",
    "ftbchunks": "ftb-chunks",
    "jei": "jei-",
    "ftbquests": "ftb-quests",
    "ftbfiltersystem": "ftb-filter-system",
    "extremesoundmuffler": "ExtremeSoundMuffler",
    "inventoryessentials": "inventoryessentials",
    "skyblockbuilder": "SkyblockBuilder",
    "cabletiers": "cabletiers",
    "rsinsertexportupgrade": "refinedwirelessupgrades",
    "pipe_connector": "pipe_connector",
    "enderio_endergy": "enderio_endergy",
    "mysticalagriculture": "MysticalAgriculture",
    "mysticalagradditions": "MysticalAgradditions",
    "growthacceleratortiers": "growthacceleratortiers",
    "aeinfinitybooster": "aeinfinitybooster",
    "extendedae": "ExtendedAE",
    "ironfurnaces": "ironfurnaces",
    "alltheores": "alltheores",
    "functionalstorage": "functionalstorage",
    "refinedstorage": "refinedstorage-neoforge",
    "waystones": "waystones",
    "jade": "Jade",
    "ftblibrary": "ftb-library",
    "advanced_ae": "AdvancedAE",
    "constructionstick": "ConstructionSticks",
    "justenoughrecipesharing": "justenoughrecipesharing",
}


def load_optional(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return read_json(path)


def main() -> None:
    ensure_dirs()
    rows = []
    conflicts = []
    totals = {"en": 0, "repo": 0, "mod": 0, "i18n": 0, "missing": 0}

    for namespace in AUTHOR_MODS:
        en_path = EXTRACTED / "mods" / namespace / "en_us.json"
        if not en_path.exists():
            continue
        en = read_json(en_path)
        if namespace == "strainers":
            en.update(extra_en())
        mod_zh = load_optional(EXTRACTED / "mods" / namespace / "zh_cn.json")
        i18n_zh = load_optional(EXTRACTED / "i18n" / f"{namespace}.json")
        out_path = RESOURCEPACK / "assets" / asset_namespace(namespace) / "lang" / "zh_cn.json"
        repo_zh = load_optional(out_path)
        fallback_zh = extra_zh() if namespace == "strainers" else {}

        merged: dict[str, str] = {}
        counts = {"repo": 0, "mod": 0, "i18n": 0, "missing": 0}
        for key, english in en.items():
            if repo_zh.get(key):
                merged[key] = repo_zh[key]
                counts["repo"] += 1
            elif mod_zh.get(key):
                merged[key] = mod_zh[key]
                counts["mod"] += 1
            elif i18n_zh.get(key):
                merged[key] = i18n_zh[key]
                counts["i18n"] += 1
            elif fallback_zh.get(key):
                merged[key] = fallback_zh[key]
                counts["repo"] += 1
            else:
                counts["missing"] += 1

            if mod_zh.get(key) and i18n_zh.get(key) and mod_zh[key] != i18n_zh[key]:
                conflicts.append(
                    {
                        "namespace": namespace,
                        "key": key,
                        "en": english,
                        "mod": mod_zh[key],
                        "i18n": i18n_zh[key],
                        "used": "mod",
                    }
                )

        write_json(out_path, merged)
        total = len(en)
        translated = total - counts["missing"]
        rows.append(
            {
                "namespace": namespace,
                "total": total,
                **counts,
                "coverage": translated / total if total else 1.0,
            }
        )
        totals["en"] += total
        totals["repo"] += counts["repo"]
        totals["mod"] += counts["mod"]
        totals["i18n"] += counts["i18n"]
        totals["missing"] += counts["missing"]
        print(
            f"{namespace:18} 共 {total:5}，仓库 {counts['repo']:4}，"
            f"模组 {counts['mod']:3}，i18n {counts['i18n']:5}，缺失 {counts['missing']:4}"
        )

    supplement_rows = []
    for namespace, prefix in SUPPLEMENTS.items():
        en = jar_lang(find_jar(prefix), namespace, "en_us") or {}
        zh = load_optional(RESOURCEPACK / "assets" / asset_namespace(namespace) / "lang" / "zh_cn.json")
        translated = sum(1 for key in en if zh.get(key))
        supplement_rows.append(
            {
                "namespace": namespace,
                "total": len(en),
                "translated": translated,
                "coverage": translated / len(en) if en else 1.0,
            }
        )
        print(f"补充 {namespace:16} 共 {len(en):5}，已译 {translated:5}")

    (REPORTS / "review").mkdir(parents=True, exist_ok=True)
    write_json(REPORTS / "review" / "conflicts.json", conflicts)
    write_json(REPORTS / "coverage.json", {"mods": rows, "supplements": supplement_rows, "totals": totals})

    lines = [
        "# 覆盖率报告",
        "",
        f"生成时间：自动生成，数据来自 `work/extracted/`。",
        "",
        "## 作者模组",
        "",
        "| 命名空间 | 总条目 | 仓库译文 | 模组自带 | i18n 资源包 | 缺失 | 覆盖率 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda item: (-item["missing"], item["namespace"])):
        lines.append(
            f"| {row['namespace']} | {row['total']} | {row['repo']} | {row['mod']} | "
            f"{row['i18n']} | {row['missing']} | {row['coverage']:.1%} |"
        )
    lines.append(
        f"| **合计** | **{totals['en']}** | **{totals['repo']}** | **{totals['mod']}** | "
        f"**{totals['i18n']}** | **{totals['missing']}** | "
        f"**{(totals['en'] - totals['missing']) / totals['en']:.1%}** |"
    )
    lines += [
        "",
        "## 补充模组",
        "",
        "| 命名空间 | 总条目 | 已译 | 覆盖率 |",
        "|---|---:|---:|---:|",
    ]
    for row in supplement_rows:
        lines.append(
            f"| {row['namespace']} | {row['total']} | {row['translated']} | {row['coverage']:.1%} |"
        )
    lines += [
        "",
        "## 任务书",
        "",
        "| 范围 | 已翻译 | 说明 |",
        "|---|---:|---|",
        "| 章节、任务、子标题、任务要求标题 | 111 | 全部 |",
        "| 任务正文 | 531 | 中英双语，中文块 → 分割线 → 英文块 |",
        "",
        "## 自定义内容",
        "",
        "| 范围 | 已翻译 | 说明 |",
        "|---|---:|---|",
        "| KubeJS 物品名称 | 82 | `kubejs/assets/caveopolis/lang/zh_cn.json` |",
        "| KubeJS 方块名称 | 32 | 同上，`block.caveopolis.*` |",
        "| 玩家提示 | 3 | 翻译键 |",
        "| 商店等级与自定义语言 | 33 | `Translations.js` 的 `zh_cn` 块 |",
        "| JEI 分组名 | 34 | 直接写中文 |",
        "| 奇点名称 | 9 | 翻译键，配置位于 `config/extendedcrafting/singularities/` |",
        "| 交易员名称 | 5 | 直接写中文 |",
        "| 商店物品自定义名称 | 3 | 直接写中文 |",
        "| 折叠分组名 | 871 | 规则生成 |",
        "| 出生点告示牌 | 20 | `config/skyblockbuilder/templates/islands/spawn.snbt` |",
        f"| 通用模组补充 | {sum(row['translated'] for row in supplement_rows if row['namespace'] not in ('compressium', 'camol', 'chisel', 'framedblocks'))} | FTB、JEI、Mystical Agriculture 等，见「补充模组」表 |",
        "| Compressium | 225 | 153 条 `block.*` → `item.*` 重映射 + 72 条补译 |",
        "| Camol | 10 | 伪装方块模组，手工翻译 |",
        "| Chisel | 38008 | 370 个不同方块名 + 1,263 条不同说明，映射回全部键 |",
        "| FramedBlocks | 681 | 保留模组自带 107 条，补齐 574 条 |",
        "",
        "## 说明",
        "",
        "- 仓库译文指 `resourcepack/` 中已经存在的条目。",
        "- 模组自带中文优先于 i18n 资源包。",
        "- 没有语言文件的模组："
        + "、".join(sorted(MODS_WITHOUT_LANG))
        + "。",
        "",
    ]
    (REPORTS / "coverage.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"合计：{totals}")


if __name__ == "__main__":
    main()
