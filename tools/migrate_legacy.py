"""从 1.21.1 的 i18n 资源包迁移当前模组缺失的键。"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from common import MODS, REFERENCES, RESOURCEPACK, compare_tokens

LEGACY = REFERENCES / "i18n-resourcepack" / "Minecraft-Mod-Language-Modpack-Converted-1.21.1" / "assets"
CURRENT = REFERENCES / "i18n-resourcepack" / "Minecraft-Mod-Language-Modpack-Converted-26.1.2" / "assets"
MODS_DIR = MODS

# 旧版缺少占位符或格式代码时，迁移时使用人工修正后的文本。
REPAIRS = {
    "ftbteams.party_api_only": "在这个整合包中，你无法直接创建团队！\n%s",
}


def load_json(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def jar_langs() -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {}
    for jar in MODS_DIR.glob("*.jar"):
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    if not (
                        name.startswith("assets/")
                        and name.endswith(("/lang/en_us.json", "/lang/zh_cn.json"))
                    ):
                        continue
                    parts = name.split("/")
                    if len(parts) != 4:
                        continue
                    namespace, locale = parts[1], parts[3].split(".")[0]
                    try:
                        data = json.loads(archive.read(name).decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    if isinstance(data, dict):
                        result.setdefault(namespace, {})[locale] = data
        except (OSError, zipfile.BadZipFile):
            continue
    return result


def main() -> None:
    total = 0
    for namespace, langs in sorted(jar_langs().items()):
        english = langs.get("en_us") or {}
        if not english:
            continue
        shipped = langs.get("zh_cn") or {}
        legacy = load_json(LEGACY / namespace / "lang" / "zh_cn.json")
        current = load_json(CURRENT / namespace / "lang" / "zh_cn.json")
        target = RESOURCEPACK / "assets" / namespace / "lang" / "zh_cn.json"
        existing = load_json(target)
        migrated: dict[str, str] = {}
        for key, source in english.items():
            if key not in legacy or key in current or key in existing or key in shipped:
                continue
            value = legacy[key]
            if compare_tokens(source, value):
                value = REPAIRS.get(key, "")
                if not value or compare_tokens(source, value):
                    continue
            migrated[key] = value
        if not migrated:
            continue
        existing.update(migrated)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(dict(sorted(existing.items())), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        total += len(migrated)
        print(f"{namespace}: {len(migrated)} 条")

    print(f"合计 {total} 条")


if __name__ == "__main__":
    main()
