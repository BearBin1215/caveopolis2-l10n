"""把构建目录打包为发布压缩包。"""

from __future__ import annotations

import zipfile
from pathlib import Path

from build_pack import BUILD, PACK_NAME
from common import DIST


def main() -> None:
    target = DIST / f"{PACK_NAME}.zip"
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(BUILD.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(BUILD).as_posix())
    print(f"发布包：{target}（{target.stat().st_size / 1024:.1f} KiB）")


if __name__ == "__main__":
    main()
