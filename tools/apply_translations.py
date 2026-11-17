"""把翻译批次合并进资源包。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from common import EXTRACTED, RESOURCEPACK, read_json, write_json

BATCHES = Path(__file__).resolve().parent.parent / "work" / "translation" / "batches"


def apply_batch(namespace: str, batch: dict[str, str]) -> tuple[int, int]:
    en_path = EXTRACTED / "mods" / namespace / "en_us.json"
    if not en_path.exists():
        return 0, 0
    en = read_json(en_path)
    zh_path = RESOURCEPACK / "assets" / namespace / "lang" / "zh_cn.json"
    zh = read_json(zh_path) if zh_path.exists() else {}
    unknown = [key for key in batch if key not in en]
    if unknown:
        raise SystemExit(f"{namespace}: 批次中有 {len(unknown)} 个键不在 en_us 中：{unknown[:5]}")
    added = 0
    for key, value in batch.items():
        if value and not zh.get(key):
            zh[key] = value
            added += 1
    ordered = {key: zh[key] for key in en if key in zh}
    write_json(zh_path, ordered)
    return added, len(batch)


def main() -> None:
    names = sys.argv[1:]
    files = sorted(BATCHES.glob("*.json"))
    if names:
        files = [
            BATCHES / (name if name.endswith(".json") else f"{name}.json")
            for name in names
        ]
    for path in files:
        if path.stem.startswith("_"):
            combined = read_json(path)
            for namespace, batch in combined.items():
                added, total = apply_batch(namespace, batch)
                print(f"{namespace}: 新增 {added} / {total}")
        else:
            batch = read_json(path)
            added, total = apply_batch(path.stem, batch)
            print(f"{path.stem}: 新增 {added} / {total}")


if __name__ == "__main__":
    main()
