#!/usr/bin/env python3
"""Build typed narrative graph for Novel World Wiki."""

from __future__ import annotations

import argparse
import json
import re
import webbrowser
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
GRAPH_DIR = REPO_ROOT / "graph"
GRAPH_JSON = GRAPH_DIR / "graph.json"
GRAPH_HTML = GRAPH_DIR / "graph.html"
LOG_FILE = WIKI_DIR / "log.md"

TYPE_COLORS = {
    "source": "#4CAF50",
    "character": "#42A5F5",
    "location": "#26A69A",
    "faction": "#AB47BC",
    "culture": "#FFA726",
    "artifact": "#EF5350",
    "system": "#5C6BC0",
    "event": "#EC407A",
    "timeline": "#8D6E63",
    "arc": "#29B6F6",
    "chapter": "#9CCC65",
    "synthesis": "#BDBDBD",
    "unknown": "#9E9E9E",
}
EDGE_COLORS = {
    "EXTRACTED": "#455A64",
    "ALLY_OF": "#43A047",
    "CONFLICTS_WITH": "#E53935",
    "LOCATED_IN": "#1E88E5",
    "CAUSES": "#FB8C00",
    "LEARNS": "#8E24AA",
    "BETRAYS": "#6D4C41",
    "OWNS": "#5E35B1",
    "MEMBER_OF": "#00897B",
}
KEYWORD_EDGE_TYPES = {
    "ally": "ALLY_OF",
    "allied": "ALLY_OF",
    "conflict": "CONFLICTS_WITH",
    "enemy": "CONFLICTS_WITH",
    "betray": "BETRAYS",
    "owns": "OWNS",
    "member of": "MEMBER_OF",
    "located in": "LOCATED_IN",
    "learns": "LEARNS",
    "causes": "CAUSES",
}


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def append_log(entry: str) -> None:
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")


def page_id(path: Path) -> str:
    return path.relative_to(WIKI_DIR).as_posix().replace(".md", "")


def all_pages() -> list[Path]:
    return [p for p in WIKI_DIR.rglob("*.md") if p.name not in {"index.md", "log.md", "lint-report.md"}]


def extract_type(content: str) -> str:
    match = re.search(r"^type:\s*([^\n]+)$", content, re.MULTILINE)
    if not match:
        return "unknown"
    return match.group(1).strip().strip('"\'')


def extract_title(content: str, fallback: str) -> str:
    match = re.search(r"^title:\s*\"?([^\n\"]+)\"?$", content, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def infer_edge_type(snippet: str) -> str:
    lower = snippet.lower()
    for keyword, edge_type in KEYWORD_EDGE_TYPES.items():
        if keyword in lower:
            return edge_type
    return "EXTRACTED"


def build_nodes(pages: list[Path]) -> list[dict]:
    nodes = []
    for p in pages:
        content = read_file(p)
        node_type = extract_type(content)
        nodes.append(
            {
                "id": page_id(p),
                "label": extract_title(content, p.stem),
                "type": node_type,
                "path": str(p.relative_to(REPO_ROOT)),
                "color": TYPE_COLORS.get(node_type, TYPE_COLORS["unknown"]),
            }
        )
    return nodes


def build_edges(pages: list[Path]) -> list[dict]:
    stem_to_id = {p.stem.lower(): page_id(p) for p in pages}
    edges = []
    seen = set()
    for p in pages:
        content = read_file(p)
        src = page_id(p)
        for match in re.finditer(r"\[\[([^\]]+)\]\]", content):
            target_stem = Path(match.group(1)).stem.lower()
            target = stem_to_id.get(target_stem)
            if not target or target == src:
                continue
            start = max(0, match.start() - 120)
            end = min(len(content), match.end() + 120)
            snippet = content[start:end]
            edge_type = infer_edge_type(snippet)
            key = (src, target, edge_type)
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                {
                    "id": f"{src}->{target}:{edge_type}",
                    "from": src,
                    "to": target,
                    "type": edge_type,
                    "confidence": 1.0 if edge_type == "EXTRACTED" else 0.8,
                    "color": EDGE_COLORS.get(edge_type, EDGE_COLORS["EXTRACTED"]),
                }
            )
    return edges


def simple_report(nodes: list[dict], edges: list[dict]) -> str:
    degree = defaultdict(int)
    for e in edges:
        degree[e["from"]] += 1
        degree[e["to"]] += 1
    hubs = sorted(degree.items(), key=lambda item: item[1], reverse=True)[:10]
    edge_types = defaultdict(int)
    for e in edges:
        edge_types[e["type"]] += 1
    lines = [
        f"# Narrative Graph Report — {date.today().isoformat()}",
        "",
        f"- Nodes: {len(nodes)}",
        f"- Edges: {len(edges)}",
        "",
        "## Edge Types",
    ]
    lines.extend(f"- {k}: {v}" for k, v in sorted(edge_types.items()))
    lines.append("")
    lines.append("## Hubs")
    lines.extend(f"- `{node}` ({deg})" for node, deg in hubs)
    return "\n".join(lines)


def render_html(nodes: list[dict], edges: list[dict]) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Novel World Graph</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>body{{margin:0;background:#111;color:#ddd;font-family:Arial}}#graph{{height:100vh}}</style>
</head>
<body>
<div id="graph"></div>
<script>
const nodes = new vis.DataSet({json.dumps(nodes, ensure_ascii=False)});
const edges = new vis.DataSet({json.dumps(edges, ensure_ascii=False)});
new vis.Network(document.getElementById("graph"), {{nodes, edges}}, {{
  nodes: {{shape:"dot", size:14}},
  edges: {{arrows:"to", smooth:true}},
  interaction: {{hover:true}},
  physics: {{barnesHut: {{gravitationalConstant:-3500}}}}
}});
</script>
</body>
</html>"""


def build_graph(open_browser: bool, report: bool, save: bool) -> None:
    pages = all_pages()
    if not pages:
        print("Wiki is empty.")
        return

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    nodes = build_nodes(pages)
    edges = build_edges(pages)
    built = date.today().isoformat()

    GRAPH_JSON.write_text(json.dumps({"nodes": nodes, "edges": edges, "built": built}, indent=2), encoding="utf-8")
    GRAPH_HTML.write_text(render_html(nodes, edges), encoding="utf-8")
    print(f"saved: {GRAPH_JSON.relative_to(REPO_ROOT)}")
    print(f"saved: {GRAPH_HTML.relative_to(REPO_ROOT)}")

    append_log(
        f"## [{built}] graph | Narrative graph rebuilt\n\n"
        f"{len(nodes)} nodes and {len(edges)} edges."
    )

    if report:
        report_md = simple_report(nodes, edges)
        print("\n" + report_md)
        if save:
            out = GRAPH_DIR / "graph-report.md"
            out.write_text(report_md, encoding="utf-8")
            print(f"saved: {out.relative_to(REPO_ROOT)}")

    if open_browser:
        webbrowser.open(f"file://{GRAPH_HTML.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build narrative graph")
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    build_graph(open_browser=args.open, report=args.report, save=args.save)
