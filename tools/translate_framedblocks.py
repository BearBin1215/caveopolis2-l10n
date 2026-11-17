"""生成 FramedBlocks 的完整 zh_cn 语言文件。"""

from __future__ import annotations

from framed_data import BLOCKS
from framed_ui import OTHER, OVERRIDES
from common import RESOURCEPACK, WORK, find_jar, jar_lang, write_json


def build() -> dict[str, str]:
    jar = find_jar("FramedBlocks")
    en = jar_lang(jar, "framedblocks", "en_us")
    existing = jar_lang(jar, "framedblocks", "zh_cn") or {}
    assert en
    result = dict(existing)
    result.update(BLOCKS)
    result.update(OTHER)
    result.update(OVERRIDES)
    result = {key: value for key, value in result.items() if key in en}
    missing = sorted(key for key in en if key not in result)
    if missing:
        (WORK / "framed_missing_keys.txt").write_text(
            "\n".join(f"{key}\t{en[key]}" for key in missing) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        raise SystemExit(f"未翻译 {len(missing)} 个键，见 work/framed_missing_keys.txt")
    output = RESOURCEPACK / "assets" / "framedblocks" / "lang" / "zh_cn.json"
    write_json(output, result)
    print(f"FramedBlocks：{len(result)} 条，{len(en)} 个键")
    return result


if __name__ == "__main__":
    build()
