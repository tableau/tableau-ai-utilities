# Skill authoring guide

A skill is a self-contained directory. Keep `SKILL.md` short (when + how); push
deep detail into `references/`.

```
tableau-studio-skills/tableau-agent/<category>/my-skill-name/
  SKILL.md       # frontmatter + instructions (the contract)
  README.md      # optional; becomes the catalog details page
  references/    # deep-dive docs loaded on demand
  scripts/       # optional helper scripts the agent can run
```

Put the skill in the matching catalog layer: `data-and-model`,
`analysis-support`, `calc-family`, `build-and-design`, `content-quality`,
or `publish-and-deploy`. Skills that operate on skill files go in `studio-utilities/`
and are **protected** (they do not appear as a public category). List the
skill in `scripts/categories.ts` so the site nav and filters keep pipeline
order.

## Frontmatter fields

Portable Agent Skills format — only these two are required:

| Field         | Required | Notes                                                          |
| ------------- | -------- | -------------------------------------------------------------- |
| `name`        | yes      | Kebab-case; **must equal the folder name**.                    |
| `description` | yes      | When to use this skill. This is the agent's selection signal.  |

Other YAML keys are allowed and ignored by this catalog.

## Body

Write the steps and rules the agent needs every time the skill fires. Link out
to `references/` rather than inlining catalogs, examples, or schemas.

Skill Creator in Tableau Agent enforces a description quality gate: several
trigger phrases, at least one "do not trigger" boundary, and a short
description. Follow that when you add a skill here.

## Catalog pages

If you include a README, the site renders it as the skill's details page and
still publishes `SKILL.md` next to it. If there is no README, the details page
is the `SKILL.md` body.
