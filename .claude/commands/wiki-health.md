Run deterministic structural health checks for the Novel World Wiki.

Usage: /wiki-health

Steps:
1. Run `python tools/health.py`
2. Report:
   - empty/stub pages
   - index sync issues
   - source/chapter log coverage gaps
3. Ask whether to save the report with `python tools/health.py --save`
