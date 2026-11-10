/** Export repository skills as locally validated .tskill packages. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {TextDecoder} from 'node:util';
import {writeZip, type ZipEntry} from './zip.ts';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKIP_DIRS = new Set(['node_modules', 'dist', 'build', '__pycache__', 'coverage', 'venv']);
const TEXT_EXTENSIONS = new Set(['.md', '.py', '.txt']);
const MANIFEST = 'export-manifest.json';
const GENERATOR = 'export-repo-skills';
const portable = (value: string): string => value.split(path.sep).join('/');
const ignored = (name: string): boolean => name.startsWith('.') || SKIP_DIRS.has(name) || name.endsWith('.pyc');
const inside = (parent: string, child: string): boolean => {
  const relative = path.relative(parent, child);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
};

export interface SkillRecord {
  source: string;
  package: string;
  generated_readme: boolean;
  resources: Record<string, string>;
  excluded: string[];
  relocated_scripts: string[];
}

export function discoverSkills(repo: string, output: string): string[] {
  const skills: string[] = [];
  function walk(dir: string) {
    const entries = fs.readdirSync(dir, {withFileTypes: true}).sort((a, b) => a.name.localeCompare(b.name));
    if (entries.some(entry => entry.name === 'SKILL.md' && !entry.isDirectory())) {
      skills.push(dir);
      return;
    }
    for (const entry of entries) {
      const target = path.join(dir, entry.name);
      if (entry.isDirectory() && !ignored(entry.name) && target !== output) walk(target);
    }
  }
  walk(repo);
  return skills.sort();
}

function resourceFiles(skill: string): {files: string[]; excluded: string[]} {
  const files: string[] = [];
  const excluded: string[] = [];
  function walk(dir: string) {
    for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
      const target = path.join(dir, entry.name);
      const relative = portable(path.relative(skill, target));
      if (entry.isSymbolicLink()) throw new Error(`Symlink unsupported: ${target}`);
      if (ignored(entry.name) || (entry.isDirectory() && relative === 'agents')) {
        excluded.push(relative + (entry.isDirectory() ? '/' : ''));
      } else if (entry.isDirectory()) {
        walk(target);
      } else if (entry.isFile()) {
        files.push(target);
      } else {
        throw new Error(`Unsupported filesystem entry: ${target}`);
      }
    }
  }
  walk(skill);
  return {files: files.sort(), excluded: excluded.sort()};
}

export function rewriteMarkdown(text: string, source: string, mapping: Record<string, string>): string {
  const replacements = new Map<string, string>();
  for (const [relative, destination] of Object.entries(mapping)) {
    const updated = path.posix.relative(path.posix.dirname(mapping[source]), destination);
    for (const old of [relative, path.posix.relative(path.posix.dirname(source), relative)]) {
      replacements.set(old, updated);
    }
  }
  const escaped = [...replacements.keys()].sort((a, b) => b.length - a.length)
    .map(value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (!escaped.length) return text;
  const pattern = new RegExp(`(?<![\\w/.:\\\\-])(?:\\./)?(${escaped.join('|')})(?![\\w/.\\\\-])`, 'g');
  return text.replace(pattern, (_match, old: string) => replacements.get(old)!);
}

export function packageSkill(skill: string, repo: string, staging: string): SkillRecord {
  const relative = portable(path.relative(repo, skill));
  const filename = (relative || path.basename(repo)).replace(/[^a-zA-Z0-9_-]+/g, '--') + '.tskill';
  const {files, excluded} = resourceFiles(skill);
  const mapping: Record<string, string> = Object.create(null);
  const seen = new Set<string>();
  for (const source of files) {
    const rel = portable(path.relative(skill, source));
    let destination = rel;
    if (rel !== 'SKILL.md' && rel !== 'README.md') {
      let name = rel.replaceAll('/', '__');
      if (['LICENSE', 'NOTICE'].includes(path.basename(source))) name += '.txt';
      else if (!TEXT_EXTENSIONS.has(path.extname(source).toLowerCase())) throw new Error(`Unsupported resource: ${source}`);
      destination = `skill-expertise/${name}`;
    }
    if (seen.has(destination.toLowerCase())) throw new Error(`Resource filename collision in ${skill}: ${destination}`);
    seen.add(destination.toLowerCase());
    mapping[rel] = destination;
  }
  const contents = new Map<string, Buffer>();
  for (const source of files) {
    const rel = portable(path.relative(skill, source));
    let data = fs.readFileSync(source);
    if (path.extname(source).toLowerCase() === '.md') {
      const text = new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(data);
      data = Buffer.from(rewriteMarkdown(text, rel, mapping));
    }
    contents.set(mapping[rel], data);
  }
  if (!contents.has('SKILL.md')) throw new Error(`Missing root SKILL.md: ${skill}`);
  const generatedReadme = !contents.has('README.md');
  if (generatedReadme) contents.set('README.md', contents.get('SKILL.md')!);
  const destination = path.join(staging, filename);
  // Check case-insensitively for portability across destination filesystems.
  if (fs.readdirSync(staging).some(name => name.toLowerCase() === filename.toLowerCase())) {
    throw new Error(`Package filename collision: ${filename}`);
  }
  const entries = [...contents].sort(([a], [b]) => a.localeCompare(b)).map(([name, data]) => ({name, data}));
  validateSkillEntries(filename, entries);
  writeZip(destination, entries);
  return {source: relative, package: filename, generated_readme: generatedReadme,
    resources: mapping, excluded, relocated_scripts: Object.keys(mapping).filter(name => name.endsWith('.py'))};
}

/** Validate the exact file list before passing it to the ZIP writer. */
export function validateSkillEntries(filename: string, entries: ZipEntry[]): void {
  if (!filename.toLowerCase().endsWith('.tskill')) throw new Error('Skills require a .tskill ZIP package');
  const names = new Set(entries.map(entry => entry.name));
  if (names.size !== entries.length) throw new Error(`${filename}: duplicate package filenames`);
  for (const required of ['SKILL.md', 'README.md']) {
    if (!names.has(required)) {
      throw new Error(`${filename}: the .tskill package must contain ${required} at the root level`);
    }
  }
  for (const {name} of entries) {
    if (['SKILL.md', 'README.md'].includes(name)) continue;
    if (name.startsWith('skill-expertise/')) {
      const leaf = name.slice('skill-expertise/'.length);
      if (!leaf.includes('/') && !leaf.includes('\\') &&
          !leaf.includes('\0') && /\.(md|py|txt)$/i.test(leaf)) continue;
      throw new Error(`${filename}: skill-expertise may only contain flat .md, .py, or .txt files`);
    }
    throw new Error(`${filename}: only SKILL.md, README.md, and the optional skill-expertise folder are allowed at the root level`);
  }
}

function checkReplacement(output: string, replace: boolean) {
  if (!fs.existsSync(output)) return;
  if (fs.lstatSync(output).isSymbolicLink()) throw new Error('Output must not be a symlink');
  if (!replace || !fs.existsSync(path.join(output, MANIFEST))) {
    throw new Error('Output exists; choose a fresh folder or use --replace for a generated export');
  }
  const prior = JSON.parse(fs.readFileSync(path.join(output, MANIFEST), 'utf8'));
  if (prior.generator !== GENERATOR || !Array.isArray(prior.skills)) throw new Error('Unrecognized export manifest');
  const expected = new Set([MANIFEST, ...prior.skills.map((item: SkillRecord) => item.package)]);
  const actual = fs.readdirSync(output, {withFileTypes: true});
  if (actual.length !== expected.size || actual.some(entry => !entry.isFile() || !expected.has(entry.name))) {
    throw new Error('Existing output contains unrecognized files; choose a fresh folder');
  }
}

export interface ExportOptions {repo: string; output: string; replace: boolean}

export function exportSkills({repo, output, replace}: ExportOptions): SkillRecord[] {
  if (!fs.statSync(repo).isDirectory()) throw new Error(`Repository missing: ${repo}`);
  if (inside(output, repo)) throw new Error('Output cannot be the repository or an ancestor');
  checkReplacement(output, replace);
  const skills = discoverSkills(repo, output);
  if (!skills.length) throw new Error('No SKILL.md files found');
  if (skills.some(skill => inside(skill, output))) throw new Error('Output must not be inside a source skill');
  fs.mkdirSync(path.dirname(output), {recursive: true});
  const staging = fs.mkdtempSync(path.join(path.dirname(output), '.tskill-export-'));
  try {
    const records = skills.map(skill => packageSkill(skill, repo, staging));
    const validation = {validated: records.length};
    const manifest = {generator: GENERATOR, repository: repo,
      validator: 'pre-zip-tskill-structure-v1', validation, skills: records};
    fs.writeFileSync(path.join(staging, MANIFEST), JSON.stringify(manifest, null, 2) + '\n');
    // Preserve the previous export if validation or ZIP creation failed.
    checkReplacement(output, replace);
    if (fs.existsSync(output)) fs.rmSync(output, {recursive: true});
    fs.renameSync(staging, output);
    return records;
  } finally {
    fs.rmSync(staging, {recursive: true, force: true});
  }
}

function resolvePath(value: string): string {
  const expanded = value === '~' ? os.homedir() : value.startsWith('~/') ? path.join(os.homedir(), value.slice(2)) : value;
  const absolute = path.resolve(expanded);
  // Resolve existing ancestors too, so a symlinked parent cannot target source skills.
  if (fs.existsSync(absolute)) return fs.realpathSync(absolute);
  const parent = path.dirname(absolute);
  return parent === absolute ? absolute : path.join(resolvePath(parent), path.basename(absolute));
}

function main(args: string[]) {
  if (args.includes('--help') || args.includes('-h')) {
    console.log('Usage: node scripts/run-tsx.cjs scripts/export-skills.ts [--output PATH] [--replace]\n' +
      'Always scans this repository; default output: dist/tskills.\n' +
      'Validates package structure before ZIP creation.');
    return;
  }
  const values = new Map<string, string>();
  let replace = false;
  for (let i = 0; i < args.length; i++) {
    const flag = args[i];
    if (flag === '--replace') replace = true;
    else if (flag === '--output' && args[i + 1] && !args[i + 1].startsWith('--')) {
      values.set(flag, args[++i]);
    } else throw new Error(`Unknown option or missing value: ${flag}`);
  }
  const repo = resolvePath(ROOT);
  const output = resolvePath(values.get('--output') ?? path.join(repo, 'dist/tskills'));
  const records = exportSkills({repo, output, replace});
  console.log(`Exported and locally validated ${records.length} packages: ${output}`);
  console.log(`Manifest: ${path.join(output, MANIFEST)}. Relocated Python files require separate runtime testing.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 1; }
}
