# Contributing to Tableau AI Utilities

Thanks for helping grow the catalog. There are three contribution flows, each
with its own issue template: **new skill**, **skill improvement**, and **bug**.

## Add or change a skill

1. Create a folder `tableau-studio-skills/tableau-agent/<category>/<skill-name>/` (or `tableau-mcp-skills/<harness>/<skill-name>/`) and add a `SKILL.md`.
   Public categories are `data-and-model`, `analysis-support`, `calc-family`,
   `build-and-design`, `content-quality`, and `publish-and-deploy`. Skills that
   operate on skill files go in `studio-utilities/` and are protected. Add the skill name
   to `scripts/categories.ts` so it sorts in pipeline order.
2. Frontmatter is the portable Agent Skills pair: `name` (must equal the folder)
   and `description` (when the agent should use this skill).
3. Keep the body short. Put heavy detail in `references/` so the agent only
   loads it when the skill says to.
4. Optional: add a `README.md` (or `README-*.md`). The site uses that file as
   the human-facing details page.
5. Validate locally:

```bash
cd site
npm install
npm run validate
npm run build
```

6. Open a PR using the **New skill** PR template.

## Protected vs overridable

- **Overridable** skills can be replaced by a same-name folder in the user's
  skills directory.
- **Protected** skills cannot. Skills in the `studio-utilities` layer are protected in this
  catalog. Do not add new protected skills in other layers unless the product
  seed marks them that way.

## Versioning

Do not hard-delete a published skill without an explicit replacement. Prefer
a pull request that updates the existing folder.
