/**
 * Production GitHub Pages build (tableau.github.io/tableau-ai-utilities).
 * Sets env in-process so this works on Windows cmd, PowerShell, and Unix shells.
 * An explicit GITHUB_BASE_PATH is kept. The private GitHub Pages host needs `/`.
 */
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {OFFICIAL_ORIGIN, PUBLIC_BASE_PATH} from '../site/src/extLinks/resolve';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../site');
const requestedBase = process.env.GITHUB_BASE_PATH?.trim();

const result = spawnSync('npm', ['run', 'build'], {
  cwd: SITE_DIR,
  env: {
    ...process.env,
    GITHUB_ORIGIN: OFFICIAL_ORIGIN,
    GITHUB_BASE_PATH: requestedBase || PUBLIC_BASE_PATH,
  },
  stdio: 'inherit',
  shell: process.platform === 'win32',
});
process.exit(result.status ?? 1);
