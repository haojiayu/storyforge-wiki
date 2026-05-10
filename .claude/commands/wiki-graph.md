Build the typed narrative graph for the Novel World Wiki.

Usage: /wiki-graph

Run `python tools/build_graph.py --open` when possible.

Graph requirements:
1. Parse all `[[wikilinks]]` in `wiki/`
2. Build nodes for all pages with type metadata
3. Build edges with narrative relation typing (`EXTRACTED`, `ALLY_OF`, `CONFLICTS_WITH`, `LOCATED_IN`, `CAUSES`, `LEARNS`, `BETRAYS`, `OWNS`, `MEMBER_OF`)
4. Write `graph/graph.json`
5. Write `graph/graph.html`
6. Summarize node/edge counts and top hubs
