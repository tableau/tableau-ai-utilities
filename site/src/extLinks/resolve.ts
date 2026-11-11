/**
 * Environment-aware external-docs links.
 *
 * Registry (`../data/ext.json`) stores baseURLs only. Callers pass an optional
 * page path. Hosts change with build env / viewer hostname; paths do not live
 * in the registry.
 */

import extJson from '../data/ext.json' with {type: 'json'};
import {VARIABLES} from '../remark/variables.mjs';

export const OFFICIAL_ORIGIN = 'https://tableau.github.io';
export const OFFICIAL_REPO_URL = 'https://github.com/tableau/tableau-ai-utilities';
/** Public GitHub Pages base path. Also the default when GITHUB_BASE_PATH is unset. */
export const PUBLIC_BASE_PATH = '/tableau-ai-utilities';
export const EXT_COMING_RELEASE = VARIABLES.coming_release;

export const EXT_SITES = ['studio', 'eca', 'mcp', 'extensions', 'packages'] as const;
export type ExtSite = (typeof EXT_SITES)[number];
export type ExtLinkEnv = 'prod' | 'stage';
export type ViewerEnv = ExtLinkEnv | 'unknown';

type SiteBases = {stage?: string; prod?: string};

const registry = extJson as Record<string, SiteBases>;

const PROD_HOSTS = new Set(['help.tableau.com', 'tableau.github.io']);

/** Pre-GA Help is served at /v0.0/ on the public host; that path is still stage. */
function isHelpV0Stage(hostname: string, pathname: string): boolean {
  if (hostname !== 'help.tableau.com') {
    return false;
  }
  const path = pathname.toLowerCase();
  return path === '/v0.0' || path.startsWith('/v0.0/');
}

const EXT_PROTOCOL = /^ext:\/\/([^/]+)(?:\/(.*))?$/;

export function isExtSite(value: string): value is ExtSite {
  return (EXT_SITES as readonly string[]).includes(value);
}

export function getSiteEntry(site: string): SiteBases {
  const entry = registry[site];
  if (!entry) {
    throw new Error(`Unknown ext site "${site}". Valid sites: ${EXT_SITES.join(', ')}`);
  }
  return entry;
}

/**
 * Unset / any non-official GITHUB_ORIGIN → stage outbound bases.
 * Only an explicit official origin selects prod (local defaults to stage).
 */
export function outboundEnvFromGithubOrigin(githubOrigin: string | undefined): ExtLinkEnv {
  return githubOrigin === OFFICIAL_ORIGIN ? 'prod' : 'stage';
}

/** Strip a trailing slash. The site root stays `/`. */
function stripTrailingSlash(path: string): string {
  if (path === '/') return '/';
  return path.replace(/\/$/, '');
}

/**
 * Base path for this build.
 * Unset or empty defaults to the public GitHub Pages path.
 */
export function siteBasePathFromEnv(githubBasePath: string | undefined): string {
  if (githubBasePath === undefined || githubBasePath === '') return PUBLIC_BASE_PATH;
  const withSlash = githubBasePath.startsWith('/') ? githubBasePath : `/${githubBasePath}`;
  return stripTrailingSlash(withSlash);
}

/** Docusaurus baseUrl, always with one trailing slash. */
export function siteBaseUrlFromEnv(githubBasePath: string | undefined): string {
  const basePath = siteBasePathFromEnv(githubBasePath);
  return basePath === '/' ? '/' : `${basePath}/`;
}

export function siteOriginFromEnv(githubOrigin: string | undefined): string {
  return (githubOrigin ?? OFFICIAL_ORIGIN).replace(/\/$/, '');
}

/** Absolute site root with no trailing slash, e.g. https://tableau.github.io/tableau-ai-utilities. */
export function siteRootFromEnv(githubOrigin: string | undefined, githubBasePath: string | undefined): string {
  const basePath = siteBasePathFromEnv(githubBasePath);
  return `${siteOriginFromEnv(githubOrigin)}${basePath === '/' ? '' : basePath}`;
}

/**
 * The committed llms/ directory is the public corpus. Only a build aimed at
 * https://tableau.github.io/tableau-ai-utilities may rewrite it.
 */
export function isPublicCorpusBuild(githubOrigin: string | undefined, githubBasePath: string | undefined): boolean {
  return (
    siteOriginFromEnv(githubOrigin) === OFFICIAL_ORIGIN &&
    siteBasePathFromEnv(githubBasePath) === PUBLIC_BASE_PATH
  );
}

export function classifyHostname(hostname: string, pathname = ''): ViewerEnv {
  const host = hostname.toLowerCase();
  if (isHelpV0Stage(host, pathname)) {
    return 'stage';
  }
  if (PROD_HOSTS.has(host)) return 'prod';
  if (host === 'localhost' || host === '127.0.0.1') return 'stage';
  return 'unknown';
}

export function joinBasePath(base: string, path = ''): string {
  if (!path) return base;
  if (path.startsWith('//') || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(path)) {
    throw new Error(`ext link path must be relative, got: ${path}`);
  }
  const trimmed = path.replace(/^\/+/, '');
  if (!trimmed) return base;
  const normalizedBase = base.endsWith('/') ? base : `${base}/`;
  return new URL(trimmed, normalizedBase).href;
}

export function parseExtProtocol(url: string): {site: ExtSite; path: string} | null {
  const match = EXT_PROTOCOL.exec(url);
  if (!match) return null;
  const site = match[1];
  const path = (match[2] ?? '').replace(/^\/+/, '');
  if (!isExtSite(site)) {
    throw new Error(`Unknown ext:// site "${site}". Valid sites: ${EXT_SITES.join(', ')}`);
  }
  return {site, path};
}

export type ExtLinkModel = {
  site: ExtSite;
  href: string;
  prodHref: string | undefined;
  stageHref: string | undefined;
  emitStageHref: boolean;
  coming: boolean;
  comingRelease: string;
};

export function buildExtLinkModel(
  site: string,
  path: string,
  bakedEnv: ExtLinkEnv,
): ExtLinkModel {
  if (!isExtSite(site)) {
    throw new Error(`Unknown ext site "${site}". Valid sites: ${EXT_SITES.join(', ')}`);
  }
  const entry = getSiteEntry(site);
  const prodHref = entry.prod ? joinBasePath(entry.prod, path) : undefined;
  const stageHref = entry.stage ? joinBasePath(entry.stage, path) : undefined;
  const selected = bakedEnv === 'prod' ? prodHref : stageHref;
  return {
    site,
    href: selected ?? '#',
    prodHref,
    stageHref,
    emitStageHref: bakedEnv !== 'prod' && Boolean(stageHref),
    coming: !selected,
    comingRelease: EXT_COMING_RELEASE,
  };
}

export function extLinkDataAttributes(model: ExtLinkModel): Record<string, string> {
  const attrs: Record<string, string> = {
    'data-ext-link': model.site,
  };
  if (model.prodHref) attrs['data-prod-href'] = model.prodHref;
  if (model.emitStageHref && model.stageHref) {
    attrs['data-stage-href'] = model.stageHref;
  }
  if (!model.stageHref) attrs['data-coming'] = model.comingRelease;
  return attrs;
}

export function hrefForViewer(
  model: ExtLinkModel,
  viewer: ViewerEnv,
): {href: string; coming: boolean} {
  if (viewer === 'prod') {
    return {href: model.prodHref ?? '#', coming: !model.prodHref};
  }
  if (viewer === 'stage') {
    return model.stageHref ? {href: model.stageHref, coming: false} : {href: '#', coming: true};
  }
  return {href: model.href, coming: model.coming};
}
