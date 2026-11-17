# AGENTS.md

## 资源

`.agents/references/` 存放整合包、模组 jar、i18n 资源包与翻译示例，已加入 `.gitignore`。在新环境中缺少这些资源时，需要请用户提供。示例译文只参考术语和风格，不整段复制。

## 核心约定

- 不确定的译名或语义，先请用户决定，不自行猜测。
- 语言文件是生成物：Chisel、FramedBlocks、任务书和折叠分组应先修改 `tools/` 中的源数据或规则，再重新生成，不要直接修改生成结果。
- 配置路径与资源包命名空间以模组实际读取为准，不能按 mod id 或常识推断；必要时解包 jar 或进入游戏核实。
- strainers 的矿石碎块名称由模组代码拼接，资源包无法覆盖；`tools/strainers_patch.py` 在构建时修补 `OrePieceItem#getName`，并把补丁 jar 放进发布包的 `mods/`。更新该模组后需重新核对 SHA1 和字节码；新增矿石类型时在 `ORE_NAMES` 中补键，否则会显示原始键。
- 术语以 `glossary/terms.csv` 和官方中文为准；修改术语时同步登记禁用变体并运行 `python tools/validate.py`。
- 纯文本或键名改动只需通过 `validate.py` 校验；只有新增命名空间、配置路径或修改脚本行为时，才需要启动游戏验证。
- 审查发现的问题直接修复，P1/P2 默认处理；需要用户确认的条目单独列出。
- 交付前必须运行 `validate.py` 并确保 0 问题，然后重新运行 `build_pack.py` 和 `package.py`。

## 常用命令

```bash
python tools/extract.py
python tools/merge.py
python tools/translate_groups.py
python tools/translate_chisel.py
python tools/translate_framedblocks.py
python tools/build_quests.py
python tools/validate.py
python tools/build_pack.py
python tools/package.py
```

执行顺序：提取/合并 → 各类生成 → 校验 → 打包。

## 更新整合包

1. 替换 `.agents/references/` 下的整合包、模组和 i18n 资源包。
2. 按常用命令顺序运行提取、合并、各生成脚本与 `validate.py`。
3. 检查 `kubejs/`、`config/` 中的自定义补丁，必要时按新版重建。
4. 运行 `build_pack.py`、`package.py`。

注意：

- i18n 资源包与新版模组的键可能不完全匹配；合并只使用 `en_us` 中存在的键。
- 任务正文格式为中文段落 → 灰色分割线 → 英文段落，规则见 `glossary/style.md`。
