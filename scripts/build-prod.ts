/**
 * Production GitHub Pages build (tableau.github.io/tableau-ai-utilities).
 * Sets env in-process so this works on Windows cmd, PowerShell, and Unix shells.
 */
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {OFFICIAL_ORIGIN, PUBLIC_BASE_PATH} from '../site/src/extLinks/resolve';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../site');

const result = spawnSync('npm', ['run', 'build'], {
  cwd: SITE_DIR,
  env: {
    ...process.env,
    GITHUB_ORIGIN: OFFICIAL_ORIGIN,
    GITHUB_BASE_PATH: PUBLIC_BASE_PATH,
  },
  stdio: 'inherit',
  shell: process.platform === 'win32',
});
process.exit(result.status ?? 1);
