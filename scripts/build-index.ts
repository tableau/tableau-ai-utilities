/**
 * build-index.ts
 *
 * Walks every SKILL.md under tableau-studio-skills/ and tableau-mcp-skills/, then fans each skill out into:
 *
 *   1. site/docs/<same path as the skill folder>/index.md
 *   2. site/docs/<same path as the skill folder>/SKILL.md
 *   3. site/docs/<same path as the skill folder>/resources/
 *   4. site/static/downloads/<name>.zip
 *   5. site/static/catalog.json
 *
 * `npm run build-indexes` also runs build-llms.ts after this. Every build
 * copies the corpora to site/static/llms/. A public build also rewrites the
 * committed llms/ directory (index, SKILL.md + when-to-use corpora).
 *
 * An empty skill tree is a no-op for that root (writes catalog.json = [] when both are empty).
 * Does not delete site/docs/skills.mdx.
 */
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import matter from 'gray-matter';
import {protectionFor} from './protection';
import {
  CATEGORY_BY_SKILL,
  CATEGORY_LABELS,
  SKILL_ORDER,
  SKILL_ROOTS,
  categoryLabel,
  treeLabel,
  treePosition,
} from './categories';
import {collectDir, writeZip} from './zip';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const DOCS_DIR = path.join(ROOT, 'site', 'docs');
const CATALOG_PATH = path.join(ROOT, 'site', 'static', 'catalog.json');
const DOWNLOADS_DIR = path.join(ROOT, 'site', 'static', 'downloads');

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

function yamlString(value: string): string {
  return JSON.stringify(value);
}

function skillFiles(): string[] {
  return SKILL_ROOTS.flatMap((root) => walkSkillMd(path.join(ROOT, root))).sort();
}

function clearGeneratedDocs() {
  for (const root of SKILL_ROOTS) {
    fs.rmSync(path.join(DOCS_DIR, root), {recursive: true, force: true});
  }
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

function pythonPage(abs: string, raw: string): string {
  const longest = Math.max(0, ...(raw.match(/`+/g) ?? []).map((m) => m.length));
  const fence = '`'.repeat(Math.max(3, longest + 1));
  return `# ${path.basename(abs)}\n\n${fence}python\n${raw.replace(/\r\n/g, '\n').trimEnd()}\n${fence}\n`;
}

function collectResourceMarkdown(skillDir: string): {rel: string; dest: string; contents: string}[] {
  const files: {rel: string; dest: string; contents: string}[] = [];

  function addMarkdown(abs: string, rel: string) {
    const isPy = abs.endsWith('.py');
    if (!isPy && !abs.endsWith('.md') && !abs.endsWith('.mdx')) return;
    if (isSkillOrReadme(abs)) return;
    const raw = fs.readFileSync(abs, 'utf8');
    files.push({rel, dest: flattenRel(rel), contents: isPy ? pythonPage(abs, raw) : raw});
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
  for (const folder of ['references', 'examples', 'resources', 'testing', 'skill-expertise', 'skill-experience', 'skill-experiences']) {
    walk(path.join(skillDir, folder), (folder === 'references' || folder === 'skill-expertise' || folder === 'skill-experience' || folder === 'skill-experiences') ? '' : folder);
  }
  return files;
}

function rewriteLocalMdLinks(
  markdown: string,
  resourcesPrefix: string,
  resources: {rel: string; dest: string}[],
): string {
  return markdown.replace(/\]\(([^)]+)\)/g, (full, url: string) => {
    const [pathPart, ...hashParts] = url.split('#');
    const hash = hashParts.length ? `#${hashParts.join('#')}` : '';
    const clean = pathPart.trim();
    if (!clean || /^[a-z][a-z0-9+.-]*:/i.test(clean) || clean.startsWith('/') || clean.startsWith('#')) {
      return full;
    }
    const posix = clean.replace(/\\/g, '/').replace(/^\.\//, '');
    const stripped = posix.replace(/^(references|examples|resources|testing)\//, '');
    const base = posix.split('/').pop() ?? posix;
    const match =
      resources.find((r) => r.rel === posix || r.rel === stripped) ??
      resources.find((r) => path.posix.basename(r.rel) === base);
    if (!match) return full;
    const destName = match.dest.replace(/\.mdx?$/, '');
    return `](${resourcesPrefix}${destName}${hash})`;
  });
}

function detailsPage(opts: {
  title: string;
  description: string;
  name: string;
  position: number;
  body: string;
}): string {
  return `---
title: ${yamlString(opts.title)}
description: ${yamlString(opts.description)}
sidebar_label: ${yamlString(opts.title)}
sidebar_position: ${opts.position}
hide_title: true
mdx:
  format: md
---

${opts.body.trim()}
`;
}

function skillDocPage(opts: {title: string; description: string; name: string; body: string}): string {
  return `---
title: ${yamlString(`${opts.title} — SKILL.md`)}
description: ${yamlString(opts.description)}
sidebar_label: SKILL.md
sidebar_position: 1
hide_title: true
mdx:
  format: md
---

${opts.body.trim()}
`;
}

function resourcePage(filename: string, raw: string): string {
  const {content} = matter(raw);
  const title = firstHeading(content) ?? titleize(path.basename(filename, path.extname(filename)));
  const body = content.trim() || raw.trim();
  return `---
title: ${yamlString(title)}
sidebar_label: ${yamlString(path.basename(filename))}
mdx:
  format: md
---

${body}
`;
}

function writeCategoryJson(dir: string, label: string, position?: number) {
  const payload: Record<string, unknown> = {label};
  if (position != null) payload.position = position;
  fs.mkdirSync(dir, {recursive: true});
  fs.writeFileSync(path.join(dir, '_category_.json'), JSON.stringify(payload, null, 2) + '\n');
}

function zipManySkills(entries: {name: string; skillDir: string}[], destZip: string) {
  if (fs.existsSync(destZip)) fs.rmSync(destZip);
  writeZip(
    destZip,
    entries.flatMap((e) => collectDir(e.skillDir, e.name)),
  );
}

function zipSkill(skillDir: string, destZip: string) {
  if (fs.existsSync(destZip)) fs.rmSync(destZip);
  writeZip(destZip, collectDir(skillDir));
}

function parseSkill(file: string): {
  name: string;
  category: string;
  route: string;
  description: string;
  title: string;
  skillBody: string;
  skillDir: string;
} {
  const skillDir = path.dirname(file);
  const folder = path.basename(skillDir);
  const rel = path.relative(ROOT, skillDir).split(path.sep);
  const categoryFromPath = rel.length >= 2 ? rel[rel.length - 2] : CATEGORY_BY_SKILL[folder];
  const raw = fs.readFileSync(file, 'utf8');
  const {data, content} = matter(raw);
  const fm = data as {name?: string; description?: string};
  const name = (typeof fm.name === 'string' && fm.name) || folder;
  const category = categoryFromPath || CATEGORY_BY_SKILL[name];
  if (!category || !CATEGORY_LABELS[category]) {
    throw new Error(
      `${path.relative(ROOT, file)}: put this skill under tableau-studio-skills/tableau-agent/<category>/${name}/ or tableau-mcp-skills/<harness>/${name}/`,
    );
  }
  const description =
    (typeof fm.description === 'string' && fm.description.trim()) || firstParagraph(content) || titleize(name);
  const title = firstHeading(content) ?? titleize(name);
  return {name, category, route: rel.join('/'), description, title, skillBody: content, skillDir};
}

function main() {
  fs.mkdirSync(DOCS_DIR, {recursive: true});
  clearGeneratedDocs();
  if (fs.existsSync(DOWNLOADS_DIR)) {
    fs.rmSync(DOWNLOADS_DIR, {recursive: true, force: true});
  }
  fs.mkdirSync(DOWNLOADS_DIR, {recursive: true});

  const files = skillFiles();
  if (files.length === 0) {
    fs.mkdirSync(path.dirname(CATALOG_PATH), {recursive: true});
    fs.writeFileSync(CATALOG_PATH, '[]\n');
    console.log('No SKILL.md files under tableau-studio-skills/ or tableau-mcp-skills/; wrote empty catalog.json');
    return;
  }

  const catalog: Array<Record<string, unknown>> = [];
  const zipEntries: {name: string; skillDir: string}[] = [];

  for (const file of files) {
    const parsed = parseSkill(file);
    const {name, category, route, description, skillDir} = parsed;
    const protection = protectionFor(name, category);
    const skillPos = SKILL_ORDER.indexOf(name);
    const sidebarPos = skillPos === -1 ? 100 : skillPos + 1;

    const readmePath = findReadme(skillDir);
    const fromReadme = Boolean(readmePath);
    const detailsRaw = fromReadme ? fs.readFileSync(readmePath!, 'utf8') : parsed.skillBody;
    const {content: detailsContent} = matter(detailsRaw);
    const heading = firstHeading(detailsContent) ?? parsed.title;
    const title = heading === name ? titleize(name) : heading;

    const resources = collectResourceMarkdown(skillDir);

    const permalink = `/${route}`;
    const detailsBody = rewriteLocalMdLinks(detailsContent, `${permalink}/resources/`, resources);
    const skillBody = rewriteLocalMdLinks(parsed.skillBody, `${permalink}/resources/`, resources);

    const routeParts = route.split('/');
    const skillDocsDir = path.join(DOCS_DIR, ...routeParts);
    fs.mkdirSync(skillDocsDir, {recursive: true});
    for (let i = 1; i < routeParts.length - 1; i++) {
      const slug = routeParts[i];
      const label = treeLabel(slug);
      writeCategoryJson(
        path.join(DOCS_DIR, ...routeParts.slice(0, i + 1)),
        label === slug ? titleize(slug) : label,
        treePosition(slug),
      );
    }
    writeCategoryJson(skillDocsDir, title, sidebarPos);

    fs.writeFileSync(
      path.join(skillDocsDir, 'index.md'),
      detailsPage({
        title,
        description,
        name,
        position: 0,
        body: detailsBody,
      }),
    );
    fs.writeFileSync(
      path.join(skillDocsDir, 'SKILL.md'),
      skillDocPage({title, description, name, body: skillBody}),
    );

    if (resources.length) {
      const resourcesDir = path.join(skillDocsDir, 'resources');
      writeCategoryJson(resourcesDir, 'Skill Expertise', 2);
      for (const res of resources) {
        const rewritten = rewriteLocalMdLinks(res.contents, './', resources);
        fs.writeFileSync(path.join(resourcesDir, res.dest), resourcePage(res.rel, rewritten));
      }
    }

    const destZip = path.join(DOWNLOADS_DIR, `${name}.zip`);
    zipSkill(skillDir, destZip);
    zipEntries.push({name, skillDir});

    catalog.push({
      id: route,
      name,
      title,
      description,
      category,
      categoryLabel: categoryLabel(category),
      protection,
      keywords: [],
      hasReadme: fromReadme,
      permalink,
      download: `/downloads/${name}.zip`,
    });

    console.log(
      `✓ ${route}  (${protection}${fromReadme ? ', README' : ', SKILL.md details'}, ${resources.length} resources)`,
    );
  }

  catalog.sort((a, b) => {
    const ia = SKILL_ORDER.indexOf(String(a.name));
    const ib = SKILL_ORDER.indexOf(String(b.name));
    return (ia === -1 ? 100 : ia) - (ib === -1 ? 100 : ib);
  });
  zipEntries.sort((a, b) => {
    const ia = SKILL_ORDER.indexOf(a.name);
    const ib = SKILL_ORDER.indexOf(b.name);
    return (ia === -1 ? 100 : ia) - (ib === -1 ? 100 : ib);
  });
  zipManySkills(zipEntries, path.join(DOWNLOADS_DIR, 'skills.zip'));

  fs.mkdirSync(path.dirname(CATALOG_PATH), {recursive: true});
  fs.writeFileSync(CATALOG_PATH, JSON.stringify(catalog, null, 2) + '\n');
  console.log(`\nWrote ${catalog.length} skills → ${path.relative(ROOT, CATALOG_PATH)}`);
}

main();
