"""生成可直接覆盖到游戏目录的汉化包。"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from common import (
    CONFIG,
    DIST,
    KUBEJS,
    OVERRIDES,
    RELEASE_VERSION,
    RESOURCEPACK,
    ROOT,
    find_jar,
)
from strainers_patch import write_patched_jar

BUILD = DIST / "build" / f"Caveopolis2-zh_cn-{RELEASE_VERSION}"
PACK_NAME = f"Caveopolis2-zh_cn-{RELEASE_VERSION}"
# 资源包文件名固定，升级时直接覆盖，避免资源包界面积累多个版本、启用状态需要重设。
RESOURCEPACK_NAME = "Caveopolis2-zh_cn"

INSTALL = """Caveopolis 2 汉化包 {version}

安装方法
1. 安装 I18nUpdateMod 3.7.1 或更高版本，把 jar 放入 mods 目录。
2. 把本压缩包解压到游戏目录，覆盖同名文件。包内 mods/ 下的 strainers 是修补版，会替换原模组。
3. 在资源包界面把本汉化包置于 i18n 资源包之上。
4. 任务书语言目录以及 kubejs、config 文件不受资源包顺序影响。

说明
- 资源包文件名固定为 resourcepacks/Caveopolis2-zh_cn.zip，升级时直接覆盖即可；之前装过带版本号的旧资源包请删除，避免同时启用两个汉化包。
- 通用模组文本由 I18nUpdateMod 和 i18n 资源包提供，本包不附带。
- 本包只覆盖整合包自有内容和作者模组的文本。
- 未翻译的通用模组文本保持英文。
- strainers 修补版让矿石碎块按中文名称显示。整合包更新后需要重新解压本包；如果 strainers 升级到新版本，补丁会失效，请删除旧版修补 jar 并等待汉化包更新。

来源与许可
- 部分译文来自 CFPAOrg/Minecraft-Mod-Language-Package，按 CC BY-NC-SA 4.0 使用：
  https://github.com/CFPAOrg/Minecraft-Mod-Language-Package
  贡献者名单：https://github.com/CFPAOrg/Minecraft-Mod-Language-Package/graphs/contributors
- 本包译文和文档采用 CC BY-NC-SA 4.0：
  https://creativecommons.org/licenses/by-nc-sa/4.0/
- 修补版 BBL Strainers 按原模组的 MIT 许可提供，详见 LICENSE-strainers。
- 本包对上游译文进行了提取、合并、裁剪、重译和格式转换。
- 整合包、模组及原始文本的权利归各自作者所有。
- 完整说明见 NOTICE.md。
""".format(version=RELEASE_VERSION)


def reset_build() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)


def zip_resourcepack() -> Path:
    target = BUILD / "resourcepacks" / f"{RESOURCEPACK_NAME}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(RESOURCEPACK.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(RESOURCEPACK).as_posix())
    return target


SIGN_TEXT = {
    '["Welcome To", "Caveopolis 2", "", ""]': '["欢迎来到", "Caveopolis 2", "", ""]',
    '["", "The World", "And You", ""]': '["", "世界", "与你", ""]',
    '["Content", "", "", ""]': '["内容", "", "", ""]',
    '["Easter Egg", "", "", ""]': '["彩蛋", "", "", ""]',
    '["Use", "/sky gui", "to get started", ""]': '["使用", "/sky gui", "开始游戏", ""]',
}


def patch_templates() -> None:
    source = OVERRIDES / "config" / "skyblockbuilder" / "templates" / "islands"
    target = BUILD / "config" / "skyblockbuilder" / "templates" / "islands"
    for path in sorted(source.glob("*.snbt")):
        text = path.read_text(encoding="utf-8")
        patched = text
        for english, chinese in SIGN_TEXT.items():
            patched = patched.replace(english, chinese)
        if patched == text:
            continue
        target.mkdir(parents=True, exist_ok=True)
        (target / path.name).write_text(patched, encoding="utf-8", newline="\n")


TEMPLATE_NAMES = {
    '"name": "Spawn"': '"name": "出生点"',
    '"name": "Small Cave"': '"name": "小型洞穴"',
    '"name": "Mossy Cave"': '"name": "苔藓洞穴"',
}

BHMENU_TEXT = {
    'title = "Need a server?"': 'title = "需要服务器吗？"',
    'description = "Click me to get your own server!"': 'description = "点击这里获取你自己的服务器！"',
}


def patch_skyblock_config() -> None:
    source = OVERRIDES / "config" / "skyblockbuilder" / "templates.json5"
    target = BUILD / "config" / "skyblockbuilder" / "templates.json5"
    text = source.read_text(encoding="utf-8")
    for english, chinese in TEMPLATE_NAMES.items():
        text = text.replace(english, chinese)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def patch_bhmenu() -> None:
    source = OVERRIDES / "config" / "bhmenu-client.toml"
    target = BUILD / "config" / "bhmenu-client.toml"
    text = source.read_text(encoding="utf-8")
    for english, chinese in BHMENU_TEXT.items():
        text = text.replace(english, chinese)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def copy_tree(source: Path, target: Path) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def main() -> None:
    reset_build()
    source = find_jar("strainers")
    write_patched_jar(BUILD / "mods" / source.name, source)
    zip_resourcepack()
    copy_tree(CONFIG / "ftbquests", BUILD / "config" / "ftbquests")
    copy_tree(CONFIG / "collapsiblegroups", BUILD / "config" / "collapsiblegroups")
    copy_tree(CONFIG / "extendedcrafting", BUILD / "config" / "extendedcrafting")
    copy_tree(CONFIG / "mysticalcustomization", BUILD / "config" / "mysticalcustomization")
    patch_templates()
    patch_skyblock_config()
    patch_bhmenu()
    copy_tree(KUBEJS, BUILD / "kubejs")
    shutil.copy2(ROOT / "LICENSE", BUILD / "LICENSE")
    shutil.copy2(ROOT / "LICENSE-CODE", BUILD / "LICENSE-CODE")
    shutil.copy2(ROOT / "LICENSE-strainers", BUILD / "LICENSE-strainers")
    shutil.copy2(ROOT / "NOTICE.md", BUILD / "NOTICE.md")
    (BUILD / "安装说明.txt").write_text(INSTALL, encoding="utf-8", newline="\n")

    files = [path for path in BUILD.rglob("*") if path.is_file()]
    total = sum(path.stat().st_size for path in files)
    print(f"构建完成：{len(files)} 个文件，{total / 1024:.1f} KiB")
    print(f"输出目录：{BUILD}")


if __name__ == "__main__":
    main()
