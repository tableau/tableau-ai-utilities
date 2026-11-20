# tableau-skills

Public catalog of **Tableau Agent skills** for Tableau Studio — what is available, how to customize an overridable skill, and how to download a skill folder.

- Browse the generated site (Overview, then Installable Skills).
- Each skill is a folder with a `SKILL.md`. Studio skills live at `tableau-studio-skills/tableau-agent/<category>/<name>/`. MCP skills live at `tableau-mcp-skills/<harness>/<name>/`.
- MCP skills in `tableau-mcp-skills/general/` use shared, host-independent instructions; client-specific skills remain in their existing format folders.
- A README (when present) is the human-facing details page. `SKILL.md` is what the agent loads.
- Protected skills cannot be replaced by a same-name override. Overridable skills can.

## Preview the site

```
cd site
npm install
npm start
```

Local preview is served under `/tableau-ai-utilities/` (the public GitHub Pages base path). `npm start` still uses stage Help links.

- `/` — Overview
- `/skills` — filterable catalog
- `/tableau-studio-skills/...` and `/tableau-mcp-skills/...` — details (README, or `SKILL.md` if there is no README)
- `/llms.txt` — LLM index (also `llms/tableau-ai-utilities-llms.txt`); family corpora are `llms/tableau-ai-utilities-llms-full-<family>.txt` (SKILL.md plus README when-to-use sections)
- Download links on each skill page use this site's origin and base path
- Plugins appear in the left nav only when `plugins/` contains a plugin

Merging to `main` builds the site with live links and pushes the `gh-pages` branch, served at [tableau.github.io/tableau-ai-utilities](https://tableau.github.io/tableau-ai-utilities/).

## Validate

```
cd site
npm run validate
npm run build-indexes
npm run build
```

## Export Gallery skill packages

With the site's dependencies installed, run from the repository root:

```sh
node scripts/run-tsx.cjs scripts/export-skills.ts
```

On Node 22.18+ or Node 24+, you can run the exporter directly without installing
the site's dependencies:

```sh
node scripts/export-skills.ts
```

This writes all skills as `.tskill` ZIPs plus `export-manifest.json` in `dist/tskills/`.
It validates the file structure before creating each ZIP. Packages must contain root `SKILL.md` and `README.md`; the only
optional folder is a flat `skill-expertise/` containing `.md`, `.py`, or `.txt` files. Options: `--output PATH` and `--replace` to update
a previous generated export. From `site/`, you can also use
`npm run export-skills -- --replace`.

The exporter flattens supporting text/Python resources into `skill-expertise/`,
rewrites Markdown resource paths, and records excluded agent UI metadata in the
manifest. Validation checks the planned package structure; relocated Python resources
need separate runtime testing. Source skills stay unchanged.

Run exporter tests with:

```sh
node scripts/run-tsx.cjs --test scripts/export-skills.test.ts
```
