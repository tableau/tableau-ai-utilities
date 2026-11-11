# Governance

## Review

Pull requests that touch `tableau-studio-skills/**` or `tableau-mcp-skills/**` should be reviewed by someone who can
confirm the skill still matches its `description` (when it fires) and that
supporting files stay referenced from `SKILL.md` rather than duplicated.

Root [`CODEOWNERS`](./CODEOWNERS) is the compliance header. The public GitHub repo
([tableau/tableau-ai-utilities](https://github.com/tableau/tableau-ai-utilities))
keeps `#ECCN:Open Source` and `#GUSINFO:Open Source,Open Source Workflow`,
including its reserved comment line.

## Publishing

- Merging to `main` runs [`.github/workflows/pages.yml`](./.github/workflows/pages.yml), which force-pushes public `gh-pages` with live Help links. While `tableau/tableau-ai-utilities` is private, that build uses base path `/` so the private Pages host can load it. A public repository keeps `/tableau-ai-utilities/`. Making the repository public runs the workflow again.

[`scripts/publish-gh-pages.ts`](./scripts/publish-gh-pages.ts) copies the checkout's `CODEOWNERS` into the Pages tree. It requires the Open Source header.

## Quality gates

Every PR must pass CI (`.github/workflows/validate.yml`):

1. **Schema validation** of `SKILL.md` frontmatter (`name` + `description` when
   YAML is present; folder name is kebab-case).
2. **Site build** — regenerates catalog pages, skill zip downloads, and the
   Docusaurus site.
