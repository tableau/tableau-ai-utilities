#!/usr/bin/env node
/**
 * Run a repo .ts script with site/node_modules on NODE_PATH.
 * npm scripts in site/ cannot use Unix `NODE_PATH=...` prefixes on Windows cmd.
 */
'use strict';

const path = require('path');
const fs = require('fs');
const {spawnSync} = require('child_process');

const siteDir = path.resolve(__dirname, '../site');
const sep = process.platform === 'win32' ? ';' : ':';
const siteModules = path.join(siteDir, 'node_modules');
const env = {
  ...process.env,
  NODE_PATH: process.env.NODE_PATH ? `${siteModules}${sep}${process.env.NODE_PATH}` : siteModules,
};

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('usage: node scripts/run-tsx.cjs <script.ts> [args...]');
  process.exit(1);
}

const tsxBin = path.join(siteDir, 'node_modules', '.bin', process.platform === 'win32' ? 'tsx.cmd' : 'tsx');
if (!fs.existsSync(tsxBin)) {
  console.error('Cannot run TypeScript: site dependencies are not installed.');
  console.error('From the repository root, run: npm --prefix site ci');
  process.exit(1);
}
const result = spawnSync(tsxBin, args, {
  cwd: process.cwd(),
  env,
  stdio: 'inherit',
  shell: process.platform === 'win32',
});
if (result.error) console.error(`Failed to start tsx: ${result.error.message}`);
if (result.signal) console.error(`tsx was terminated by ${result.signal}`);
process.exit(result.status === null ? 1 : result.status);
