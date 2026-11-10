/**
 * validate.ts — CI gate for every PR.
 *
 * Checks each tableau-studio-skills and tableau-mcp-skills SKILL.md for:
 *   - portable frontmatter (name + description) when YAML is present
 *   - frontmatter name matches the skill folder
 *
 * Empty skill trees are valid.
 */
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import matter from 'gray-matter';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import {CATEGORY_BY_SKILL, CATEGORY_LABELS, SKILL_ROOTS} from './categories';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
function skillFiles(): string[] {
  return SKILL_ROOTS.flatMap((root) => walk(path.join(ROOT, root))).sort();
}
const SCHEMA_PATH = path.join(ROOT, 'schema', 'skill.schema.json');
const NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function walk(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  const out: string[] = [];
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name === 'SKILL.md') out.push(full);
  }
  return out;
}

function main() {
  const ajv = new Ajv({allErrors: true});
  addFormats(ajv);
  const validate = ajv.compile(JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf8')));

  const files = skillFiles();
  const errors: string[] = [];

  for (const file of files) {
    const rel = path.relative(ROOT, file);
    const skillDir = path.dirname(file);
    const folder = path.basename(skillDir);
    const relDir = path.relative(ROOT, skillDir).split(path.sep).join('/');
    const {data} = matter(fs.readFileSync(file, 'utf8'));
    const fm = data as {name?: string; description?: string};
    const hasFrontmatter = Object.keys(fm).length > 0;
    const name = fm.name || folder;
    const expectedCategory = CATEGORY_BY_SKILL[name];
    const parts = relDir.split('/');

    if (parts.length < 3 || !CATEGORY_LABELS[parts[parts.length - 2]]) {
      errors.push(
        `${rel}: skill must live under tableau-studio-skills/tableau-agent/<category>/${folder}/ or tableau-mcp-skills/<harness>/${folder}/`,
      );
    } else if (expectedCategory && parts[parts.length - 2] !== expectedCategory) {
      errors.push(
        `${rel}: category folder "${parts[parts.length - 2]}" should be "${expectedCategory}" per the Complete Reference`,
      );
    }

    if (!NAME_RE.test(folder)) {
      errors.push(`${rel}: folder "${folder}" must be kebab-case`);
    }

    if (hasFrontmatter) {
      if (!validate(fm)) {
        for (const e of validate.errors ?? []) {
          errors.push(`${rel}: ${e.instancePath || '(root)'} ${e.message}`);
        }
      }
      if (fm.name && fm.name !== folder) {
        errors.push(`${rel}: name "${fm.name}" must equal folder "${folder}"`);
      }
    }
  }

  if (errors.length) {
    console.error(`✗ validate failed (${errors.length} problem${errors.length > 1 ? 's' : ''}):`);
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }
  console.log(`✓ validate passed: ${files.length} skill${files.length === 1 ? '' : 's'} OK`);
}

main();
