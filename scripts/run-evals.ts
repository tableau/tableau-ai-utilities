/**
 * run-evals.ts — executes each skill's eval/cases.yml.
 *
 * This is a lightweight reference runner: it parses the declared cases and
 * checks the assertion shape. In a full implementation each case would prompt
 * an agent (with the skill injected) and assert on the response; here we verify
 * the eval files are well-formed so CI can gate on "has runnable evals".
 */
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import matter from 'gray-matter';
import yaml from 'js-yaml';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SKILL_ROOTS = ['tableau-studio-skills', 'tableau-mcp-skills'];

type EvalCase = {
  name: string;
  prompt: string;
  expect_contains?: string[];
  must_not_contain?: string[];
};

function walk(dir: string): string[] {
  const out: string[] = [];
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name === 'SKILL.md') out.push(full);
  }
  return out;
}

function main() {
  const roots = SKILL_ROOTS.filter((root) => fs.existsSync(path.join(ROOT, root)));
  if (roots.length === 0) {
    console.log('✓ no tableau-studio-skills/ or tableau-mcp-skills/ directory; nothing to eval');
    return;
  }
  const files = roots.flatMap((root) => walk(path.join(ROOT, root))).sort();
  let total = 0;
  let skills = 0;
  const errors: string[] = [];

  for (const file of files) {
    const folder = path.basename(path.dirname(file));
    const fm = matter(fs.readFileSync(file, 'utf8')).data as {name?: string};
    const id = fm.name ?? folder;
    const casesPath = path.join(path.dirname(file), 'eval', 'cases.yml');
    if (!fs.existsSync(casesPath)) {
      console.log(`↷ ${id}: no eval/ (skipped)`);
      continue;
    }
    const cases = yaml.load(fs.readFileSync(casesPath, 'utf8')) as EvalCase[];
    if (!Array.isArray(cases) || cases.length === 0) {
      errors.push(`${id}: eval/cases.yml has no cases`);
      continue;
    }
    skills += 1;
    for (const c of cases) {
      total += 1;
      if (!c.name || !c.prompt) {
        errors.push(`${id}: a case is missing "name" or "prompt"`);
      }
      if (!c.expect_contains && !c.must_not_contain) {
        errors.push(`${id}/${c.name}: case has no assertions`);
      }
    }
    console.log(`✓ ${id}: ${cases.length} case${cases.length === 1 ? '' : 's'}`);
  }

  if (errors.length) {
    console.error(`\n✗ run-evals failed:`);
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }
  if (skills === 0) {
    console.log('✓ no eval cases to run');
    return;
  }
  console.log(`\n✓ ${total} eval cases across ${skills} skills are well-formed`);
}

main();
