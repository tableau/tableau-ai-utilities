import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {discoverSkills, exportSkills, packageSkill, rewriteMarkdown, validateSkillEntries} from './export-skills.ts';

function fixture(t: {after: (cleanup: () => void) => void}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'export-skills-test-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  const repo = path.join(root, 'repo');
  const output = path.join(root, 'output');
  fs.mkdirSync(repo);
  fs.mkdirSync(output);
  function skill(relative: string) {
    const folder = path.join(repo, relative);
    fs.mkdirSync(folder, {recursive: true});
    fs.writeFileSync(path.join(folder, 'SKILL.md'), '# Example\n');
    return folder;
  }
  return {root, repo, output, skill};
}

test('discovers all variants and excludes generated/dependency directories', t => {
  const {repo, output, skill} = fixture(t);
  const expected = [skill('claude/example'), skill('codex/example')].sort();
  for (const directory of ['node_modules', 'dist', '.hidden']) skill(`${directory}/ignored`);
  assert.deepEqual(discoverSkills(repo, output), expected);
});

test('separate variants have unique package names and missing README is generated', t => {
  const {repo, output, skill} = fixture(t);
  const records = ['claude/example', 'codex/example'].map(relative => packageSkill(skill(relative), repo, output));
  assert.equal(new Set(records.map(record => record.package)).size, 2);
  assert.ok(records.every(record => record.generated_readme));
});

test('rewrites paths in both directions without changing unrelated URLs', () => {
  const mapping = {'SKILL.md': 'SKILL.md', 'references/guide.md': 'skill-expertise/references__guide.md',
    'references/peer.md': 'skill-expertise/references__peer.md', 'scripts/run.py': 'skill-expertise/scripts__run.py'};
  assert.equal(rewriteMarkdown('[Guide](references/guide.md) `scripts/run.py` https://host/references/guide.md', 'SKILL.md', mapping),
    '[Guide](skill-expertise/references__guide.md) `skill-expertise/scripts__run.py` https://host/references/guide.md');
  assert.equal(rewriteMarkdown('[Home](../SKILL.md) [Peer](peer.md)', 'references/guide.md', mapping),
    '[Home](../SKILL.md) [Peer](references__peer.md)');
});

test('rejects resources that cannot be uploaded and flattening collisions', t => {
  const {repo, output, skill} = fixture(t);
  const folder = skill('example');
  const unsupported = path.join(folder, 'asset.json');
  fs.writeFileSync(unsupported, '{}');
  assert.throws(() => packageSkill(folder, repo, output), /Unsupported resource/);
  fs.unlinkSync(unsupported);
  fs.mkdirSync(path.join(folder, 'a'));
  fs.writeFileSync(path.join(folder, 'a/b.md'), '# Nested');
  fs.writeFileSync(path.join(folder, 'a__b.md'), '# Flat');
  assert.throws(() => packageSkill(folder, repo, output), /filename collision/);
});

test('records excluded agent UI metadata and preserves LICENSE as text', t => {
  const {repo, output, skill} = fixture(t);
  const folder = skill('example');
  fs.mkdirSync(path.join(folder, 'agents'));
  fs.writeFileSync(path.join(folder, 'agents/openai.yaml'), 'interface: {}');
  fs.writeFileSync(path.join(folder, 'LICENSE'), 'License text');
  const record = packageSkill(folder, repo, output);
  assert.deepEqual(record.excluded, ['agents/']);
  assert.equal(record.resources.LICENSE, 'skill-expertise/LICENSE.txt');
});

test('failed export preserves the previous generated export', t => {
  const {repo, output, skill} = fixture(t);
  const folder = skill('example');
  fs.writeFileSync(path.join(folder, 'unsupported.json'), '{}');
  const manifest = JSON.stringify({generator: 'export-repo-skills', skills: []});
  fs.writeFileSync(path.join(output, 'export-manifest.json'), manifest);
  assert.throws(() => exportSkills({repo, output, replace: true}), /Unsupported resource/);
  assert.equal(fs.readFileSync(path.join(output, 'export-manifest.json'), 'utf8'), manifest);
  assert.deepEqual(fs.readdirSync(path.dirname(output)).sort(), ['output', 'repo']);
});

test('exports and validates without access to any Gallery API checkout', t => {
  const {repo, output, skill} = fixture(t);
  skill('example');
  fs.rmdirSync(output);
  const records = exportSkills({repo, output, replace: false});
  assert.equal(records.length, 1);
  const manifest = JSON.parse(fs.readFileSync(path.join(output, 'export-manifest.json'), 'utf8'));
  assert.deepEqual(manifest.validation, {validated: 1});
  assert.equal(manifest.validator, 'pre-zip-tskill-structure-v1');
  assert.equal(manifest.validator_sha256, undefined);
});

test('pre-ZIP validator accepts required documents and optional flat expertise files', () => {
  for (const extras of [[], ['skill-expertise/a.md', 'skill-expertise/b.PY', 'skill-expertise/c.txt']]) {
    const entries = ['SKILL.md', 'README.md', ...extras].map(name => ({name, data: Buffer.from('# Example')}));
    assert.doesNotThrow(() => validateSkillEntries('example.TSKILL', entries));
  }
});

for (const names of [
  ['README.md'], ['SKILL.md'], ['skill.md', 'readme.md'], ['SKILL.md/', 'README.md'],
  ['SKILL.md', 'README.md', 'extra.md'], ['SKILL.md', 'README.md', 'other/'],
  ['SKILL.md', 'README.md', 'skill-expertise'],
  ['SKILL.md', 'README.md', 'skill-expertise/nested/'],
  ['SKILL.md', 'README.md', 'skill-expertise/nested/a.md'],
  ['SKILL.md', 'README.md', 'skill-expertise/a.json'],
  ['SKILL.md', 'README.md', 'skill-expertise/a.md.exe'],
  ['SKILL.md', 'README.md', 'skill-expertise/../a.md'],
]) {
  test(`pre-ZIP validator rejects invalid layout: ${names.join(', ')}`, () => {
    const entries = names.map(name => ({name, data: Buffer.from('# Example')}));
    assert.throws(() => validateSkillEntries('example.tskill', entries), /root level|root|flat/);
  });
}

test('pre-ZIP validator rejects wrong extensions and duplicate filenames', () => {
  const entries = ['SKILL.md', 'README.md'].map(name => ({name, data: Buffer.from('# Example')}));
  assert.throws(() => validateSkillEntries('example.zip', entries), /require a .tskill/);
  assert.throws(() => validateSkillEntries('example.tskill', [...entries, entries[0]]), /duplicate/);
});
