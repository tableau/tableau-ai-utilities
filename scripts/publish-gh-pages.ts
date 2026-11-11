/**
 * Publish site/build to the gh-pages branch of tableau/tableau-ai-utilities.
 *
 * GitHub Pages serves gh-pages directly. CODEOWNERS must carry the Open Source
 * header, which is copied into the Pages tree.
 */
import {spawnSync, type SpawnSyncReturns} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BUILD = path.join(ROOT, 'site', 'build');
const PUBLIC_REPO = 'tableau/tableau-ai-utilities';

const PUBLIC_ECCN = '#ECCN:Open Source';
const PUBLIC_GUS = '#GUSINFO:Open Source,Open Source Workflow';

/** gh-pages on github.com must carry the public header. */
export function assertPublicCodeowners(body: string): void {
  if (!body.includes(PUBLIC_ECCN) || !body.includes(PUBLIC_GUS)) {
    throw new Error(
      'CODEOWNERS must contain the public GitHub header (#ECCN:Open Source, #GUSINFO:Open Source,Open Source Workflow) before publishing gh-pages to github.com.',
    );
  }
}

function git(args: string[], cwd: string): SpawnSyncReturns<string> {
  return spawnSync('git', args, {cwd, encoding: 'utf8'});
}

function gitOrThrow(args: string[], cwd: string): string {
  const result = git(args, cwd);
  if (result.status !== 0) {
    throw new Error(`git ${args.join(' ')} failed: ${result.stderr || result.stdout}`);
  }
  return result.stdout ?? '';
}

function githubRemote(): string {
  const repo = process.env.GITHUB_REPOSITORY;
  if (repo && repo !== PUBLIC_REPO) {
    throw new Error(`Refusing to publish gh-pages for ${repo}. The public site is ${PUBLIC_REPO}.`);
  }
  const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN || process.env.PUBLIC_GITHUB_TOKEN;
  if (!token) return `git@github.com:${PUBLIC_REPO}.git`;
  return `https://x-access-token:${token}@github.com/${PUBLIC_REPO}.git`;
}

export function publishGhPages(): void {
  const index = path.join(BUILD, 'index.html');
  if (!fs.existsSync(index)) {
    throw new Error(`Missing ${index} — run npm run build first.`);
  }

  const sha = gitOrThrow(['rev-parse', '--short', 'HEAD'], ROOT).trim();
  const codeownersPath = path.join(ROOT, 'CODEOWNERS');
  if (!fs.existsSync(codeownersPath)) {
    throw new Error('Missing CODEOWNERS — gh-pages must carry the compliance header for its remote.');
  }
  const codeowners = fs.readFileSync(codeownersPath, 'utf8');
  assertPublicCodeowners(codeowners);
  fs.writeFileSync(path.join(BUILD, '.nojekyll'), '');
  fs.writeFileSync(path.join(BUILD, 'CODEOWNERS'), codeowners);

  const gitDir = path.join(BUILD, '.git');
  if (fs.existsSync(gitDir)) fs.rmSync(gitDir, {recursive: true, force: true});

  gitOrThrow(['init', '-q'], BUILD);
  gitOrThrow(['checkout', '-q', '-b', 'gh-pages'], BUILD);
  gitOrThrow(['add', '-A'], BUILD);

  const authorEnv = {
    ...process.env,
    GIT_AUTHOR_NAME: process.env.GIT_AUTHOR_NAME || 'github-actions[bot]',
    GIT_AUTHOR_EMAIL: process.env.GIT_AUTHOR_EMAIL || 'github-actions[bot]@users.noreply.github.com',
    GIT_COMMITTER_NAME: process.env.GIT_COMMITTER_NAME || 'github-actions[bot]',
    GIT_COMMITTER_EMAIL: process.env.GIT_COMMITTER_EMAIL || 'github-actions[bot]@users.noreply.github.com',
  };
  const commit = spawnSync('git', ['commit', '-qm', `Deploy public site for ${sha}`], {
    cwd: BUILD,
    encoding: 'utf8',
    env: authorEnv,
  });
  if (commit.status !== 0) {
    throw new Error(`git commit failed: ${commit.stderr || commit.stdout}`);
  }

  const remote = githubRemote();
  const push = spawnSync('git', ['push', '-f', remote, 'gh-pages:gh-pages'], {
    cwd: BUILD,
    encoding: 'utf8',
    stdio: 'inherit',
  });
  if (push.status !== 0) {
    throw new Error('git push to gh-pages failed');
  }
  console.log(
    `Published ${sha} to gh-pages (${remote.replace(/x-access-token:[^@]+@/, 'x-access-token:***@')})`,
  );
}

function isMain(): boolean {
  const entry = process.argv[1];
  if (!entry) return false;
  return pathToFileURL(path.resolve(entry)).href === import.meta.url;
}

if (isMain()) {
  try {
    publishGhPages();
  } catch (err) {
    console.error(err instanceof Error ? err.message : err);
    process.exit(1);
  }
}
