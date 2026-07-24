# Storyforge Wiki — 架构与工作流说明

本 Wiki 由 Claude Code 维护，作为混合式故事圣经（story bible）与世界观构建系统。

## 语言规则（最高优先级）

- 所有人类可读内容必须使用简体中文，包括页面标题、正文、章节标题、信息框标签、索引说明、日志和报告。
- 人物名、地名等正式专名保持原文稳定，不强行翻译；必要时可在首次出现处补充中文说明。
- YAML 键、`type` 枚举、目录名、命令名、代码标识符、关系枚举和 WikiLink 语法保持英文，避免破坏工具兼容性。

## 斜杠命令

- `/wiki-ingest`
- `/wiki-query`
- `/wiki-health`
- `/wiki-lint`
- `/wiki-graph`

## 领域模型

主要页面类型：
- `source`
- `character`
- `location`
- `faction`
- `culture`
- `artifact`
- `system`
- `event`
- `timeline`
- `arc`
- `chapter`
- `synthesis`

`wiki/` 下的标准目录：
- `sources`, `characters`, `locations`, `factions`, `cultures`, `artifacts`, `systems`, `events`, `timeline`, `arcs`, `chapters`, `syntheses`

章节模板定义于：
- `templates/wiki-section-templates.md`
- 创建或更新页面时必须遵循这些标题结构。

## Frontmatter 契约

```yaml
---
title: "Page Title"
type: source | character | location | faction | culture | artifact | system | event | timeline | arc | chapter | synthesis
tags: []
sources: []
canon_status: canon | contested | apocrypha | draft
spoiler_level: none | low | medium | high
era: ""
aliases: []
relationships: []
first_appearance: ""
last_updated: YYYY-MM-DD
---
```

## 摄取工作流（Ingest）

1. 完整阅读源文件（非 md 格式需先用 markitdown 自动转换）
2. 阅读 `wiki/index.md` 和 `wiki/overview.md`
3. 写入 `wiki/sources/<slug>.md`，内容包括：
   - 叙事要点
   - 角色状态变化
   - 引入的世界观设定
   - 时间线事件
   - 未解决的悬念
   - 与既有设定的冲突
4. 更新或创建各领域页面
   - 领域页面必须遵循对应的章节模板标题结构。
5. 更新 `wiki/index.md`
6. 更新 `wiki/overview.md`
7. 在 `wiki/log.md` 追加 `## [YYYY-MM-DD] ingest | <title>`
8. 校验链接和索引注册情况

## 查询工作流（Query）

1. 阅读 `wiki/index.md`
2. 阅读相关页面，针对范围明确的问题优先查阅 `chapters`、`arcs`、`timeline`
3. 以 markdown 格式回答，并使用 `[[PageName]]` 引用
4. 添加 `## 来源`
5. 询问是否保存为 `wiki/syntheses/<slug>.md`

## 校验工作流（Lint）

检查以下项目：
- 断链或孤立的 wikilink
- 时间线矛盾
- 角色连续性错误
- 未解决的设置/回应（setup/payoff）
- 别名冲突
- canon 漂移（`canon_status: contested` 但无说明）
- 链接密度过低的稀疏页面

## 健康检查工作流（Health）

运行 `python tools/health.py` 进行确定性检查：
- 空白页
- 索引同步
- 日志覆盖率

## 图谱工作流（Graph）

生成图谱，包含：
- 来自 wikilink 的 `EXTRACTED` 边
- 带类型的推断叙事边（`ALLY_OF`、`CONFLICTS_WITH`、`LOCATED_IN`、`CAUSES`、`LEARNS`、`BETRAYS`、`OWNS`、`MEMBER_OF`）
- 可选的置信度和社群检测
