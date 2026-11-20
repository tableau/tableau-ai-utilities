/**
 * Complete Reference pipeline layers.
 * Folder names are kebab-case; labels are what the site shows.
 */
export const CATEGORIES = [
  {
    slug: 'data-and-model',
    label: 'Data and Model',
    skills: [
      'data-quality-review',
      'data-scribe',
      'data-source-connector',
      'esri-map-builder',
      'join-and-relationship-advisor',
      'geocoding-auditor',
      'extract-optimizer',
    ],
  },
  {
    slug: 'analysis-support',
    label: 'Analysis Support',
    skills: [
      'logic-explainer',
      'calc-orchestrator',
      'dashboard-walkthrough-generator',
      'inheritance-triage',
      'stakeholder-translator',
      'what-if-advisor',
      'workbook-summary-onepager',
    ],
  },
  {
    slug: 'calc-family',
    label: 'Calc Family',
    skills: [
      'calc-writer',
      'calc-debugger',
      'calc-optimizer',
      'calc-linter',
      'calc-hygiene-scan',
      'calc-inventory',
      'calc-translator',
      'calc-migrator',
      'calc-migrator-diff-report',
      'calc-documenter',
      'calc-explainer',
    ],
  },
  {
    slug: 'build-and-design',
    label: 'Build and Design',
    skills: [
      'data-model-documenter',
      'worksheet-builder',
      'viz-planner',
      'viz-critique-pro-studio',
      'phone-layout-blueprint',
    ],
  },
  {
    slug: 'content-quality',
    label: 'Content Quality',
    skills: [
      'interaction-validator',
      'desktop-spellcheck',
      'i18n-scanner',
      'chart-swap-advisor',
      'dashboard-caption-audit',
      'format-drift-scanner',
      'caption-and-tooltip-advisor',
    ],
  },
  {
    slug: 'publish-and-deploy',
    label: 'Publish and Deploy',
    skills: [
      'publish-readiness',
      'workbook-auditor',
      'dashboard-preflight',
      'workbook-optimizer',
      'dashboard-print-check',
      'dashboard-tab-order',
      'sheet-swap-detector',
      'worksheet-cleanup',
    ],
  },
  {
    slug: 'studio-utilities',
    label: 'Studio Utilities',
    skills: [
      'testing-matrix',
    ],
  },
  {
    slug: 'general',
    label: 'General',
    skills: ['tableau-workbook-inventory'],
  },
  {
    slug: 'claude-format',
    label: 'Claude Format',
    skills: ['tableau-insights-service'],
  },
  {
    slug: 'codex-format',
    label: 'Codex Format',
    skills: [],
  },
] as const;

export type CategorySlug = (typeof CATEGORIES)[number]['slug'];

export const CATEGORY_LABELS: Record<string, string> = Object.fromEntries(
  CATEGORIES.map((c) => [c.slug, c.label]),
);

export const CATEGORY_ORDER: string[] = CATEGORIES.map((c) => c.slug);

export const SKILL_ORDER: string[] = CATEGORIES.flatMap((c) => [...c.skills]);

export const CATEGORY_BY_SKILL: Record<string, CategorySlug> = Object.fromEntries(
  CATEGORIES.flatMap((c) => c.skills.map((s) => [s, c.slug])),
) as Record<string, CategorySlug>;

/** Repo-root skill trees. Docs and permalinks use these paths. */
export const SKILL_ROOTS = ['tableau-studio-skills', 'tableau-mcp-skills'] as const;

/** Product and surface folders above the category layer. */
export const TREE_LABELS: Record<string, string> = {
  'tableau-studio-skills': 'Tableau Studio Skills',
  'tableau-mcp-skills': 'Tableau MCP Skills',
  'tableau-agent': 'Tableau Agent',
  'tableau-public': 'Tableau Public',
  'codex-format': 'Codex Format',
};

const TREE_ORDER = ['tableau-studio-skills', 'tableau-mcp-skills', 'tableau-agent', 'tableau-public', 'codex-format'];

/** Shown in filter chips, list subheadings, and the left-nav category list. */
export const PUBLIC_CATEGORY_SLUGS: string[] = [...CATEGORY_ORDER];

export function treeLabel(slug: string): string {
  return TREE_LABELS[slug] ?? categoryLabel(slug);
}

export function treePosition(slug: string): number {
  const categoryIndex = CATEGORY_ORDER.indexOf(slug);
  if (categoryIndex !== -1) return categoryIndex + 1;
  const treeIndex = TREE_ORDER.indexOf(slug);
  if (treeIndex !== -1) return treeIndex + 1;
  return 100;
}

export function categoryLabel(slug: string): string {
  return CATEGORY_LABELS[slug] ?? slug;
}

export function isPublicCategory(slug: string): boolean {
  return PUBLIC_CATEGORY_SLUGS.includes(slug);
}
