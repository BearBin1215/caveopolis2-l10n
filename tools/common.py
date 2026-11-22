"""汉化项目的公共定义和读写工具。"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
REFERENCES = ROOT / ".agents" / "references"
MODS = REFERENCES / "mods"
MODPACK = REFERENCES / "Caveopolis-2-1.0"
OVERRIDES = MODPACK / "overrides"
I18N = REFERENCES / "i18n-resourcepack" / "Minecraft-Mod-Language-Modpack-Converted-26.1.2"

WORK = ROOT / "work"
EXTRACTED = WORK / "extracted"
TRANSLATION = WORK / "translation"
RESOURCEPACK = ROOT / "resourcepack"
CONFIG = ROOT / "config"
KUBEJS = ROOT / "kubejs"
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"

MODPACK_VERSION = "1.0"
RELEASE_VERSION = "1.0-r2"

# 命名空间到模组 jar 文件名前缀的映射，只列出作者模组。
AUTHOR_MODS = {
    "bblcore": "bblcore",
    "bblfixes": "bblfixes",
    "bbllights": "bbllights",
    "bblroutersfacade": "bblroutersfacade",
    "casting": "casting",
    "castingmb": "castingmb",
    "castingtools": "castingtools",
    "colors": "colors",
    "cloche": "cloche",
    "dimresources": "dimresources",
    "flightblocks": "flightblocks",
    "strainers": "strainers",
    "rooms": "rooms",
    "structureloot": "structureloot",
    "dimenergy": "dimenergy",
    "infinitystorage": "infinitystorage",
    "routers": "routers",
    "refinedsticks": "refinedsticks",
    "smartcrafting": "smartcrafting",
    "woodenhopper": "woodenhopper",
    "stepcrafter": "stepcrafter",
    "utility": "utility",
    "inworldrecipes": "inworldrecipes",
    "jeigroups": "jeigroups",
    "modpackutils": "modpackutils",
    "minime": "minime",
    "shops": "shops",
    "appliedsticks": "appliedsticks",
    "schemajs": "schemajs",
    "adrenaline": "adrenaline",
    "nofog": "nofog",
    "sniffysniffers": "sniffysniffers",
}

# 没有 en_us 语言文件的模组，需要在源码里查找硬编码文本。
MODS_WITHOUT_LANG = {"bblfixes", "schemajs"}

# 资源包实际使用的 assets 命名空间与模组 id 不一致时在此登记。
RESOURCE_NAMESPACE = {"nofog": "rainfog"}


def asset_namespace(namespace: str) -> str:
    return RESOURCE_NAMESPACE.get(namespace, namespace)


def find_jar(prefix: str) -> Path:
    matches = sorted(MODS.glob(f"{prefix}*.jar"))
    if not matches:
        raise FileNotFoundError(f"找不到模组 jar：{prefix}*.jar")
    return matches[0]


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_json_text(text: str) -> Any:
    return json.loads(text)


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(data), encoding="utf-8", newline="\n")


def jar_lang(jar: Path, namespace: str, locale: str) -> dict[str, str] | None:
    with zipfile.ZipFile(jar) as archive:
        candidates = [
            name
            for name in archive.namelist()
            if name.endswith(f"/lang/{locale}.json")
        ]
        if not candidates:
            return None
        preferred = f"assets/{namespace}/lang/{locale}.json"
        name = preferred if preferred in candidates else candidates[0]
        return json.loads(archive.read(name).decode("utf-8"))


def jar_lang_names(jar: Path) -> list[str]:
    with zipfile.ZipFile(jar) as archive:
        return [name for name in archive.namelist() if "/lang/" in name]


def author_lang_files() -> Iterable[tuple[str, Path]]:
    for namespace, prefix in AUTHOR_MODS.items():
        yield namespace, find_jar(prefix)


_PLACEHOLDER = re.compile(r"%(?:\d+\$)?[sdbfxXeEgGc%]|\$\{[^}]*\}|\{[^{}]*\}")
_FORMAT_CODE = re.compile(r"[&\u00a7][0-9a-fk-orA-FK-OR]")


def placeholders(text: str) -> list[str]:
    tokens = []
    for match in _PLACEHOLDER.finditer(text):
        token = match.group(0)
        if token == "%%":
            continue
        tokens.append(token)
    return tokens


def format_codes(text: str) -> list[str]:
    return _FORMAT_CODE.findall(text)


def compare_tokens(source: str, target: str) -> list[str]:
    problems = []
    if placeholders(source) != placeholders(target):
        problems.append(f"占位符不一致：{placeholders(source)} -> {placeholders(target)}")
    source_codes = sorted(format_codes(source))
    target_codes = sorted(format_codes(target))
    if source_codes != target_codes:
        problems.append(f"格式代码数量不一致：{source_codes} -> {target_codes}")
    return problems


def ensure_dirs() -> None:
    for path in (
        EXTRACTED / "mods",
        EXTRACTED / "i18n",
        EXTRACTED / "quests",
        EXTRACTED / "custom",
        TRANSLATION,
        RESOURCEPACK,
        CONFIG,
        KUBEJS,
        REPORTS,
        DIST,
    ):
        path.mkdir(parents=True, exist_ok=True)
