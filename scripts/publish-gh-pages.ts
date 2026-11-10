/**
 * Publish site/build to the gh-pages branch.
 *
 * git.soma Pages and the public GitHub Pages site both serve gh-pages directly.
 * The soma target requires the EAR99 header and pushes to git.soma.
 * The github target requires the Open Source header and pushes to github.com.
 */
import {spawnSync, type SpawnSyncReturns} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BUILD = path.join(ROOT, 'site', 'build');
const HOOKS = path.join(ROOT, 'scripts', 'githooks').replace(/\\/g, '/');
const PUBLIC_REPO = 'tableau/tableau-ai-utilities';

const SOMA_ECCN = '#ECCN:EAR99';
const SOMA_GUS = '#GUSINFO:Tableau CX,Tableau CX';
const PUBLIC_ECCN = '#ECCN:Open Source';
const PUBLIC_GUS = '#GUSINFO:Open Source,Open Source Workflow';

export type PagesTarget = 'soma' | 'github';

/** gh-pages on git.soma must carry the EAR99 header and must not carry the public one. */
export function assertSomaCodeowners(body: string): void {
  const missingSoma = !body.includes(SOMA_ECCN) || !body.includes(SOMA_GUS);
  const carriesPublic = body.includes(PUBLIC_ECCN) || body.includes(PUBLIC_GUS);
  if (missingSoma || carriesPublic) {
    throw new Error(
      'CODEOWNERS must contain the git.soma header (#ECCN:EAR99, #GUSINFO:Tableau CX,Tableau CX) before publishing gh-pages to git.soma.',
    );
  }
}

/** gh-pages on github.com must carry the public header and must not carry the git.soma one. */
export function assertPublicCodeowners(body: string): void {
  const missingPublic = !body.includes(PUBLIC_ECCN) || !body.includes(PUBLIC_GUS);
  const carriesSoma = body.includes(SOMA_ECCN) || body.includes(SOMA_GUS);
  if (missingPublic || carriesSoma) {
    throw new Error(
      'CODEOWNERS must contain the public GitHub header (#ECCN:Open Source, #GUSINFO:Open Source,Open Source Workflow) before publishing gh-pages to github.com.',
    );
  }
}

export function pagesTargetFromEnv(env: NodeJS.ProcessEnv = process.env): PagesTarget {
  const explicit = env.PUBLISH_PAGES_TARGET;
  if (explicit === 'github' || explicit === 'soma') return explicit;
  if (explicit) {
    throw new Error(`PUBLISH_PAGES_TARGET must be "github" or "soma", got ${explicit}`);
  }
  const server = env.GITHUB_SERVER_URL;
  if (!server) return 'soma';
  try {
    const host = new URL(server).host.toLowerCase();
    if (host === 'github.com' || host.endsWith('.github.com')) return 'github';
  } catch {
    // Unparseable server URL keeps the git.soma preview default.
  }
  return 'soma';
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

function somaRemote(): string {
  const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
  const repo = process.env.GITHUB_REPOSITORY;
  if (token && repo) {
    const server = (process.env.GITHUB_SERVER_URL || 'https://git.soma.salesforce.com').replace(/\/$/, '');
    const host = new URL(server).host;
    if (!host.includes('git.soma.salesforce.com')) {
      throw new Error(`Refusing to publish the git.soma preview to ${host}.`);
    }
    return `https://x-access-token:${token}@${host}/${repo}.git`;
  }
  return gitOrThrow(['remote', 'get-url', 'origin'], ROOT).trim();
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

function pushRemote(target: PagesTarget): string {
  return target === 'github' ? githubRemote() : somaRemote();
}

export function publishGhPages(target: PagesTarget = 'soma'): void {
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
  if (target === 'github') assertPublicCodeowners(codeowners);
  else assertSomaCodeowners(codeowners);
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
  const subject = target === 'github' ? `Deploy public site for ${sha}` : `Deploy site preview for ${sha}`;
  const commit = spawnSync('git', ['commit', '-qm', subject], {
    cwd: BUILD,
    encoding: 'utf8',
    env: authorEnv,
  });
  if (commit.status !== 0) {
    throw new Error(`git commit failed: ${commit.stderr || commit.stdout}`);
  }

  const remote = pushRemote(target);
  const push = spawnSync(
    'git',
    ['-c', `core.hooksPath=${HOOKS}`, 'push', '-f', remote, 'gh-pages:gh-pages'],
    {
      cwd: BUILD,
      encoding: 'utf8',
      stdio: 'inherit',
    },
  );
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
    publishGhPages(pagesTargetFromEnv());
  } catch (err) {
    console.error(err instanceof Error ? err.message : err);
    process.exit(1);
  }
}
