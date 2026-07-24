为 Novel World Wiki 构建带类型的叙事图谱。所有输出使用简体中文。

用法：/wiki-graph

尽可能运行 `python tools/build_graph.py --open`。

图谱要求：
1. 解析 `wiki/` 中所有 `[[wikilinks]]`
2. 为所有页面构建带类型元数据的节点
3. 构建带叙事关系类型的边（`EXTRACTED`、`ALLY_OF`、`CONFLICTS_WITH`、`LOCATED_IN`、`CAUSES`、`LEARNS`、`BETRAYS`、`OWNS`、`MEMBER_OF`）
4. 写入 `graph/graph.json`
5. 写入 `graph/graph.html`
6. 总结节点/边数量和主要枢纽
