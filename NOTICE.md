# 来源与许可说明

本仓库的译文、数据和代码来自不同来源，适用不同许可。再分发或再使用前，请确认对应范围。

## 译文与数据

- 部分译文来自 [CFPAOrg/Minecraft-Mod-Language-Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package)，按 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 使用。上游贡献者名单见 [Contributors](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package/graphs/contributors)。
- 部分译文来自模组自带的 `zh_cn` 语言文件；相关译文和原始文本的权利归各模组作者所有，按各模组的许可使用。
- 本仓库对上游译文进行了提取、合并、裁剪、重译和格式转换，并补充了整合包自有内容、作者模组和其他通用模组的译文。
- 本仓库的译文、术语表和文档采用 CC BY-NC-SA 4.0，署名为 CFPA 团队和 caveopolis2-l10n 贡献者；生成的语言文件作为改编作品，也按同一许可提供。本仓库贡献者名单见 [Contributors](https://github.com/BearBin1215/caveopolis2-l10n/graphs/contributors)。

## 代码

- `tools/` 下的 Python 脚本代码采用 [MIT](LICENSE-CODE) 许可，版权归 BearBin1215 及贡献者所有。
- 脚本中内嵌的译文数据（字典、字符串表和类似内容）以及 `tools/quests_zh/`、`tools/chisel_guide_zh.json` 下的 JSON 文件仍采用 CC BY-NC-SA 4.0。

## 第三方内容

- Minecraft 原版文本、整合包 Caveopolis 2、各模组及其美术资源的权利归各自作者所有。本仓库不因翻译、合并或打包而主张这些内容的版权。
- `config/`、`kubejs/` 和 `resourcepack/` 中来自整合包、模组或 i18n 资源包的原始文件，权利归各自作者；本仓库生成的译文文件和修改部分按前述译文许可提供，原始部分仍按原作者的条款使用。
- 如果某个文件带有单独的版权或许可声明，以该声明为准。

## 修改过的第三方模组

- 发布包 `mods/` 中的 `strainers-*.jar` 是 BBL Strainers 的修改版本，原作者 benbenlaw，按 MIT 许可使用，全文见 `LICENSE-strainers`。
- 修改内容：`OrePieceItem#getName` 改为根据 `strainers:ore_type` 组件查找 `item.strainers.ore_piece.<ore_type>` 翻译键，其余逻辑未改动。
- 原始模组：https://www.curseforge.com/minecraft/mc-mods/bbl-strainers

本说明用于满足许可的署名和修改说明要求，不构成法律意见。
