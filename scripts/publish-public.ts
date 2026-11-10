/**
 * Overlay git.soma main onto tableau/tableau-ai-utilities and open or update
 * the from-soma-main pull request. Does not merge, and does not push the
 * public main or gh-pages branches. Merging the pull request publishes gh-pages.
 *
 * Token: PUBLIC_GITHUB_TOKEN, or `gh auth token --hostname github.com`.
 * A token api.github.com rejects is refused.
 */
import {spawnSync, type SpawnSyncReturns} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PUBLIC_REPO = 'tableau/tableau-ai-utilities';
const PUBLIC_BRANCH = 'from-soma-main';
const SOURCE_URL = 'https://git.soma.salesforce.com/cx-labs/studio-skills';
const PRESERVE = [
  'CODEOWNERS',
  'LICENSE.txt',
  'CODE_OF_CONDUCT.md',
  'SECURITY.md',
  'how_to_license.md',
  '.github/CODEOWNERS',
];

type GitResult = SpawnSyncReturns<string>;

function git(args: string[], cwd: string, env?: NodeJS.ProcessEnv): GitResult {
  return spawnSync('git', args, {
    cwd,
    encoding: 'utf8',
    env: {...process.env, GIT_TERMINAL_PROMPT: '0', ...env},
  });
}

function gitOrThrow(args: string[], cwd: string, env?: NodeJS.ProcessEnv): string {
  const result = git(args, cwd, env);
  if (result.status !== 0) {
    throw new Error(`git ${args.join(' ')} failed: ${result.stderr || result.stdout}`);
  }
  return result.stdout ?? '';
}

function redact(text: string, token: string): string {
  return text.split(token).join('***');
}

function authArgs(token: string): string[] {
  const basic = Buffer.from(`x-access-token:${token}`).toString('base64');
  return ['-c', `http.extraheader=AUTHORIZATION: basic ${basic}`];
}

function gitAuth(args: string[], cwd: string, token: string): GitResult {
  const result = git([...authArgs(token), ...args], cwd);
  const basic = Buffer.from(`x-access-token:${token}`).toString('base64');
  const scrub = (text: string) => redact(redact(text, token), basic);
  if (result.stderr) result.stderr = scrub(result.stderr);
  if (result.stdout) result.stdout = scrub(result.stdout);
  return result;
}

function gitAuthOrThrow(args: string[], cwd: string, token: string): string {
  const result = gitAuth(args, cwd, token);
  if (result.status !== 0) {
    throw new Error(`git ${args.join(' ')} failed: ${result.stderr || result.stdout}`);
  }
  return result.stdout ?? '';
}

function resolveGithubToken(): string {
  const fromEnv = process.env.PUBLIC_GITHUB_TOKEN?.trim();
  if (fromEnv) return fromEnv;
  const gh = spawnSync('gh', ['auth', 'token', '--hostname', 'github.com'], {encoding: 'utf8'});
  const token = gh.stdout?.trim();
  if (gh.status === 0 && token) return token;
  throw new Error(
    'Set PUBLIC_GITHUB_TOKEN, or log in with: gh auth login --hostname github.com',
  );
}

async function github(
  token: string,
  method: string,
  apiPath: string,
  body?: unknown,
): Promise<{status: number; json: unknown}> {
  const response = await fetch(`https://api.github.com${apiPath}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'studio-skills-publish',
      ...(body === undefined ? {} : {'Content-Type': 'application/json'}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  let json: unknown = null;
  if (text) {
    try {
      json = JSON.parse(text);
    } catch {
      json = text;
    }
  }
  return {status: response.status, json};
}

async function assertGithubToken(token: string): Promise<void> {
  const user = await github(token, 'GET', '/user');
  if (user.status !== 200) {
    throw new Error(
      `api.github.com rejected the token (${user.status}). Use a github.com token with contents and pull-request write on ${PUBLIC_REPO}.`,
    );
  }
  const repo = await github(token, 'GET', `/repos/${PUBLIC_REPO}`);
  if (repo.status !== 200) {
    throw new Error(`api.github.com cannot read ${PUBLIC_REPO} (${repo.status}).`);
  }
}

function assertSomaOrigin(): void {
  const origin = gitOrThrow(['remote', 'get-url', 'origin'], ROOT).trim();
  if (!origin.includes('git.soma.salesforce.com')) {
    throw new Error(`publish:public must run from the git.soma checkout. origin is ${origin}`);
  }
}

function gitShow(rev: string, file: string, cwd: string): Buffer | null {
  const result = spawnSync('git', ['show', `${rev}:${file}`], {cwd});
  if (result.status !== 0) return null;
  return result.stdout as Buffer;
}

function clearWorktree(dir: string): void {
  for (const name of fs.readdirSync(dir)) {
    if (name === '.git') continue;
    fs.rmSync(path.join(dir, name), {recursive: true, force: true});
  }
}

function archiveInto(sha: string, dest: string, tarPath: string): void {
  const archive = git(['archive', '--format=tar', '-o', tarPath, sha], ROOT);
  if (archive.status !== 0) {
    throw new Error(`git archive failed: ${archive.stderr || archive.stdout}`);
  }
  const extract = spawnSync('tar', ['-xf', tarPath], {cwd: dest, encoding: 'utf8'});
  if (extract.status !== 0) {
    throw new Error(`tar extract failed: ${extract.stderr || extract.stdout}`);
  }
}

type Pull = {number: number; html_url?: string};

async function findOpenPull(token: string): Promise<Pull | null> {
  const listed = await github(
    token,
    'GET',
    `/repos/${PUBLIC_REPO}/pulls?head=tableau:${PUBLIC_BRANCH}&base=main&state=open`,
  );
  if (listed.status !== 200 || !Array.isArray(listed.json)) {
    throw new Error(`Could not list pull requests (${listed.status}).`);
  }
  const [first] = listed.json as Pull[];
  return first ?? null;
}

async function ensurePull(token: string, sha: string, short: string): Promise<string> {
  const title = `Publish studio-skills ${short}`;
  const body = [
    `Source overlay of git.soma cx-labs/studio-skills \`${sha}\`.`,
    '',
    'Public `CODEOWNERS` and the OSPO template files (`LICENSE.txt`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `how_to_license.md`) are unchanged. `.github/CODEOWNERS` is omitted so GitHub keeps using the root header.',
    '',
    'Merging this pull request publishes https://tableau.github.io/tableau-ai-utilities/ from `gh-pages`.',
    '',
    `Source: ${SOURCE_URL}/commit/${sha}`,
  ].join('\n');
  const existing = await findOpenPull(token);
  if (existing) {
    const updated = await github(token, 'PATCH', `/repos/${PUBLIC_REPO}/pulls/${existing.number}`, {
      title,
      body,
    });
    if (updated.status !== 200) {
      throw new Error(`Could not update pull request #${existing.number} (${updated.status}).`);
    }
    const url = (updated.json as Pull).html_url ?? existing.html_url ?? '';
    console.log(`Updated ${url}`);
    return url;
  }
  const created = await github(token, 'POST', `/repos/${PUBLIC_REPO}/pulls`, {
    title,
    head: PUBLIC_BRANCH,
    base: 'main',
    body,
  });
  if (created.status !== 201) {
    const message =
      created.json && typeof created.json === 'object' && 'message' in created.json
        ? String((created.json as {message: unknown}).message)
        : '';
    throw new Error(`Could not open the pull request (${created.status}) ${message}`.trim());
  }
  const url = (created.json as Pull).html_url ?? '';
  console.log(`Opened ${url}`);
  return url;
}

async function publishPublic(): Promise<void> {
  assertSomaOrigin();
  const token = resolveGithubToken();
  await assertGithubToken(token);

  gitOrThrow(['fetch', 'origin', 'main'], ROOT);
  const sha = gitOrThrow(['rev-parse', 'origin/main'], ROOT).trim();
  const short = gitOrThrow(['rev-parse', '--short', 'origin/main'], ROOT).trim();
  const authorName = gitOrThrow(['log', '-1', '--format=%an', sha], ROOT).trim() || 'github-actions[bot]';
  const authorEmail =
    gitOrThrow(['log', '-1', '--format=%ae', sha], ROOT).trim() ||
    'github-actions[bot]@users.noreply.github.com';

  const parent = fs.mkdtempSync(path.join(os.tmpdir(), 'publish-public-'));
  const clone = path.join(parent, 'repo');
  const tarPath = path.join(parent, 'tree.tar');
  try {
    console.log(`Publishing ${short} to ${PUBLIC_REPO} (${PUBLIC_BRANCH})`);
    const cloned = gitAuth(
      ['clone', '--depth', '1', '--branch', 'main', `https://github.com/${PUBLIC_REPO}.git`, clone],
      parent,
      token,
    );
    if (cloned.status !== 0) {
      throw new Error(`git clone failed: ${cloned.stderr || cloned.stdout}`);
    }
    const fetched = gitAuth(
      [
        'fetch',
        '--depth',
        '1',
        'origin',
        `refs/heads/${PUBLIC_BRANCH}:refs/remotes/origin/${PUBLIC_BRANCH}`,
      ],
      clone,
      token,
    );
    const hasBranch = fetched.status === 0;

    gitAuthOrThrow(['checkout', '-B', PUBLIC_BRANCH, 'origin/main'], clone, token);
    const preserved = new Map<string, Buffer | null>();
    for (const file of PRESERVE) preserved.set(file, gitShow('origin/main', file, clone));

    clearWorktree(clone);
    archiveInto(sha, clone, tarPath);
    for (const [file, body] of preserved) {
      const dest = path.join(clone, file);
      if (body) {
        fs.mkdirSync(path.dirname(dest), {recursive: true});
        fs.writeFileSync(dest, body);
      } else if (fs.existsSync(dest)) {
        fs.rmSync(dest);
      }
    }

    gitOrThrow(['add', '-A'], clone);
    const newTree = gitOrThrow(['write-tree'], clone).trim();
    const baseTree = gitOrThrow(['rev-parse', 'HEAD^{tree}'], clone).trim();
    const publishedTree = hasBranch
      ? gitOrThrow(['rev-parse', `origin/${PUBLIC_BRANCH}^{tree}`], clone).trim()
      : null;
    if (publishedTree === newTree || (!hasBranch && baseTree === newTree)) {
      console.log(`Public branch already has ${short}.`);
      if (hasBranch) await ensurePull(token, sha, short);
      return;
    }

    const commit = git(
      [
        '-c',
        `user.name=${authorName}`,
        '-c',
        `user.email=${authorEmail}`,
        'commit',
        '-m',
        `Publish studio-skills ${short} from git.soma main.\n\nSource: ${SOURCE_URL}/commit/${sha}`,
      ],
      clone,
    );
    if (commit.status !== 0) {
      throw new Error(`git commit failed: ${commit.stderr || commit.stdout}`);
    }

    const pushArgs = hasBranch
      ? [
          'push',
          `--force-with-lease=refs/heads/${PUBLIC_BRANCH}:refs/remotes/origin/${PUBLIC_BRANCH}`,
          'origin',
          `HEAD:${PUBLIC_BRANCH}`,
        ]
      : ['push', '-u', 'origin', `HEAD:${PUBLIC_BRANCH}`];
    const pushed = gitAuth(pushArgs, clone, token);
    if (pushed.status !== 0) {
      throw new Error(`git push failed: ${pushed.stderr || pushed.stdout}`);
    }
    await ensurePull(token, sha, short);
  } finally {
    fs.rmSync(parent, {recursive: true, force: true});
  }
}

function isMain(): boolean {
  const entry = process.argv[1];
  if (!entry) return false;
  return pathToFileURL(path.resolve(entry)).href === import.meta.url;
}

if (isMain()) {
  publishPublic().catch((err: unknown) => {
    console.error(err instanceof Error ? err.message : err);
    process.exit(1);
  });
}
