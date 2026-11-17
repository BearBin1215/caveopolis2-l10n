"""修复模组把 block.* 键改成 item.* 后失效的中文。"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from common import MODS, REFERENCES, RESOURCEPACK, compare_tokens

MODS_DIR = MODS
I18N_PACKS = [
    REFERENCES / "i18n-resourcepack" / "Minecraft-Mod-Language-Modpack-Converted-26.1.2" / "assets",
    REFERENCES / "i18n-resourcepack" / "Minecraft-Mod-Language-Modpack-Converted-1.21.1" / "assets",
]


def load_json(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def main() -> None:
    total = 0
    for jar in sorted(MODS_DIR.glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as archive:
                names = set(archive.namelist())
                for name in sorted(names):
                    parts = name.split("/")
                    if len(parts) != 4 or parts[3] != "en_us.json":
                        continue
                    namespace = parts[1]
                    zh_name = f"assets/{namespace}/lang/zh_cn.json"
                    if zh_name not in names:
                        continue
                    english = json.loads(archive.read(name).decode("utf-8"))
                    shipped = json.loads(archive.read(zh_name).decode("utf-8"))
                    covered = set(shipped)
                    for pack in I18N_PACKS:
                        covered |= set(load_json(pack / namespace / "lang" / "zh_cn.json"))
                    target = RESOURCEPACK / "assets" / namespace / "lang" / "zh_cn.json"
                    existing = load_json(target)
                    covered |= set(existing)

                    remapped: dict[str, str] = {}
                    for key, value in shipped.items():
                        if key in english:
                            continue
                        for old, new in (("block.", "item."), ("item.", "block.")):
                            if not key.startswith(old):
                                continue
                            candidate = new + key[len(old) :]
                            if candidate in english and candidate not in covered:
                                if not compare_tokens(english[candidate], value):
                                    remapped[candidate] = value
                            break
                    if not remapped:
                        continue
                    existing.update(remapped)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(
                        json.dumps(dict(sorted(existing.items())), ensure_ascii=False, indent=2)
                        + "\n",
                        encoding="utf-8",
                    )
                    print(f"{namespace}: 修正 {len(remapped)} 条")
                    total += len(remapped)
        except (OSError, zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError):
            continue
    print(f"合计 {total} 条")


if __name__ == "__main__":
    main()
