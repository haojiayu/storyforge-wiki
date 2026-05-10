# Quartz Publishing Guide (Novel World Wiki)

This guide publishes the generated `wiki/` from this repo into a Quartz site.

## 1) Prepare Quartz

```bash
git clone https://github.com/jackyzha0/quartz.git my-world-wiki
cd my-world-wiki
npm ci
```

## 2) Generate Wiki Content Here

From this repository (`llm-wiki-agent`):

```bash
claude
# then run in Claude:
# /wiki-ingest raw/
# /wiki-lint
# /wiki-graph
```

## 3) Sync to Quartz `content/`

From this repo:

```bash
python tools/sync_to_quartz.py "../my-world-wiki" --clean
```

This copies all `wiki/**/*.md` files into `my-world-wiki/content/`.

## 4) Configure Quartz Theme

Update `my-world-wiki/quartz.config.ts`:

- `pageTitle`: your world name
- `baseUrl`: `YOUR_USERNAME.github.io/my-world-wiki`
- fonts/colors for your world vibe (parchment fantasy, sci-fi neon, etc.)
- ready-made presets: `docs/quartz-theme-presets.md`

## 5) Local Preview

In Quartz repo:

```bash
npx quartz build --serve
```

Open `http://localhost:8080`.

## 6) Publish to GitHub Pages

Use Quartz deploy workflow (GitHub Actions), then:

```bash
npx quartz sync
```

Set GitHub Pages source to **GitHub Actions** in repo settings.

## 7) Update Loop

Each time you ingest new lore:

1. regenerate wiki in this repo
2. run `python tools/sync_to_quartz.py "../my-world-wiki" --clean`
3. in Quartz repo, run `npx quartz sync`
