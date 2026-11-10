/**
 * build-plugins-index.ts
 *
 * Second mockup — Claude plugins. This reads a Claude-style plugin marketplace
 * (plugins/.claude-plugin/marketplace.json) and each plugin's Claude manifest
 * (<plugin>/.claude-plugin/plugin.json), then enumerates the plugin's
 * components exactly as the Claude plugin architecture defines them:
 *
 *   skills/<name>/SKILL.md   (frontmatter: name, description, version)
 *   commands/*.md files      (frontmatter: description, argument-hint)
 *   agents/*.md files        (frontmatter: name, description, model)
 *   hooks/hooks.json         (event -> matchers)
 *   .mcp.json                (mcpServers)
 *
 * It fans this out into two consumers:
 *
 *   1. site/docs/plugins/<name>.mdx           — one Docusaurus page per plugin
 *      site/docs/plugins/<name>/<skill>.mdx   — one page per bundled skill
 *   2. site/static/plugins.json               — flat machine-readable index
 *
 * The shared tableau-studio-skills/ and tableau-mcp-skills/ catalogs and the first (skills) mockup are left untouched.
 *
 * Run with:  npm run build-plugins-index   (from site/, via ../scripts)
 */
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import matter from 'gray-matter';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PLUGINS_DIR = path.join(ROOT, 'plugins');
const MARKETPLACE_PATH = path.join(PLUGINS_DIR, '.claude-plugin', 'marketplace.json');
const PLUGIN_SCHEMA_PATH = path.join(ROOT, 'schema', 'plugin.schema.json');
const MARKETPLACE_SCHEMA_PATH = path.join(ROOT, 'schema', 'marketplace.schema.json');
const DOCS_DIR = path.join(ROOT, 'site', 'docs', 'plugins');
const PLUGINS_JSON_PATH = path.join(ROOT, 'site', 'static', 'plugins.json');

type Author = { name: string; email?: string };

type MarketplaceEntry = {
  name: string;
  source: string;
  description: string;
  category: string;
  keywords?: string[];
  author?: Author;
};

type Marketplace = {
  name: string;
  owner: Author;
  plugins: MarketplaceEntry[];
};

type PluginManifest = {
  name: string;
  version: string;
  description: string;
  author?: Author;
  homepage?: string;
  license?: string;
  keywords?: string[];
};

type SkillEntry = {
  name: string;
  description: string;
  version: string;
  scripts: string[];
  references: string[];
  permalink: string;
};

type CommandEntry = { name: string; description: string; argumentHint: string | null };
type AgentEntry = { name: string; description: string; model: string | null };

function listFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isFile())
    .map((e) => e.name);
}

function listDirs(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name);
}

const KEEP_IN_DOCS = new Set(['index.mdx']);

function rimrafGenerated() {
  if (!fs.existsSync(DOCS_DIR)) {
    fs.mkdirSync(DOCS_DIR, {recursive: true});
    return;
  }
  for (const entry of fs.readdirSync(DOCS_DIR, {withFileTypes: true})) {
    if (KEEP_IN_DOCS.has(entry.name)) continue;
    fs.rmSync(path.join(DOCS_DIR, entry.name), {recursive: true, force: true});
  }
}

function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(file, 'utf8')) as T;
}

// ---- component collectors -------------------------------------------------

function collectSkills(pluginDir: string, pluginName: string): {
  skills: SkillEntry[];
  errors: string[];
  pages: { file: string; contents: string }[];
} {
  const skillsRoot = path.join(pluginDir, 'skills');
  const skills: SkillEntry[] = [];
  const errors: string[] = [];
  const pages: { file: string; contents: string }[] = [];

  for (const slug of listDirs(skillsRoot).sort()) {
    const skillDir = path.join(skillsRoot, slug);
    const skillMd = path.join(skillDir, 'SKILL.md');
    if (!fs.existsSync(skillMd)) continue;
    const { data, content } = matter(fs.readFileSync(skillMd, 'utf8'));
    const fm = data as { name?: string; description?: string; version?: string };
    if (!fm.name || !fm.description) {
      errors.push(`${pluginName}/skills/${slug}/SKILL.md: missing name/description frontmatter`);
      continue;
    }
    if (fm.name !== slug) {
      errors.push(
        `${pluginName}/skills/${slug}/SKILL.md: frontmatter name "${fm.name}" must equal folder "${slug}"`,
      );
    }

    const scripts = listFiles(path.join(skillDir, 'scripts')).sort();
    const references = listFiles(skillDir)
      .filter((f) => f.endsWith('.md') && f !== 'SKILL.md')
      .concat(listFiles(path.join(skillDir, 'references')).map((f) => `references/${f}`))
      .sort();

    const permalink = `/plugins/${pluginName}/${slug}`;
    skills.push({
      name: fm.name,
      description: fm.description,
      version: String(fm.version ?? '—'),
      scripts: scripts.map((s) => `skills/${slug}/scripts/${s}`),
      references,
      permalink,
    });

    pages.push({
      file: path.join(DOCS_DIR, pluginName, `${slug}.mdx`),
      contents: skillPage(fm.name, fm.description, String(fm.version ?? '—'), pluginName, scripts, references, content),
    });
  }

  return { skills, errors, pages };
}

function collectCommands(pluginDir: string): CommandEntry[] {
  const dir = path.join(pluginDir, 'commands');
  return listFiles(dir)
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => {
      const { data } = matter(fs.readFileSync(path.join(dir, f), 'utf8'));
      const fm = data as { description?: string; 'argument-hint'?: string };
      return {
        name: `/${path.basename(f, '.md')}`,
        description: fm.description ?? '',
        argumentHint: fm['argument-hint'] ?? null,
      };
    });
}

function collectAgents(pluginDir: string): AgentEntry[] {
  const dir = path.join(pluginDir, 'agents');
  return listFiles(dir)
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => {
      const { data } = matter(fs.readFileSync(path.join(dir, f), 'utf8'));
      const fm = data as { name?: string; description?: string; model?: string };
      return {
        name: fm.name ?? path.basename(f, '.md'),
        description: fm.description ?? '',
        model: fm.model ?? null,
      };
    });
}

function collectHookEvents(pluginDir: string): string[] {
  const file = path.join(pluginDir, 'hooks', 'hooks.json');
  if (!fs.existsSync(file)) return [];
  const json = readJson<{ hooks?: Record<string, unknown> }>(file);
  return Object.keys(json.hooks ?? {}).sort();
}

function collectMcpServers(pluginDir: string): string[] {
  const file = path.join(pluginDir, '.mcp.json');
  if (!fs.existsSync(file)) return [];
  const json = readJson<{ mcpServers?: Record<string, unknown> }>(file);
  return Object.keys(json.mcpServers ?? {}).sort();
}

// ---- page templates -------------------------------------------------------

function skillPage(
  name: string,
  description: string,
  version: string,
  pluginName: string,
  scripts: string[],
  references: string[],
  body: string,
): string {
  const meta = [
    `| | |`,
    `| --- | --- |`,
    `| **Skill** | \`${name}\` |`,
    `| **Version** | ${version} |`,
    `| **Bundled in** | [${pluginName}](/plugins/${pluginName}) |`,
    `| **Scripts** | ${scripts.length ? scripts.map((s) => `\`${s}\``).join(', ') : '—'} |`,
    `| **References** | ${references.length ? references.map((r) => `\`${r}\``).join(', ') : '—'} |`,
  ].join('\n');

  return `---
title: ${name}
description: ${JSON.stringify(description)}
---

# ${name}

> ${description}

${meta}

${body.trim()}
`;
}

function pluginPage(
  entry: MarketplaceEntry,
  manifest: PluginManifest,
  skills: SkillEntry[],
  commands: CommandEntry[],
  agents: AgentEntry[],
  hooks: string[],
  mcp: string[],
  readme: string | null,
): string {
  const author = manifest.author?.name ?? entry.author?.name ?? '—';
  const meta = [
    `| | |`,
    `| --- | --- |`,
    `| **Name** | \`${manifest.name}\` |`,
    `| **Version** | ${manifest.version} |`,
    `| **Category** | \`${entry.category}\` |`,
    `| **Author** | ${author} |`,
    `| **Keywords** | ${(manifest.keywords ?? entry.keywords ?? []).map((k) => `\`${k}\``).join(' ') || '—'} |`,
  ].join('\n');

  const install = `## Install

\`\`\`bash
/plugin marketplace add tableau/tableau-ai-utilities
/plugin install ${manifest.name}@tableau-ai-utilities
\`\`\``;

  const skillsSection = skills.length
    ? `## Skills\n\n${skills
        .map(
          (s) =>
            `- [${s.name}](${s.permalink}) — ${s.description}${
              s.scripts.length ? ` <br/>_scripts:_ ${s.scripts.map((x) => `\`${path.basename(x)}\``).join(', ')}` : ''
            }`,
        )
        .join('\n')}\n`
    : '';

  const commandsSection = commands.length
    ? `## Commands\n\n${commands
        .map((c) => `- \`${c.name}\`${c.argumentHint ? ` \`${c.argumentHint}\`` : ''} — ${c.description}`)
        .join('\n')}\n`
    : '';

  const agentsSection = agents.length
    ? `## Agents\n\n${agents
        .map((a) => `- \`${a.name}\`${a.model ? ` _(model: ${a.model})_` : ''} — ${a.description}`)
        .join('\n')}\n`
    : '';

  const hooksSection = hooks.length ? `## Hooks\n\n- Events: ${hooks.map((h) => `\`${h}\``).join(', ')}\n` : '';
  const mcpSection = mcp.length ? `## MCP servers\n\n- ${mcp.map((m) => `\`${m}\``).join(', ')}\n` : '';

  return `---
title: ${manifest.name}
description: ${JSON.stringify(entry.description)}
tags:
  - ${entry.category}
---

# ${manifest.name}

> ${manifest.description}

${meta}

${skillsSection}
${commandsSection}
${agentsSection}
${hooksSection}
${mcpSection}
${install}

${readme ? `---\n\n${readme.trim()}\n` : ''}`;
}

// ---- main -----------------------------------------------------------------

function writeEmpty(reason: string) {
  fs.mkdirSync(DOCS_DIR, {recursive: true});
  rimrafGenerated();
  fs.mkdirSync(path.dirname(PLUGINS_JSON_PATH), {recursive: true});
  fs.writeFileSync(PLUGINS_JSON_PATH, '[]\n');
  console.log(`${reason}; wrote empty plugins.json`);
}

function main() {
  if (!fs.existsSync(MARKETPLACE_PATH)) {
    writeEmpty('No marketplace found');
    return;
  }

  const ajv = new Ajv({ allErrors: true });
  addFormats(ajv);
  const validateMarketplace = ajv.compile(readJson(MARKETPLACE_SCHEMA_PATH));
  const validatePlugin = ajv.compile(readJson(PLUGIN_SCHEMA_PATH));

  const marketplace = readJson<Marketplace>(MARKETPLACE_PATH);
  if (!marketplace.plugins?.length) {
    writeEmpty('Marketplace lists no plugins');
    return;
  }
  if (!validateMarketplace(marketplace)) {
    console.error('\n✗ marketplace.json schema errors:');
    for (const e of validateMarketplace.errors ?? []) {
      console.error(`  - ${e.instancePath || '(root)'} ${e.message}`);
    }
    process.exit(1);
  }

  rimrafGenerated();

  const index: Array<Record<string, unknown>> = [];
  const errors: string[] = [];

  for (const entry of [...marketplace.plugins].sort((a, b) => a.name.localeCompare(b.name))) {
    const pluginDir = path.resolve(PLUGINS_DIR, entry.source);
    const manifestPath = path.join(pluginDir, '.claude-plugin', 'plugin.json');
    if (!fs.existsSync(manifestPath)) {
      errors.push(`${entry.name}: no .claude-plugin/plugin.json at ${entry.source}`);
      continue;
    }

    const manifest = readJson<PluginManifest>(manifestPath);
    if (!validatePlugin(manifest)) {
      for (const e of validatePlugin.errors ?? []) {
        errors.push(`${entry.name}/plugin.json: ${e.instancePath || '(root)'} ${e.message}`);
      }
      continue;
    }
    if (manifest.name !== entry.name) {
      errors.push(`${entry.name}: plugin.json name "${manifest.name}" != marketplace name "${entry.name}"`);
    }

    const { skills, errors: skillErrors, pages } = collectSkills(pluginDir, manifest.name);
    errors.push(...skillErrors);
    const commands = collectCommands(pluginDir);
    const agents = collectAgents(pluginDir);
    const hooks = collectHookEvents(pluginDir);
    const mcp = collectMcpServers(pluginDir);
    const readmePath = path.join(pluginDir, 'README.md');
    const readme = fs.existsSync(readmePath) ? fs.readFileSync(readmePath, 'utf8') : null;

    // Write the plugin overview page + each bundled skill page.
    fs.writeFileSync(
      path.join(DOCS_DIR, `${manifest.name}.mdx`),
      pluginPage(entry, manifest, skills, commands, agents, hooks, mcp, readme),
    );
    for (const page of pages) {
      fs.mkdirSync(path.dirname(page.file), { recursive: true });
      fs.writeFileSync(page.file, page.contents);
    }

    index.push({
      name: manifest.name,
      version: manifest.version,
      description: manifest.description,
      category: entry.category,
      keywords: manifest.keywords ?? entry.keywords ?? [],
      author: manifest.author ?? entry.author ?? null,
      homepage: manifest.homepage ?? null,
      license: manifest.license ?? null,
      skills,
      commands,
      agents,
      hooks,
      mcpServers: mcp,
      permalink: `/plugins/${manifest.name}`,
    });

    console.log(
      `✓ ${manifest.name}  (v${manifest.version}, ${entry.category}) — ${skills.length} skills, ${commands.length} commands, ${agents.length} agents, ${hooks.length} hook events, ${mcp.length} mcp`,
    );
  }

  if (errors.length) {
    console.error(`\n✗ build-plugins-index failed (${errors.length} problem${errors.length > 1 ? 's' : ''}):`);
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(PLUGINS_JSON_PATH), { recursive: true });
  fs.writeFileSync(PLUGINS_JSON_PATH, JSON.stringify(index, null, 2) + '\n');
  console.log(`\nWrote ${index.length} plugins → ${path.relative(ROOT, PLUGINS_JSON_PATH)}`);
}

main();
