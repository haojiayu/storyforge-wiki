查询 Novel World Wiki 并生成符合 canon 设定的回答。所有输出使用简体中文。

用法：/wiki-query $ARGUMENTS

$ARGUMENTS 为问题，例如：
- `Mira 在第 12 章之前知道什么？`
- `列出第二个故事弧中的时间线冲突`

工作流：
1. 阅读 `wiki/index.md` 并确定相关页面
2. 优先在 `chapters`、`arcs`、`timeline`、`characters` 范围内检索
3. 以 markdown 格式回答，并使用 `[[PageName]]` 引用
4. 包含 `## 来源`
5. 询问是否保存为 `wiki/syntheses/<slug>.md`
