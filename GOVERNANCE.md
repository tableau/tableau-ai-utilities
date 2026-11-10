# Governance

## Review

Pull requests that touch `tableau-studio-skills/**` or `tableau-mcp-skills/**` should be reviewed by someone who can
confirm the skill still matches its `description` (when it fires) and that
supporting files stay referenced from `SKILL.md` rather than duplicated.

[`.github/CODEOWNERS`](./.github/CODEOWNERS) routes review on this git.soma
checkout. GitHub uses the first `CODEOWNERS` it finds, and it looks in
`.github/` before the repository root. The public overlay omits
`.github/CODEOWNERS` so the public root file stays in force.

Root [`CODEOWNERS`](./CODEOWNERS) is the compliance header, and it is
remote-specific. This git.soma checkout keeps `#ECCN:EAR99` and
`#GUSINFO:Tableau CX,Tableau CX`. The public GitHub repo
([tableau/tableau-ai-utilities](https://github.com/tableau/tableau-ai-utilities))
keeps `#ECCN:Open Source` and `#GUSINFO:Open Source,Open Source Workflow`,
including its reserved comment line. [`scripts/publish-public.ts`](./scripts/publish-public.ts)
restores that public blob, plus `LICENSE.txt`, `CODE_OF_CONDUCT.md`,
`SECURITY.md`, and `how_to_license.md`, after copying the git.soma `main` tree.

## Publishing

- git.soma `development`, or `npm run deploy:preview` from `site/`, publishes the internal preview to git.soma `gh-pages` with stage links.
- A push to git.soma `main` runs [`scripts/publish-public.ts`](./scripts/publish-public.ts). It pushes branch `from-soma-main` on the public repo and opens or updates a pull request. It does not merge that pull request.
- Merging the public pull request runs [`.github/workflows/pages.yml`](./.github/workflows/pages.yml), which builds `https://tableau.github.io/tableau-ai-utilities/` (live Help links) and force-pushes public `gh-pages`.

[`scripts/publish-gh-pages.ts`](./scripts/publish-gh-pages.ts) copies the checkout's `CODEOWNERS` into the Pages tree. The git.soma target requires the EAR99 header. The github.com target requires the Open Source header and refuses the EAR99 header.

`scripts/githooks/pre-push` rejects a push whose remote URL is git.soma when `CODEOWNERS` lacks the git.soma header or carries the public one. A github.com URL is not checked. Enable the hook once per clone:

```bash
git config core.hooksPath scripts/githooks
```

Ownership below the header is `*` on this checkout. The public placeholder `* @github-org/my-team` stays on the public repo.

## Quality gates

Every PR must pass CI (`.github/workflows/validate.yml`):

1. **Schema validation** of `SKILL.md` frontmatter (`name` + `description` when
   YAML is present; folder name is kebab-case).
2. **Site build** — regenerates catalog pages, skill zip downloads, and the
   Docusaurus site.
