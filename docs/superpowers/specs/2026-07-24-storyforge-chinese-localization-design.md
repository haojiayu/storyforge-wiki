# Storyforge 中文化与既有 Wiki 迁移设计

## 目标

将 Storyforge 的所有人类可读输出统一为简体中文，并使用用户当前的 Claude Code 配置迁移已经生成的 45 个 Wiki Markdown 文件。迁移完成后，无论通过 Claude Code 的 `/wiki-*` 命令还是 Python 工具生成内容，正文、标题、信息框、索引、日志和报告都应默认使用简体中文。

## 已确认范围

- 使用当前 Claude Code 全局配置，不修改其网关、模型或认证信息。
- 将现有 45 个 Wiki 文件的英文可读内容迁移为简体中文。
- 后续新摄取的小说章节默认生成简体中文 Wiki。
- 正式专名保持稳定，例如 `MissPanda`、`Princeton` 和已有角色姓名；必要时可在首次出现处补充中文说明。
- YAML 键、`type` 枚举、目录名、命令名、代码标识符和关系类型保持英文，避免破坏工具兼容性。

## 非目标

- 不重命名 `wiki/characters`、`wiki/locations` 等目录。
- 不翻译 YAML 字段名或 `character`、`location` 等类型值。
- 不修改用户的全局 Claude Code 配置。
- 不在本次迁移中继续分析第 11 回以后的内容。
- 不将小说原文、生成 Wiki 或 API 密钥提交到 Git。

## 语言契约

### 必须使用简体中文

- 页面标题和正文
- Markdown 章节标题
- HTML 信息框字段名称和值中的自然语言
- 索引说明、总览、日志、健康报告和连续性报告
- Claude Code `/wiki-*` 命令产生的解释与结论
- Python 摄取、查询、lint 和健康检查中面向用户的文本

### 必须保持稳定

- Frontmatter 键：`title`、`type`、`tags`、`sources`、`canon_status`、`spoiler_level`、`era`、`aliases`、`relationships`、`first_appearance`、`last_updated`
- 类型枚举与目录：`character`、`location`、`faction`、`event` 等
- 关系枚举：`ALLY_OF`、`CONFLICTS_WITH`、`LOCATED_IN`、`CAUSES` 等
- WikiLink 目标和文件路径，除非已有错误需要在同一事务中同步修复
- 原文中的人物名、地名和正式专名

## 规则层改造

### Claude Code 指令

在 `CLAUDE.md` 加入最高优先级语言规则，明确所有可读内容使用简体中文、专名忠于原文、技术字段保持英文。同步中文化 `.claude/commands/wiki-*.md`，让 `/wiki-ingest`、`/wiki-query`、`/wiki-lint`、`/wiki-health` 和 `/wiki-graph` 都遵循同一契约。

### 页面模板

将 `templates/wiki-section-templates.md` 中的展示标题和信息框标签翻译为中文，例如 `Overview` → `概述`、`Biography` → `生平`、`Relationships` → `关系`。示例路径、类型值和 WikiLink 语法保持不变。

### Python 工具

在模型提示词中明确要求简体中文输出，同时保持 JSON 键和技术标识不变。将 fallback 页面、索引骨架、报告标题和用户提示中文化，确保 Claude Code 之外的备用路径也不会重新生成英文页面。

## 既有 Wiki 迁移

### 备份

迁移前将当前 `wiki/` 完整复制到 `raw/_migration-backups/wiki-before-chinese/`。该路径受现有 `raw/**` 忽略规则保护，不进入 Git。

### Claude Code 迁移方式

使用用户当前 Claude Code 配置，分批处理现有页面。每批要求：

1. 翻译所有人类可读英文内容为简体中文。
2. 保留 frontmatter 键、类型值、目录、文件名和 WikiLink 目标。
3. 不添加原文或已有 Wiki 无法支持的新事实。
4. 人物名和章节标题与原文保持一致。
5. 不删除来源、时间线、关系或连续性信息。

迁移顺序为：总览与索引 → 来源与章节 → 人物 → 地点/组织/系统/事件 → 时间线/故事弧 → 日志与报告。先迁移导航和契约页面，可以让后续批次读取到中文上下文。

## 验证

迁移完成后必须验证：

- `python tools/health.py` 无空页、索引不同步或日志覆盖缺口。
- `python tools/ingest.py --validate-only` 无断链、无漏索引。
- Wiki 中不存在未授权的英文结构标题或信息框标签。
- 第 1–10 回章节标题与原文逐项一致。
- `周衿` 等已校正专名没有回退。
- 所有原有 Wiki 文件仍存在，备份可用。
- `git status` 不包含小说原文、生成 Wiki或密钥。
- 使用当前 Claude Code 配置执行一次只读中文响应测试，确认实际输出为中文。

## 失败与恢复

- Claude Code 任一批次出现链接变化、事实扩写或英文残留时，停止后续批次并从备份恢复该批文件。
- 验证失败时不继续第 11 回以后的分析。
- 规则层代码修改通过 Git 提交恢复；生成 Wiki 通过 `raw/_migration-backups/wiki-before-chinese/` 恢复。

## 完成标准

规则层和已有 Wiki 均通过验证；当前第 1–10 回页面可直接以中文浏览；之后从第 11 回继续摄取时，Claude Code 无需额外提醒即可生成简体中文、链接完整、专名稳定的 Wiki。
