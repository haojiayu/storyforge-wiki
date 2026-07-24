#!/usr/bin/env python3
"""确保 wiki 领域页面存在所需的章节标题和信息框。"""

from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"

REQUIRED_HEADINGS: dict[str, list[str]] = {
    "characters": [
        "## 概述",
        "## 生平",
        "## 性格与特质",
        "## 能力与装备",
        "## 关系",
        "## 出场与故事弧作用",
        "## 花絮",
    ],
    "arcs": [
        "## 简介",
        "## 情节",
        "## 主要事件",
        "## 涉及人物",
        "## 连续性说明",
    ],
    "locations": [
        "## 概述",
        "## 地理",
        "## 历史",
        "## 政治与社会",
        "## 重要事件",
    ],
    "factions": [
        "## 概述",
        "## 历史",
        "## 组织结构",
        "## 目标与手段",
        "## 关系",
    ],
    "systems": [
        "## 概述",
        "## 机制",
        "## 限制与代价",
        "## 已知使用者或实践者",
        "## Canon 澄清",
    ],
    "events": [
        "## 概要",
        "## 前情",
        "## 事件经过",
        "## 后续影响",
        "## 相关页面",
    ],
    "timeline": [
        "## 时间线概述",
        "## 年表",
        "## 不确定的日期",
    ],
    "sources": [
        "## 来源概述",
        "## 情节与设定摘录",
        "## 人物更新",
        "## 时间线新增",
        "## 未解决问题",
        "## 冲突与设定修订",
    ],
}

INFOBOXES: dict[str, str] = {
    "characters": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">人物信息</th></tr>\n"
        "  <tr><td>全名</td><td>待定</td></tr>\n"
        "  <tr><td>别名</td><td>待定</td></tr>\n"
        "  <tr><td>种族</td><td>待定</td></tr>\n"
        "  <tr><td>所属</td><td>待定</td></tr>\n"
        "  <tr><td>状态</td><td>待定</td></tr>\n"
        "  <tr><td>首次出场</td><td>待定</td></tr>\n"
        "</table>"
    ),
    "arcs": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">故事弧信息</th></tr>\n"
        "  <tr><td>名称</td><td>待定</td></tr>\n"
        "  <tr><td>时间线</td><td>待定</td></tr>\n"
        "  <tr><td>核心冲突</td><td>待定</td></tr>\n"
        "  <tr><td>主要角色</td><td>待定</td></tr>\n"
        "  <tr><td>状态</td><td>待定</td></tr>\n"
        "</table>"
    ),
    "locations": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">地点信息</th></tr>\n"
        "  <tr><td>区域</td><td>待定</td></tr>\n"
        "  <tr><td>类型</td><td>待定</td></tr>\n"
        "  <tr><td>统治势力</td><td>待定</td></tr>\n"
        "  <tr><td>人口</td><td>待定</td></tr>\n"
        "  <tr><td>首次出场</td><td>待定</td></tr>\n"
        "</table>"
    ),
    "factions": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">组织信息</th></tr>\n"
        "  <tr><td>类型</td><td>待定</td></tr>\n"
        "  <tr><td>领导者</td><td>待定</td></tr>\n"
        "  <tr><td>据点</td><td>待定</td></tr>\n"
        "  <tr><td>立场</td><td>待定</td></tr>\n"
        "  <tr><td>状态</td><td>待定</td></tr>\n"
        "</table>"
    ),
    "systems": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">体系信息</th></tr>\n"
        "  <tr><td>类别</td><td>待定</td></tr>\n"
        "  <tr><td>来源</td><td>待定</td></tr>\n"
        "  <tr><td>使用者</td><td>待定</td></tr>\n"
        "  <tr><td>限制</td><td>待定</td></tr>\n"
        "  <tr><td>风险等级</td><td>待定</td></tr>\n"
        "</table>"
    ),
    "events": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">事件信息</th></tr>\n"
        "  <tr><td>日期/时代</td><td>待定</td></tr>\n"
        "  <tr><td>地点</td><td>待定</td></tr>\n"
        "  <tr><td>参与者</td><td>待定</td></tr>\n"
        "  <tr><td>结果</td><td>待定</td></tr>\n"
        "  <tr><td>重要性</td><td>待定</td></tr>\n"
        "</table>"
    ),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def split_frontmatter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        return "", content
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return "", content
    return f"---\n{parts[1]}---\n", parts[2].lstrip("\n")


def ensure_headings(path: Path, headings: list[str], infobox: str | None) -> bool:
    content = read(path)
    if not content.strip():
        return False

    changed = False
    frontmatter, body = split_frontmatter(content)

    if infobox:
        infobox_pattern = re.compile(
            r"<table class=\"infobox\">[\s\S]*?</table>\s*",
            re.MULTILINE,
        )
        if "class=\"infobox\"" in body:
            updated_body, replacements = infobox_pattern.subn(infobox + "\n\n", body, count=1)
            if replacements > 0 and updated_body != body:
                body = updated_body
                changed = True
        else:
            body = infobox + "\n\n" + body
            changed = True

    for heading in headings:
        if heading not in body:
            body = body.rstrip() + f"\n\n{heading}\n- 待定\n"
            changed = True

    if changed:
        final_content = ((frontmatter + "\n") if frontmatter else "") + body.rstrip() + "\n"
        write(path, final_content)
    return changed


def main() -> None:
    updated = 0
    scanned = 0
    for folder, headings in REQUIRED_HEADINGS.items():
        base = WIKI_DIR / folder
        if not base.exists():
            continue
        for page in base.glob("*.md"):
            scanned += 1
            infobox = INFOBOXES.get(folder)
            if ensure_headings(page, headings, infobox):
                updated += 1
                print(f"已更新：{page.relative_to(REPO_ROOT)}")
    print(f"已扫描：{scanned}，已更新：{updated}")


if __name__ == "__main__":
    main()
