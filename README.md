# Caveopolis 2 汉化

[benbenlaw](https://www.benbenlaw.com/) 整合包 [洞穴城2（Caveopolis 2）](https://www.curseforge.com/minecraft/modpacks/caveopolis-2)的汉化仓库。

译文由 AI 起草，脚本自动校验占位符与格式代码，有争议的条目由人工确认。

物品等内容使用中文，任务书的正文全部为中英双语（中文在前、英文在后）。

## 使用

- 前往 [releases 页面](https://github.com/BearBin1215/caveopolis2-l10n/releases)下载对应版本的汉化包，解压后覆盖到游戏目录。
- 压缩包内的 `mods/strainers-*.jar` 是修补版，用于让矿石碎块使用中文名称；解压时会覆盖原模组。整合包更新后需要重新解压本包；如果 `mods` 目录同时出现两个版本的 strainers，请删除旧版修补 jar。
- 安装 [I18nUpdateMod](https://www.curseforge.com/minecraft/mc-mods/i18nupdatemod) 3.7.1 或更高版本，把 jar 放入 mods 目录。
- 在资源包界面把本汉化包置于 i18n 资源包之上。

发现错译、漏译或显示异常，请在 [Issues](https://github.com/BearBin1215/caveopolis2-l10n/issues) 中附上截图、物品/任务名称或所在位置等信息。

## 许可

- 译文、术语表和文档采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可，署名为 CFPA 团队和 caveopolis2-l10n 贡献者；生成的语言文件按同一许可提供。
- `tools/` 下的 Python 脚本代码采用 [MIT](LICENSE-CODE) 许可；脚本内嵌的译文数据和 `tools/quests_zh/` 下的 JSON 文件仍按 CC BY-NC-SA 4.0 处理。
- `mods/` 中的修补版 BBL Strainers 按原模组的 MIT 许可提供，详见 [LICENSE-strainers](LICENSE-strainers)。
- 通用模组文本来自 [CFPAOrg/Minecraft-Mod-Language-Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package) 和模组自带的 `zh_cn` 文件；整合包、模组和原始文本的权利归各自作者所有。
- 来源、修改说明和第三方权利详见 [NOTICE.md](NOTICE.md)。
