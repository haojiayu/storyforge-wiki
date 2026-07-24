# Storyforge Wiki 章节模板（Fandom 风格）

生成或更新页面时使用这些模板。它们刻意模仿常见的 Fandom 式页面结构：先信息框，再清晰的设定章节。所有人类可读内容使用简体中文。

## 人物页面模板（`wiki/characters/*.md`）

```markdown
<table class="infobox">
  <tr><th colspan="2">人物信息</th></tr>
  <tr><td>全名</td><td>待定</td></tr>
  <tr><td>别名</td><td>待定</td></tr>
  <tr><td>种族</td><td>待定</td></tr>
  <tr><td>所属</td><td>待定</td></tr>
  <tr><td>状态</td><td>待定</td></tr>
  <tr><td>首次出场</td><td>待定</td></tr>
</table>

## 概述
- 一段话概括该人物是谁、为何重要。

## 生平
- 早年经历：
- 重大转折点：
- 当前走向：

## 性格与特质
- 优点：
- 缺陷：
- 动机：

## 能力与装备
- 能力：
- 标志性技能：
- 重要装备：

## 关系
- [[CharacterOrFaction]] - 关系及当前状态

## 出场与故事弧作用
- 参与的故事弧：
- 关键章节/事件：

## 花絮
- 备注、灵感来源、命名相关事实或作者说明。
```

## 故事弧页面模板（`wiki/arcs/*.md`）

```markdown
<table class="infobox">
  <tr><th colspan="2">故事弧信息</th></tr>
  <tr><td>名称</td><td>待定</td></tr>
  <tr><td>时间线</td><td>待定</td></tr>
  <tr><td>核心冲突</td><td>待定</td></tr>
  <tr><td>主要角色</td><td>待定</td></tr>
  <tr><td>状态</td><td>待定</td></tr>
</table>

## 简介
- 简要概括故事弧前提和利害关系。

## 情节
1. 铺垫
2. 冲突升级
3. 中点反转
4. 高潮
5. 收尾

## 主要事件
- [[EventName]] - 对故事弧的影响

## 涉及人物
- [[CharacterName]] - 在故事弧中的角色

## 连续性说明
- 矛盾之处或不确定的 canon 设定点。
```

## 地点页面模板（`wiki/locations/*.md`）

```markdown
<table class="infobox">
  <tr><th colspan="2">地点信息</th></tr>
  <tr><td>区域</td><td>待定</td></tr>
  <tr><td>类型</td><td>待定</td></tr>
  <tr><td>统治势力</td><td>待定</td></tr>
  <tr><td>人口</td><td>待定</td></tr>
  <tr><td>首次出场</td><td>待定</td></tr>
</table>

## 概述
- 这个地点是什么、位于何处。

## 地理
- 地形：
- 气候：
- 重要区域/地点：

## 历史
- 建立：
- 历史转折点：

## 政治与社会
- 由谁掌控：
- 社会秩序与派系：

## 重要事件
- [[EventName]] - 与该地点的关联
```

## 组织页面模板（`wiki/factions/*.md`）

```markdown
<table class="infobox">
  <tr><th colspan="2">组织信息</th></tr>
  <tr><td>类型</td><td>待定</td></tr>
  <tr><td>领导者</td><td>待定</td></tr>
  <tr><td>据点</td><td>待定</td></tr>
  <tr><td>立场</td><td>待定</td></tr>
  <tr><td>状态</td><td>待定</td></tr>
</table>

## 概述
- 一段话定义该组织及其在设定中的作用。

## 历史
- 起源：
- 发展：
- 重大冲突：

## 组织结构
- 层级：
- 重要成员：
- 内部裂痕：

## 目标与手段
- 公开目标：
- 隐藏意图：
- 常用手段：

## 关系
- 盟友：
- 敌对方：
- 中立势力：
```

## 体系页面模板（`wiki/systems/*.md`）

```markdown
<table class="infobox">
  <tr><th colspan="2">体系信息</th></tr>
  <tr><td>类别</td><td>待定</td></tr>
  <tr><td>来源</td><td>待定</td></tr>
  <tr><td>使用者</td><td>待定</td></tr>
  <tr><td>限制</td><td>待定</td></tr>
  <tr><td>风险等级</td><td>待定</td></tr>
</table>

## 概述
- 该体系是什么、影响哪些方面。

## 机制
- 核心规则：
- 规则间的相互作用：
- 失效方式：

## 限制与代价
- 硬性限制：
- 代价：
- 副作用：

## 已知使用者或实践者
- [[CharacterOrFaction]] - 使用情况

## Canon 澄清
- 已确认事实：
- 存疑之处：
```

## 事件页面模板（`wiki/events/*.md`）

```markdown
<table class="infobox">
  <tr><th colspan="2">事件信息</th></tr>
  <tr><td>日期/时代</td><td>待定</td></tr>
  <tr><td>地点</td><td>待定</td></tr>
  <tr><td>参与者</td><td>待定</td></tr>
  <tr><td>结果</td><td>待定</td></tr>
  <tr><td>重要性</td><td>待定</td></tr>
</table>

## 概要
- 一段话描述发生了什么。

## 前情
- 导致此事件发生的前因。

## 事件经过
- 逐个关键时刻的详细梳理。

## 后续影响
- 直接影响：
- 长期后果：

## 相关页面
- [[CharacterName]]
- [[LocationName]]
- [[ArcName]]
```

## 时间线页面模板（`wiki/timeline/*.md`）

```markdown
## 时间线概述
- 该时间线页面的范围。

## 年表
- YYYY 或时代标记 - [[EventName]] - 一句话说明重要性

## 不确定的日期
- 顺序存疑的事件。
```

## 来源页面模板（`wiki/sources/*.md`）

```markdown
## 来源概述
- 文档类型、来源和可靠性。

## 情节与设定摘录
- 叙事要点：
- 世界观细节：

## 人物更新
- [[CharacterName]]：从……到……

## 时间线新增
- [[EventName]] ……

## 未解决问题
- 悬而未决的线索和猜测性要点。

## 冲突与设定修订
- 与既有 canon 的冲突。
```
