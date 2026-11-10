/**
 * Build the Docusaurus site for git.soma Pages and publish it to gh-pages.
 * Sets env in-process so this works on Windows cmd, PowerShell, and Unix shells.
 */
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {PREVIEW_BASE_SENTINEL, PREVIEW_REPO_HOST} from '../site/src/extLinks/resolve';
import {publishGhPages} from './publish-gh-pages';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../site');

function runNpm(args: string[], extraEnv: NodeJS.ProcessEnv) {
  const result = spawnSync('npm', args, {
    cwd: SITE_DIR,
    env: {...process.env, ...extraEnv},
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });
  if ((result.status ?? 1) !== 0) {
    process.exit(result.status ?? 1);
  }
}

runNpm(['run', 'build'], {
  DOCUSAURUS_GENERATED_FILES_DIR_NAME: '.docusaurus-preview',
  GITHUB_ORIGIN: PREVIEW_REPO_HOST,
  GITHUB_BASE_PATH: PREVIEW_BASE_SENTINEL,
});
publishGhPages('soma');
