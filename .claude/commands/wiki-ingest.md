将小说手稿、章节或设定资料摄取进 Novel World Wiki。所有输出使用简体中文。

用法：/wiki-ingest $ARGUMENTS

$ARGUMENTS 应为文件路径，例如：
- `raw/novel/chapter-01.md`
- `raw/world/lore-notes.md`

工作流：
1. 阅读源文件 + `wiki/index.md` + `wiki/overview.md`
2. 写入 `wiki/sources/<slug>.md`，包含叙事要点和设定变化
3. 更新相关领域页面（`characters`、`locations`、`factions`、`systems`、`events`、`timeline`、`arcs`、`chapters`）
4. 更新 `wiki/index.md` 和 `wiki/overview.md`
5. 在 `wiki/log.md` 追加摄取记录
6. 若存在设定冲突，予以报告
