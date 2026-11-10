/**
 * build-llms.ts
 *
 * Writes LLM-oriented site maps following https://llmstxt.org.
 * Filenames are `{site-slug}-llms.txt` and `{site-slug}-llms-full[-{family}].txt`
 * (site slug = kebab-case of VARIABLES.site_title).
 *
 *   llms/{site}-llms.txt                    — curated index (granular + family corpora)
 *   llms/{site}-llms-full.txt               — SKILL.md + README when-to-use for every skill
 *   llms/{site}-llms-full-{family}.txt      — same, one family per file
 *
 * Corpora omit reference files and the rest of each README (walkthroughs,
 * limitations, etc.). Those stay on the live site, linked from SKILL.md.
 *
 * Copies the publishable files to site/static/llms/ (gitignored). Spec aliases
 * /llms.txt and /llms-full.txt are the index and combined corpus.
 *
 * URLs use siteRootFromEnv(), the same origin and base path as docusaurus.config.ts
 * (official default: https://tableau.github.io/tableau-ai-utilities). The committed
 * llms/ directory is that public corpus and is rewritten only for a public build.
 * Preview builds publish site/static/llms/ and leave llms/ untouched.
 *
 * Run with:  npm run build-llms   (from site/, via ../scripts)
 */
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import matter from 'gray-matter';
import {protectionFor, protectionLabel} from './protection';
import {
  CATEGORY_LABELS,
  CATEGORY_ORDER,
  SKILL_ORDER,
  SKILL_ROOTS,
  categoryLabel,
} from './categories';
import {applyVariables, VARIABLES} from '../site/src/remark/variables.mjs';
import {
  isPublicCorpusBuild,
  outboundEnvFromGithubOrigin,
  parseExtProtocol,
  buildExtLinkModel,
  siteRootFromEnv,
  type ExtLinkEnv,
} from '../site/src/extLinks/resolve';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
function skillFiles(): string[] {
  return SKILL_ROOTS.flatMap((root) => walkSkillMd(path.join(ROOT, root))).sort();
}
const OVERVIEW_PATH = path.join(ROOT, 'site', 'docs', 'overview.mdx');
const LLMS_DIR = path.join(ROOT, 'llms');
const STATIC_DIR = path.join(ROOT, 'site', 'static');

type Resource = {rel: string; dest: string};

type ParsedSkill = {
  name: string;
  category: string;
  categoryLabel: string;
  title: string;
  description: string;
  protection: ReturnType<typeof protectionFor>;
  skillDir: string;
  skillBody: string;
  useForBody: string;
  permalink: string;
  skillPermalink: string;
  download: string;
  resources: Resource[];
};

function siteRoot(): string {
  return siteRootFromEnv(process.env.GITHUB_ORIGIN, process.env.GITHUB_BASE_PATH);
}

function abs(pathname: string): string {
  if (/^[a-z][a-z0-9+.-]*:/i.test(pathname)) return pathname;
  const root = siteRoot();
  if (!pathname || pathname === '/') return root;
  return `${root}${pathname.startsWith('/') ? pathname : `/${pathname}`}`;
}

function oneLine(value: string): string {
  return value.replace(/\s+/g, ' ').trim();
}

function kebab(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function siteSlug(): string {
  return kebab(VARIABLES.site_title);
}

type LlmsPaths = {
  indexFile: string;
  fullFile: string;
  familyFile: (category: string) => string;
  indexUrl: string;
  fullUrl: string;
  familyUrl: (category: string) => string;
};

function llmsPaths(): LlmsPaths {
  const slug = siteSlug();
  const indexFile = `${slug}-llms.txt`;
  const fullFile = `${slug}-llms-full.txt`;
  const familyFile = (category: string) => `${slug}-llms-full-${category}.txt`;
  return {
    indexFile,
    fullFile,
    familyFile,
    indexUrl: abs(`/llms/${indexFile}`),
    fullUrl: abs(`/llms/${fullFile}`),
    familyUrl: (category: string) => abs(`/llms/${familyFile(category)}`),
  };
}

function walkSkillMd(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  const out: string[] = [];
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkSkillMd(full));
    else if (entry.name === 'SKILL.md') out.push(full);
  }
  return out;
}

function titleize(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function firstHeading(markdown: string): string | undefined {
  const m = markdown.match(/^#\s+(.+)$/m);
  return m?.[1]?.trim();
}

function firstParagraph(markdown: string): string {
  const stripped = markdown.replace(/^---[\s\S]*?---\s*/, '').replace(/^#\s+.+\n+/, '');
  const para = stripped
    .split(/\n\s*\n/)
    .map((p) => p.replace(/\s+/g, ' ').trim())
    .find((p) => p.length > 0 && !p.startsWith('#') && !p.startsWith('|') && !p.startsWith('```'));
  return para ?? '';
}

const USE_FOR_HEADINGS = new Set([
  'what it does',
  'when to use it',
  'when to use',
  'when not to use it',
  'when not to use',
  'how to trigger it',
  'example trigger phrases',
]);

function normalizeHeading(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

/** README sections that answer "what to use this for" (not walkthroughs or references). */
function extractUseForSections(markdown: string): string {
  const headingRe = /^##\s+(.+)$/gm;
  const matches = [...markdown.matchAll(headingRe)];
  const chunks: string[] = [];
  for (let i = 0; i < matches.length; i++) {
    const match = matches[i];
    const heading = match[1]?.trim() ?? '';
    if (!USE_FOR_HEADINGS.has(normalizeHeading(heading))) continue;
    const start = (match.index ?? 0) + match[0].length;
    const end = i + 1 < matches.length ? (matches[i + 1].index ?? markdown.length) : markdown.length;
    const body = markdown.slice(start, end).trim();
    chunks.push(body ? `## ${heading}\n\n${body}` : `## ${heading}`);
  }
  return chunks.join('\n\n').trim();
}

function findReadme(skillDir: string): string | undefined {
  const exact = path.join(skillDir, 'README.md');
  if (fs.existsSync(exact)) return exact;
  const matches = fs
    .readdirSync(skillDir)
    .filter((n) => /^readme.*\.md$/i.test(n) && n.toLowerCase() !== 'skill.md')
    .sort();
  return matches[0] ? path.join(skillDir, matches[0]) : undefined;
}

function isSkillOrReadme(filename: string): boolean {
  const base = path.basename(filename);
  if (base === 'SKILL.md' || base === 'SKILL.mdx') return true;
  return /^readme.*\.mdx?$/i.test(base);
}

function flattenRel(rel: string): string {
  return rel.replace(/\\/g, '/').replace(/\.mdx?$/, '').replace(/\//g, '-') + '.md';
}

function collectResourceMarkdown(skillDir: string): Resource[] {
  const files: Resource[] = [];

  function addMarkdown(absPath: string, rel: string) {
    if (!absPath.endsWith('.md') && !absPath.endsWith('.mdx')) return;
    if (isSkillOrReadme(absPath)) return;
    files.push({rel, dest: flattenRel(rel)});
  }

  function walk(dir: string, relBase: string) {
    if (!fs.existsSync(dir)) return;
    for (const name of fs.readdirSync(dir, {withFileTypes: true})) {
      if (name.name === '.DS_Store') continue;
      const full = path.join(dir, name.name);
      const rel = relBase ? `${relBase}/${name.name}` : name.name;
      if (name.isDirectory()) walk(full, rel);
      else addMarkdown(full, rel);
    }
  }

  for (const name of fs.readdirSync(skillDir, {withFileTypes: true})) {
    const full = path.join(skillDir, name.name);
    if (name.isFile()) addMarkdown(full, name.name);
  }
  for (const folder of ['references', 'examples', 'resources', 'testing']) {
    walk(path.join(skillDir, folder), folder === 'references' ? '' : folder);
  }
  return files;
}

function rewriteExtLinks(markdown: string, env: ExtLinkEnv): string {
  return markdown.replace(/\]\((ext:\/\/[^)]+)\)/g, (full, url: string) => {
    const parsed = parseExtProtocol(url);
    if (!parsed) return full;
    const model = buildExtLinkModel(parsed.site, parsed.path, env);
    return `](${model.href})`;
  });
}

function rewriteLocalMdLinks(
  markdown: string,
  skillPermalink: string,
  resources: {rel: string; dest: string}[],
): string {
  return markdown.replace(/\]\(([^)]+)\)/g, (full, url: string) => {
    const [pathPart, ...hashParts] = url.split('#');
    const hash = hashParts.length ? `#${hashParts.join('#')}` : '';
    const clean = pathPart.trim();
    if (!clean || /^[a-z][a-z0-9+.-]*:/i.test(clean) || clean.startsWith('#')) {
      return full;
    }
    if (clean.startsWith('/')) {
      return `](${abs(clean)}${hash})`;
    }
    const posix = clean.replace(/\\/g, '/').replace(/^\.\//, '');
    if (SKILL_ROOTS.some((root) => posix.startsWith(`${root}/`)) || posix.startsWith('plugins/')) {
      return `](${abs(`/${posix}`)}${hash})`;
    }
    const stripped = posix.replace(/^(references|examples|resources|testing)\//, '');
    const base = posix.split('/').pop() ?? posix;
    const match =
      resources.find((r) => r.rel === posix || r.rel === stripped) ??
      resources.find((r) => path.posix.basename(r.rel) === base);
    if (!match) return full;
    const destName = match.dest.replace(/\.mdx?$/, '');
    return `](${abs(`${skillPermalink}/resources/${destName}`)}${hash})`;
  });
}

function stripMdxChrome(markdown: string): string {
  return markdown
    .split('\n')
    .filter((line) => !/^\s*import\s/.test(line) && !/^\s*export\s/.test(line))
    .join('\n')
    .replace(/<CatalogFilter\b[^>]*\/>/g, '')
    .replace(/^\s*\n+/, '');
}

function prepareMarkdown(
  raw: string,
  env: ExtLinkEnv,
  skillPermalink?: string,
  resources: {rel: string; dest: string}[] = [],
): {title: string; body: string} {
  const {content} = matter(raw);
  let body = applyVariables(content);
  body = stripMdxChrome(body);
  body = rewriteExtLinks(body, env);
  if (skillPermalink) {
    body = rewriteLocalMdLinks(body, skillPermalink, resources);
  } else {
    body = body.replace(/\]\(([^)]+)\)/g, (full, url: string) => {
      const [pathPart, ...hashParts] = url.split('#');
      const hash = hashParts.length ? `#${hashParts.join('#')}` : '';
      const clean = pathPart.trim();
      if (!clean || /^[a-z][a-z0-9+.-]*:/i.test(clean) || clean.startsWith('#')) {
        return full;
      }
      if (clean.startsWith('/')) return `](${abs(clean)}${hash})`;
      const posix = clean.replace(/\\/g, '/').replace(/^\.\//, '');
      if (SKILL_ROOTS.some((root) => posix.startsWith(`${root}/`)) || posix.startsWith('plugins/')) {
        return `](${abs(`/${posix}`)}${hash})`;
      }
      return full;
    });
  }
  const title = firstHeading(body) ?? '';
  return {title, body: body.trim()};
}

function parseSkill(file: string, env: ExtLinkEnv): ParsedSkill {
  const skillDir = path.dirname(file);
  const folder = path.basename(skillDir);
  const rel = path.relative(ROOT, skillDir).split(path.sep);
  const categoryFromPath = rel.length >= 2 ? rel[rel.length - 2] : undefined;
  const raw = fs.readFileSync(file, 'utf8');
  const {data, content} = matter(raw);
  const fm = data as {name?: string; description?: string};
  const name = (typeof fm.name === 'string' && fm.name) || folder;
  const category = categoryFromPath || '';
  if (!category || !CATEGORY_LABELS[category]) {
    throw new Error(
      `${path.relative(ROOT, file)}: put this skill under tableau-studio-skills/tableau-agent/<category>/${name}/ or tableau-mcp-skills/<harness>/${name}/`,
    );
  }
  const looseDescription = raw.match(/^description:\s+(.+)$/m)?.[1]?.trim();
  const description =
    (typeof fm.description === 'string' && fm.description.trim()) ||
    looseDescription ||
    firstParagraph(content) ||
    titleize(name);
  const title = firstHeading(content) ?? titleize(name);
  const permalink = `/${rel.join('/')}`;
  const resources = collectResourceMarkdown(skillDir);
  const readmePath = findReadme(skillDir);
  const detailsRaw = readmePath ? fs.readFileSync(readmePath, 'utf8') : '';
  const details = detailsRaw ? prepareMarkdown(detailsRaw, env, permalink, resources) : {title: '', body: ''};
  const skill = prepareMarkdown(raw, env, permalink, resources);
  const heading = details.title || title;
  return {
    name,
    category,
    categoryLabel: categoryLabel(category),
    title: heading === name ? titleize(name) : heading,
    description: oneLine(applyVariables(description)),
    protection: protectionFor(name, category),
    skillDir,
    skillBody: skill.body,
    useForBody: details.body ? extractUseForSections(details.body) : '',
    permalink,
    skillPermalink: `${permalink}/SKILL`,
    download: `/downloads/${name}.zip`,
    resources,
  };
}

function listItem(title: string, url: string, note?: string): string {
  return note ? `- [${title}](${url}): ${oneLine(note)}` : `- [${title}](${url})`;
}

function relatedDocs(env: ExtLinkEnv): {title: string; href: string; note: string}[] {
  const links = [
    {
      title: 'Get started with Tableau Agent',
      url: 'ext://studio/get-started-with-tableau-agent.html',
      note: 'How Tableau Agent works in Tableau Studio',
    },
    {
      title: 'Customize Tableau Agent',
      url: 'ext://studio/customize-tableau-agent.html',
      note: 'Override vendored skills and add your own',
    },
    {
      title: 'Tableau MCP',
      url: 'ext://mcp/docs/intro',
      note: 'Model Context Protocol server for Tableau',
    },
  ];
  return links.map((l) => {
    const parsed = parseExtProtocol(l.url);
    const href = parsed ? buildExtLinkModel(parsed.site, parsed.path, env).href : l.url;
    return {title: l.title, href, note: l.note};
  });
}

function skillsByCategory(skills: ParsedSkill[]): Map<string, ParsedSkill[]> {
  const byCategory = new Map<string, ParsedSkill[]>();
  for (const skill of skills) {
    const list = byCategory.get(skill.category) ?? [];
    list.push(skill);
    byCategory.set(skill.category, list);
  }
  return byCategory;
}

function familyCorpusNote(list: ParsedSkill[]): string {
  const n = list.length;
  const skillWord = n === 1 ? 'skill' : 'skills';
  return `SKILL.md plus when-to-use from the README for ${n} ${skillWord}`;
}

function buildLlmsTxt(skills: ParsedSkill[], env: ExtLinkEnv, paths: LlmsPaths): string {
  const sections: string[] = [];
  const byCategory = skillsByCategory(skills);
  sections.push(`# ${VARIABLES.site_title}`);
  sections.push('');
  sections.push(
    `> Skills that change how Tableau Agent authors, checks, and ships workbooks — and how you customize that default behavior.`,
  );
  sections.push('');
  sections.push(
    `Tableau Agent in ${VARIABLES.product_name} loads a skill when the short description at the top of \`SKILL.md\` matches the ask. The body is how to do the work. Supporting notes stay next to that file so the agent opens them only when the skill says to.`,
  );
  sections.push('');
  sections.push(
    `Installable skills from this catalog go in \`My Tableau Repository (Beta)/Tableau Agent/Skills/\`. Reload with \`/reload-skill\`. Skills labelled **EDIT WITH CAUTION** are tuned to Tableau Studio; changing them is not recommended. Place a same-name folder in the skills root to override an overridable skill.`,
  );
  sections.push('');
  sections.push(
    `This file is a curated index. Each corpus is SKILL.md plus the README when-to-use sections (not walkthroughs or reference catalogs). Machine-readable catalog: [catalog.json](${abs('/catalog.json')}). Generated from \`tableau-studio-skills/\` and \`tableau-mcp-skills/\`; do not edit by hand.`,
  );
  sections.push('');

  sections.push('## Docs');
  sections.push('');
  sections.push(
    listItem(
      VARIABLES.site_title,
      abs('/'),
      'Overview of installable skills, vendored overrides, and how to contribute',
    ),
  );
  sections.push(
    listItem(
      'Installable Skills',
      abs('/skills'),
      'Filterable catalog of downloadable Tableau Agent skills',
    ),
  );
  sections.push('');

  sections.push('## Full docs');
  sections.push('');
  sections.push(
    listItem(
      `${VARIABLES.site_title} — full corpus`,
      paths.fullUrl,
      'SKILL.md plus when-to-use from every README',
    ),
  );
  for (const category of CATEGORY_ORDER) {
    const list = byCategory.get(category);
    if (!list?.length) continue;
    sections.push(
      listItem(
        `${categoryLabel(category)} — full corpus`,
        paths.familyUrl(category),
        familyCorpusNote(list),
      ),
    );
  }
  sections.push('');

  for (const category of CATEGORY_ORDER) {
    const list = byCategory.get(category);
    if (!list?.length) continue;
    sections.push(`## ${categoryLabel(category)}`);
    sections.push('');
    sections.push(
      listItem(
        `${categoryLabel(category)} — full corpus`,
        paths.familyUrl(category),
        familyCorpusNote(list),
      ),
    );
    for (const skill of list) {
      const label = protectionLabel(skill.protection);
      sections.push(
        listItem(skill.title, abs(skill.permalink), `${label}. ${skill.description}`),
      );
      sections.push(
        listItem(
          `${skill.title} — SKILL.md`,
          abs(skill.skillPermalink),
          'Agent instructions (when to fire, steps, verification)',
        ),
      );
      sections.push(
        listItem(`${skill.title} — download`, abs(skill.download), `Zip of ${skill.name}/ for the skills directory`),
      );
    }
    sections.push('');
  }

  sections.push('## Optional');
  sections.push('');
  sections.push(listItem('Index (spec path)', abs('/llms.txt'), `Alias of ${paths.indexFile}`));
  sections.push(listItem('Combined corpus (spec path)', abs('/llms-full.txt'), `Alias of ${paths.fullFile}`));
  sections.push(listItem('Skill catalog (JSON)', abs('/catalog.json'), 'Machine-readable index of every installable skill'));
  sections.push(
    listItem('All skills zip', abs('/downloads/skills.zip'), 'Every installable skill folder in one archive'),
  );
  for (const doc of relatedDocs(env)) {
    sections.push(listItem(doc.title, doc.href, doc.note));
  }
  sections.push('');

  return sections.join('\n').replace(/\n{3,}/g, '\n\n');
}

function pageBlock(title: string, url: string, body: string): string {
  const heading = `# ${title}`;
  let rest = body.trim();
  if (rest === heading) {
    rest = '';
  } else if (rest.startsWith(`${heading}\n`)) {
    rest = rest.slice(heading.length).replace(/^\n+/, '');
  }
  return [heading, '', `Source: ${url}`, '', rest].join('\n');
}

function skillPageBlocks(skills: ParsedSkill[]): string[] {
  const parts: string[] = [];
  for (const skill of skills) {
    if (skill.useForBody) {
      parts.push(pageBlock(`${skill.title} — when to use`, abs(skill.permalink), skill.useForBody));
    }
    parts.push(pageBlock(`${skill.title} — SKILL.md`, abs(skill.skillPermalink), skill.skillBody));
  }
  return parts;
}

function joinCorpus(preamble: string[], blocks: string[]): string {
  const parts = [...preamble];
  for (const block of blocks) {
    parts.push('');
    parts.push('---');
    parts.push('');
    parts.push(block);
  }
  return parts.join('\n').replace(/\n{3,}/g, '\n\n') + '\n';
}

function catalogBlock(skills: ParsedSkill[]): string {
  const catalogLines = [
    '# Installable Skills',
    '',
    `Source: ${abs('/skills')}`,
    '',
    'Download a skill zip, place the folder in `My Tableau Repository (Beta)/Tableau Agent/Skills/`, and run `/reload-skill` in Tableau Studio.',
    '',
  ];
  for (const category of CATEGORY_ORDER) {
    const list = skills.filter((s) => s.category === category);
    if (!list.length) continue;
    catalogLines.push(`## ${categoryLabel(category)}`, '');
    for (const skill of list) {
      catalogLines.push(
        `- [${skill.title}](${abs(skill.permalink)}) (${protectionLabel(skill.protection)}): ${skill.description}`,
      );
    }
    catalogLines.push('');
  }
  return catalogLines.join('\n').trim();
}

function buildLlmsFull(
  skills: ParsedSkill[],
  overviewBody: string,
  env: ExtLinkEnv,
  paths: LlmsPaths,
): string {
  const related = relatedDocs(env);
  const relatedBlock = related.length
    ? [
        '# Related documentation',
        '',
        ...related.map((doc) => `- [${doc.title}](${doc.href}): ${doc.note}`),
      ].join('\n')
    : '';
  const familyList = CATEGORY_ORDER.filter((c) => skills.some((s) => s.category === c))
    .map((c) => `- [${categoryLabel(c)} — full corpus](${paths.familyUrl(c)})`)
    .join('\n');
  const preamble = [
    `# ${VARIABLES.site_title}`,
    '',
    `> Skills that change how Tableau Agent authors, checks, and ships workbooks — and how you customize that default behavior.`,
    '',
    `Corpus of ${VARIABLES.site_title}: each skill's README when-to-use sections and SKILL.md. Reference files stay on the live site. Index: [${paths.indexFile}](${paths.indexUrl}). Family files:`,
    '',
    familyList,
    '',
    `Generated from \`tableau-studio-skills/\` and \`tableau-mcp-skills/\`; do not edit by hand.`,
  ];
  const blocks = [
    pageBlock(VARIABLES.site_title, abs('/'), overviewBody),
    catalogBlock(skills),
    ...skillPageBlocks(skills),
  ];
  if (relatedBlock) blocks.push(relatedBlock);
  return joinCorpus(preamble, blocks);
}

function buildFamilyFull(category: string, list: ParsedSkill[], paths: LlmsPaths): string {
  const label = categoryLabel(category);
  const preamble = [
    `# ${VARIABLES.site_title} — ${label}`,
    '',
    `> ${label} skills for Tableau Agent in ${VARIABLES.product_name}: README when-to-use sections and SKILL.md.`,
    '',
    `Family corpus for ${label}. Index: [${paths.indexFile}](${paths.indexUrl}). Combined corpus: [${paths.fullFile}](${paths.fullUrl}). Generated from \`tableau-studio-skills/\` and \`tableau-mcp-skills/\`; do not edit by hand.`,
  ];
  return joinCorpus(preamble, skillPageBlocks(list));
}

function clearGeneratedDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, {recursive: true});
    return;
  }
  for (const name of fs.readdirSync(dir)) {
    if (name === '.gitkeep') continue;
    fs.rmSync(path.join(dir, name), {recursive: true, force: true});
  }
}

function writeOutputs(files: {name: string; contents: string}[], paths: LlmsPaths, commitCorpus: boolean) {
  const staticLlms = path.join(STATIC_DIR, 'llms');
  if (commitCorpus) clearGeneratedDir(LLMS_DIR);
  clearGeneratedDir(staticLlms);
  if (commitCorpus) fs.mkdirSync(LLMS_DIR, {recursive: true});
  fs.mkdirSync(staticLlms, {recursive: true});

  for (const file of files) {
    if (commitCorpus) fs.writeFileSync(path.join(LLMS_DIR, file.name), file.contents);
    fs.writeFileSync(path.join(staticLlms, file.name), file.contents);
  }

  const index = files.find((f) => f.name === paths.indexFile);
  const full = files.find((f) => f.name === paths.fullFile);
  if (index) fs.writeFileSync(path.join(STATIC_DIR, 'llms.txt'), index.contents);
  if (full) fs.writeFileSync(path.join(STATIC_DIR, 'llms-full.txt'), full.contents);
}

function main() {
  const env = outboundEnvFromGithubOrigin(process.env.GITHUB_ORIGIN);
  const paths = llmsPaths();
  const overviewRaw = fs.existsSync(OVERVIEW_PATH) ? fs.readFileSync(OVERVIEW_PATH, 'utf8') : '';
  const overview = prepareMarkdown(overviewRaw, env);

  const files = skillFiles();
  const skills = files.map((file) => parseSkill(file, env));
  skills.sort((a, b) => {
    const ia = SKILL_ORDER.indexOf(a.name);
    const ib = SKILL_ORDER.indexOf(b.name);
    return (ia === -1 ? 100 : ia) - (ib === -1 ? 100 : ib);
  });

  const byCategory = skillsByCategory(skills);
  const outputs: {name: string; contents: string}[] = [
    {name: paths.indexFile, contents: buildLlmsTxt(skills, env, paths)},
    {name: paths.fullFile, contents: buildLlmsFull(skills, overview.body, env, paths)},
  ];
  for (const category of CATEGORY_ORDER) {
    const list = byCategory.get(category);
    if (!list?.length) continue;
    outputs.push({
      name: paths.familyFile(category),
      contents: buildFamilyFull(category, list, paths),
    });
  }

  const commitCorpus = isPublicCorpusBuild(process.env.GITHUB_ORIGIN, process.env.GITHUB_BASE_PATH);
  writeOutputs(outputs, paths, commitCorpus);

  const kb = (n: number) => `${(n / 1024).toFixed(1)} KB`;
  console.log(
    commitCorpus
      ? `Wrote ${skills.length} skills → llms/ and site/static/llms/`
      : `Wrote ${skills.length} skills → site/static/llms/ (left committed llms/ unchanged)`,
  );
  for (const file of outputs) {
    console.log(`  ${file.name}  (${kb(Buffer.byteLength(file.contents))})`);
  }
}

main();
