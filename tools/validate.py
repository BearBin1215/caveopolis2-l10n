"""校验资源包、任务书和自定义内容的格式。"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

import json5ish
from common import (
    AUTHOR_MODS,
    CONFIG,
    EXTRACTED,
    KUBEJS,
    ROOT,
    REPORTS,
    RESOURCEPACK,
    asset_namespace,
    compare_tokens,
    find_jar,
    jar_lang,
    read_json,
)
from strainers_patch import extra_en

# 由 i18n 资源包或 1.21.1 迁移补充的命名空间，en_us 从模组 jar 读取。
SUPPLEMENT_MODS = {
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

problems: list[str] = []
warnings: list[str] = []


def add(message: str) -> None:
    problems.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_json_strict(path: Path) -> Any:
    seen: list[str] = []

    def hook(pairs):
        keys = [key for key, _ in pairs]
        duplicates = {key for key in keys if keys.count(key) > 1}
        if duplicates:
            seen.extend(sorted(duplicates))
        return dict(pairs)

    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)
    if seen:
        add(f"{path}: 重复键 {seen[:5]}")
    return data


def load_terms() -> list[tuple[str, str, str]]:
    terms = []
    with (ROOT / "glossary" / "terms.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            forbidden = (row.get("forbidden") or "").strip()
            for variant in forbidden.split("|"):
                if variant:
                    terms.append((row["term"], row["translation"], variant))
    return terms


TERMS = load_terms()
CANONICAL = {translation: term for term, translation, _ in TERMS}

# 这些键的占位符是 ICU choice、JSON 文本组件或 Jade 元数据，不能按普通占位符比对。
TOKEN_EXEMPT = {
    "jade/narration.jade.withCapacity",
    "jade/narration.jade.N/N",
    "jade/narration.jade.unit.B",
    "jade/narration.jade.unit.mB",
    "jade/jade.access.slime.size",
    "jade/jade.metadata",
    "ironfurnaces/ironfurnaces.update.speech",
    "ironfurnaces/ironfurnaces.update.version",
    "ironfurnaces/ironfurnaces.update.failed",
}


def check_terms(context: str, english: str, chinese: str) -> None:
    if not english:
        return
    source = english.lower()
    for term, translation, variant in TERMS:
        if term.lower() not in source or variant not in chinese:
            continue
        owner = CANONICAL.get(variant)
        if owner and owner.lower() in source:
            continue
        add(f"{context}: 术语不一致，“{term}”应译为“{translation}”，译文含“{variant}”")


def check_text(context: str, english: str, chinese: str) -> None:
    if not isinstance(chinese, str) or not chinese.strip():
        add(f"{context}: 译文为空")
        return
    if english and chinese.strip() == english.strip():
        warn(f"{context}: 译文与英文相同")
    if context not in TOKEN_EXEMPT:
        for issue in compare_tokens(english, chinese):
            add(f"{context}: {issue}")
    check_terms(context, english, chinese)


def check_resourcepack() -> None:
    count = 0
    for namespace in AUTHOR_MODS:
        en_path = EXTRACTED / "mods" / namespace / "en_us.json"
        if not en_path.exists():
            continue
        en = read_json(en_path)
        if namespace == "strainers":
            en.update(extra_en())
        path = RESOURCEPACK / "assets" / asset_namespace(namespace) / "lang" / "zh_cn.json"
        if not path.exists():
            add(f"资源包缺少 {namespace} 的语言文件")
            continue
        zh = load_json_strict(path)
        extra = [key for key in zh if key not in en]
        if extra:
            add(f"{namespace}: {len(extra)} 个键不在 en_us 中：{extra[:5]}")
        missing = [key for key in en if key not in zh]
        if missing:
            add(f"{namespace}: {len(missing)} 个键缺少译文：{missing[:5]}")
        for key, value in zh.items():
            check_text(f"{namespace}/{key}", en.get(key, ""), value)
        count += len(zh)
    print(f"资源包：{count} 条译文")


DIVIDER_CHARS = {"─"}
CODE_PATTERN = re.compile(r"&#[0-9A-Fa-f]{6}|&[0-9a-fk-or]")


def is_divider(line: str) -> bool:
    plain = CODE_PATTERN.sub("", line).strip()
    return bool(plain) and set(plain) <= DIVIDER_CHARS


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def split_paragraphs(lines: list[str]) -> list[list[str]]:
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            paragraphs.append(current)
            current = []
    if current:
        paragraphs.append(current)
    return paragraphs


def check_quests() -> None:
    en_root = EXTRACTED / "quests" / "en_us"
    zh_root = CONFIG / "ftbquests" / "quests" / "lang" / "zh_cn"
    if not zh_root.exists():
        print("任务书：没有 zh_cn 目录，跳过")
        return
    count = 0
    for en_path in en_root.rglob("*.json5"):
        relative = en_path.relative_to(en_root)
        zh_path = zh_root / relative
        if not zh_path.exists():
            add(f"任务书缺少 {relative}")
            continue
        en = json5ish.load(en_path)
        try:
            zh = json5ish.load(zh_path)
        except json5ish.JSON5Error as error:
            add(f"{zh_path}: 解析失败 {error}")
            continue
        extra = [key for key in zh if key not in en]
        if extra:
            add(f"任务书 {relative}: {len(extra)} 个键不在 en_us 中：{extra[:5]}")
        missing = [key for key in en if key not in zh]
        if missing:
            add(f"任务书 {relative}: {len(missing)} 个键缺少译文：{missing[:5]}")
        for key, value in zh.items():
            source = en.get(key)
            if source is None:
                continue
            if isinstance(source, list):
                if not isinstance(value, list):
                    add(f"任务书 {relative}/{key}: 类型不一致")
                    continue
                if key.endswith(".quest_desc"):
                    paragraphs = split_paragraphs(
                        [
                            line
                            for line in value
                            if isinstance(line, str) and not is_divider(line)
                        ]
                    )
                    chinese_lines: list[str] = []
                    english_lines: list[str] = []
                    english_started = False
                    for paragraph in paragraphs:
                        is_chinese = any(has_cjk(line) for line in paragraph)
                        for line in paragraph:
                            if line.strip().startswith(("[", "{")):
                                try:
                                    json5ish.loads(line)
                                except json5ish.JSON5Error as error:
                                    add(f"任务书 {relative}/{key}: JSON 组件解析失败 {error}")
                        if is_chinese:
                            if english_started:
                                add(f"任务书 {relative}/{key}: 中文段落出现在英文段落之后")
                            chinese_lines.extend(paragraph)
                        else:
                            english_started = True
                            english_lines.extend(paragraph)
                    source_lines = [line for line in source if line.strip()]
                    if not chinese_lines:
                        add(f"任务书 {relative}/{key}: 没有中文段落")
                    else:
                        for issue in compare_tokens(
                            "\n".join(source_lines), "\n".join(chinese_lines)
                        ):
                            add(f"任务书 {relative}/{key}: {issue}")
                        check_terms(
                            f"任务书 {relative}/{key}",
                            "\n".join(source_lines),
                            "\n".join(chinese_lines),
                        )
                    if [line.strip() for line in english_lines] != [
                        line.strip() for line in source_lines
                    ]:
                        add(f"任务书 {relative}/{key}: 英文段落与原文不一致")
                    continue
                for index, line in enumerate(value):
                    if not isinstance(line, str):
                        add(f"任务书 {relative}/{key}[{index}]: 不是字符串")
                        continue
                    if line.strip().startswith(("[", "{")):
                        json5ish.loads(line)
                    elif index < len(source) and isinstance(source[index], str):
                        check_text(f"任务书 {relative}/{key}[{index}]", source[index], line)
            else:
                if isinstance(value, list):
                    add(f"任务书 {relative}/{key}: 类型不一致")
                    continue
                check_text(f"任务书 {relative}/{key}", str(source), str(value))
        count += len(zh)
    print(f"任务书：{count} 条译文")


def check_collapsiblegroups() -> None:
    en = read_json(EXTRACTED / "collapsiblegroups" / "en_us.json")
    path = CONFIG / "collapsiblegroups" / "lang" / "zh_cn.json"
    if not path.exists():
        print("折叠分组：没有 zh_cn，跳过")
        return
    zh = load_json_strict(path)
    extra = [key for key in zh if key not in en]
    if extra:
        add(f"折叠分组: {len(extra)} 个键不在 en_us 中：{extra[:5]}")
    missing = [key for key in en if key not in zh]
    if missing:
        add(f"折叠分组: {len(missing)} 个键缺少译文：{missing[:5]}")
    for key, value in zh.items():
        check_text(f"collapsiblegroups/{key}", en.get(key, ""), value)
    print(f"折叠分组：{len(zh)} 条译文")


def check_supplements() -> None:
    count = 0
    for namespace, prefix in SUPPLEMENT_MODS.items():
        path = RESOURCEPACK / "assets" / asset_namespace(namespace) / "lang" / "zh_cn.json"
        if not path.exists():
            add(f"资源包缺少 {namespace} 的语言文件")
            continue
        en = jar_lang(find_jar(prefix), namespace, "en_us") or {}
        zh = load_json_strict(path)
        extra = [key for key in zh if key not in en]
        if extra:
            add(f"{namespace}: {len(extra)} 个废弃键：{extra[:5]}")
        missing = [key for key in en if key not in zh]
        if missing:
            add(f"{namespace}: {len(missing)} 个键缺少译文：{missing[:5]}")
        for key, value in zh.items():
            if key in en:
                check_text(f"{namespace}/{key}", en[key], value)
        count += len(zh)
        print(f"{namespace}：{len(zh)}/{len(en)} 条")


def check_singularities() -> None:
    lang = read_json(KUBEJS / "assets" / "extendedcrafting" / "lang" / "zh_cn.json")
    folder = CONFIG / "extendedcrafting" / "singularities"
    count = 0
    for path in sorted(folder.glob("*.json")):
        data = load_json_strict(path)
        name = data.get("name")
        if not name:
            add(f"奇点 {path.name}: 缺少 name")
            continue
        if name not in lang:
            add(f"奇点 {path.name}: 名称键 {name} 不在 extendedcrafting zh_cn 中")
        count += 1
    print(f"奇点：{count} 个")


def check_kubejs() -> None:
    count = 0
    for path in KUBEJS.rglob("*.json"):
        data = load_json_strict(path)
        for key, value in data.items():
            if isinstance(value, str):
                if not value.strip():
                    add(f"{path.name}/{key}: 译文为空")
                count += 1
    print(f"KubeJS 语言文件：{count} 条")


def main() -> None:
    check_resourcepack()
    check_quests()
    check_collapsiblegroups()
    check_supplements()
    check_singularities()
    check_kubejs()
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "validation.md").write_text(
        "# 校验结果\n\n"
        + ("没有发现问题。\n" if not problems else "\n".join(f"- {item}" for item in problems) + "\n")
        + "\n## 提示\n\n"
        + ("没有需要确认的条目。\n" if not warnings else "\n".join(f"- {item}" for item in warnings) + "\n"),
        encoding="utf-8",
        newline="\n",
    )
    print(f"校验问题：{len(problems)}，提示：{len(warnings)}")
    for item in problems[:40]:
        print(f"  {item}")
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
