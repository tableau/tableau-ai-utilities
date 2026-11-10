import React, {useEffect, useMemo, useState} from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Fuse from 'fuse.js';
import catalogData from '@site/static/catalog.json';
import pluginData from '@site/static/plugins.json';
import DownloadIcon from '@site/src/components/DownloadIcon';
import styles from './styles.module.css';

type Protection = 'protected' | 'overridable';

type CatalogSkill = {
  id: string;
  name?: string;
  title: string;
  description: string;
  category?: string;
  categoryLabel?: string;
  protection?: Protection;
  keywords: string[];
  permalink: string;
  download?: string;
};

type Plugin = {
  name: string;
  version: string;
  description: string;
  category: string;
  keywords: string[];
  permalink: string;
};

type Kind = 'skill' | 'plugin';

type Item = {
  kind: Kind;
  key: string;
  name?: string;
  title: string;
  description: string;
  category?: string;
  categoryLabel?: string;
  platform?: string;
  protection?: Protection;
  keywords: string[];
  permalink: string;
};

/** Top-level skill trees shown as Platform filters. Order is the checkbox order. */
const PLATFORMS = [
  {slug: 'tableau-studio-skills', label: 'Tableau Studio'},
  {slug: 'tableau-mcp-skills', label: 'Tableau MCP'},
] as const;

type PlatformSlug = (typeof PLATFORMS)[number]['slug'];

function platformOf(id: string): PlatformSlug | undefined {
  return PLATFORMS.find((platform) => id.startsWith(`${platform.slug}/`))?.slug;
}

function platformLabel(slug: string | undefined): string | undefined {
  return PLATFORMS.find((platform) => platform.slug === slug)?.label;
}

const catalog = (catalogData as CatalogSkill[]) ?? [];
const plugins = (pluginData as Plugin[]) ?? [];

const skillItems: Item[] = catalog.map((s) => ({
  kind: 'skill',
  key: `skill:${s.id}`,
  name: s.name ?? s.id,
  title: s.title,
  description: s.description,
  category: s.category,
  categoryLabel: s.categoryLabel,
  platform: platformOf(s.id),
  protection: s.protection,
  keywords: s.keywords ?? [],
  permalink: s.permalink,
}));

const pluginItems: Item[] = plugins.map((p) => ({
  kind: 'plugin',
  key: `plugin:${p.name}`,
  title: p.name,
  description: p.description,
  keywords: p.keywords ?? [],
  permalink: p.permalink,
}));

const fuseOptions = {
  keys: [
    {name: 'title', weight: 3},
    {name: 'keywords', weight: 1.5},
    {name: 'categoryLabel', weight: 1.2},
    {name: 'description', weight: 1},
    {name: 'protection', weight: 0.5},
  ],
  threshold: 0.35,
  ignoreLocation: true,
};

function uniqueSorted(values: string[]): string[] {
  return [...new Set(values)].sort();
}

function uniqueInOrder(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const v of values) {
    if (v && !seen.has(v)) {
      seen.add(v);
      out.push(v);
    }
  }
  return out;
}

function groupByCategory(rows: Item[]): {slug: string; label: string; platformLabel?: string; items: Item[]}[] {
  const groups = new Map<string, Item[]>();
  const labels = new Map<string, string>();
  const platforms = new Map<string, string | undefined>();
  const order: string[] = [];
  for (const row of rows) {
    const category = row.category ?? '';
    const key = `${row.platform ?? ''}:${category}`;
    if (!groups.has(key)) {
      groups.set(key, []);
      labels.set(key, row.categoryLabel ?? category);
      platforms.set(key, platformLabel(row.platform));
      order.push(key);
    }
    groups.get(key)!.push(row);
  }
  return order.map((key) => ({
    slug: key,
    label: labels.get(key) ?? key,
    platformLabel: platforms.get(key),
    items: groups.get(key) ?? [],
  }));
}

function toggle<T>(list: T[], value: T): T[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
}

/** First sentence of a SKILL.md description, for the filter-page blurb. */
function firstSentence(text: string): string {
  const t = text.trim();
  if (!t) return t;
  for (let i = 0; i < t.length; i++) {
    const ch = t[i];
    if (ch !== '.' && ch !== '!' && ch !== '?') continue;
    const prev = t[i - 1];
    const next = t[i + 1];
    if (ch === '.' && prev && /\d/.test(prev) && next && /\d/.test(next)) continue;
    if (ch === '.' && prev && /[A-Za-z]/.test(prev) && next && /[A-Za-z]/.test(next)) continue;
    const rest = t.slice(i + 1);
    if (rest === '' || /^\s*$/.test(rest) || /^\s+[A-Z]/.test(rest) || /^\s+"/.test(rest)) {
      return t.slice(0, i + 1).trim();
    }
  }
  return t;
}

/** Site route joined onto baseUrl. A route that starts with the base path must still be prefixed. */
function useSkillHref(permalink: string): string {
  const {siteConfig} = useDocusaurusContext();
  const base = siteConfig.baseUrl.replace(/\/$/, '');
  const path = permalink.startsWith('/') ? permalink : `/${permalink}`;
  return base ? `${base}${path}` : path;
}

function ItemRow({item}: {item: Item}) {
  const skillHref = useSkillHref(item.permalink);
  const tag =
    item.kind === 'plugin'
      ? 'Plugin'
      : item.protection === 'protected'
        ? 'EDIT WITH CAUTION'
        : null;
  const tagClass =
    item.kind === 'plugin'
      ? styles.tagPlugin
      : styles.tagBundled;
  const zipHref = useBaseUrl(item.name ? `downloads/${item.name}.zip` : '');

  return (
    <div className={styles.row}>
      <div className={styles.rowTitle}>
        {tag ? <span className={`${styles.tag} ${tagClass}`}>{tag}</span> : null}
        <span className={styles.titleLine}>
          {item.kind === 'skill' && item.name ? (
            <a
              className={styles.downloadIconLink}
              href={zipHref}
              download={`${item.name}.zip`}
              aria-label={`Download ${item.title}`}
              title={`Download ${item.title}`}>
              <DownloadIcon className={styles.downloadIcon} />
            </a>
          ) : null}
          <Link to={skillHref} className={styles.titleLink}>
            {item.title}
          </Link>
        </span>
      </div>
      <Link to={skillHref} className={styles.rowDesc}>
        {item.kind === 'skill' ? firstSentence(item.description) : item.description}
      </Link>
    </div>
  );
}

export default function CatalogFilter({kind}: {kind: Kind}): React.ReactElement {
  const items = kind === 'plugin' ? pluginItems : skillItems;
  const fuse = useMemo(() => new Fuse(items, fuseOptions), [items]);
  const protections = useMemo(
    () =>
      uniqueSorted(
        items
          .map((i) => i.protection)
          .filter((p): p is Protection => p === 'protected'),
      ),
    [items],
  );

  const platforms = useMemo(
    () => PLATFORMS.filter((platform) => items.some((item) => item.platform === platform.slug)).map((platform) => platform.slug),
    [items],
  );

  const categories = useMemo(
    () =>
      uniqueInOrder(
        items
          .map((i) => i.category)
          .filter((c): c is string => Boolean(c)),
      ),
    [items],
  );
  const categoryLabels = useMemo(() => {
    const map = new Map<string, string>();
    for (const item of items) {
      if (item.category && !map.has(item.category)) {
        map.set(item.category, item.categoryLabel ?? item.category);
      }
    }
    return map;
  }, [items]);

  const [q, setQ] = useState('');
  const [prot, setProt] = useState<Protection[]>([]);
  const [cats, setCats] = useState<string[]>([]);
  const [platformsSelected, setPlatformsSelected] = useState<PlatformSlug[]>([]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setQ(params.get('q') ?? '');
    setProt(
      (params.get('protection')?.split(',') ?? []).filter((p): p is Protection => p === 'protected'),
    );
    setCats(
      params.get('categories')?.split(',').filter(Boolean) ?? [],
    );
    setPlatformsSelected(
      (params.get('platforms')?.split(',').filter(Boolean) ?? []).filter((slug): slug is PlatformSlug =>
        PLATFORMS.some((platform) => platform.slug === slug),
      ),
    );
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (prot.length) params.set('protection', prot.join(','));
    if (cats.length) params.set('categories', cats.join(','));
    if (platformsSelected.length) params.set('platforms', platformsSelected.join(','));
    const qs = params.toString();
    const url = qs ? `?${qs}` : window.location.pathname;
    window.history.replaceState(null, '', url);
  }, [q, prot, cats, platformsSelected]);

  const results = useMemo(() => {
    let rows = q ? fuse.search(q).map((r) => r.item) : items;
    if (prot.length) rows = rows.filter((r) => r.protection && prot.includes(r.protection));
    if (cats.length) rows = rows.filter((r) => r.category && cats.includes(r.category));
    if (platformsSelected.length) rows = rows.filter((r) => r.platform && platformsSelected.includes(r.platform));
    return rows;
  }, [q, prot, cats, platformsSelected, fuse, items]);

  const grouped = useMemo(() => groupByCategory(results), [results]);

  const allZipHref = useBaseUrl('downloads/skills.zip');
  const hasFilters = q !== '' || prot.length > 0 || cats.length > 0 || platformsSelected.length > 0;
  const title = kind === 'plugin' ? 'Plugins' : 'Search Skills';
  const subtitle =
    kind === 'plugin'
      ? 'Filter plugins bundled in this repository. Open a plugin to see the skills and files it ships.'
      : 'Filter skills by platform, category, keyword, or whether they are protected or overridable. Open a skill to read the details and download the folder.';

  const clearFilters = () => {
    setQ('');
    setProt([]);
    setCats([]);
    setPlatformsSelected([]);
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerTop}>
          <h1 className={styles.title}>{title}</h1>
          {kind === 'skill' ? (
            <a
              className={styles.catalogDownload}
              href={allZipHref}
              download="skills.zip"
              aria-label="Download all installable skills"
              title="Download all installable skills">
              <DownloadIcon className={styles.downloadIcon} />
              Download all installable skills
            </a>
          ) : null}
        </div>
        <p className={styles.subtitle}>{subtitle}</p>

        {kind === 'skill' && platforms.length > 0 && (
          <div className={styles.filterRow}>
            <span className={styles.filterLabel}>Platform</span>
            <div className={styles.chips}>
              {platforms.map((slug) => (
                <label
                  key={slug}
                  className={`${styles.chip} ${styles.chipCategory} ${platformsSelected.includes(slug) ? styles.chipActive : ''}`}>
                  <input
                    type="checkbox"
                    checked={platformsSelected.includes(slug)}
                    onChange={() => setPlatformsSelected((prev) => toggle(prev, slug))}
                  />
                  {platformLabel(slug)}
                </label>
              ))}
            </div>
          </div>
        )}

        {categories.length > 0 && (
          <div className={styles.filterRow}>
            <span className={styles.filterLabel}>Category</span>
            <div className={styles.chips}>
              {categories.map((slug) => (
                <label
                  key={slug}
                  className={`${styles.chip} ${styles.chipCategory} ${cats.includes(slug) ? styles.chipActive : ''}`}>
                  <input
                    type="checkbox"
                    checked={cats.includes(slug)}
                    onChange={() => setCats((prev) => toggle(prev, slug))}
                  />
                  {categoryLabels.get(slug) ?? slug}
                </label>
              ))}
            </div>
          </div>
        )}

        {protections.length > 0 && (
          <div className={styles.filterRow}>
            <span className={styles.filterLabel}>Customization</span>
            <div className={styles.chips}>
              {protections.map((p) => (
                <label
                  key={p}
                  className={`${styles.chip} ${prot.includes(p) ? styles.chipActive : ''}`}>
                  <input
                    type="checkbox"
                    checked={prot.includes(p)}
                    onChange={() => setProt((prev) => toggle(prev, p))}
                  />
                  {p === 'protected' ? 'EDIT WITH CAUTION' : p}
                </label>
              ))}
              {hasFilters && (
                <button type="button" className={styles.clear} onClick={clearFilters}>
                  Clear filters
                </button>
              )}
            </div>
          </div>
        )}

        <div className={styles.filterRow}>
          <span className={styles.filterLabel}>Keyword</span>
          <input
            className={styles.search}
            placeholder={kind === 'plugin' ? 'Filter plugins' : 'e.g. “calc”, “publish”, “spellcheck”'}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label={`Filter ${title.toLowerCase()}`}
          />
          <span className={styles.count}>
            {results.length} {kind === 'plugin' ? 'plugins' : 'skills'}
          </span>
        </div>
      </header>

      <div className={styles.results}>
        {results.length === 0 ? (
          <div className={styles.empty}>
            {items.length === 0
              ? `No ${title.toLowerCase()} in this repository yet.`
              : `No ${title.toLowerCase()} match those filters.`}
          </div>
        ) : kind === 'skill' ? (
          grouped.map((section) => (
            <section key={section.slug || 'uncategorized'} className={styles.section}>
              {section.label ? (
                <h2 className={styles.sectionHeading}>
                  {section.label}
                  {section.platformLabel ? (
                    <span className={styles.platformNote}> ({section.platformLabel})</span>
                  ) : null}
                </h2>
              ) : null}
              <div className={styles.list}>
                {section.items.map((item) => (
                  <ItemRow key={item.key} item={item} />
                ))}
              </div>
            </section>
          ))
        ) : (
          <div className={styles.list}>
            {results.map((item) => (
              <ItemRow key={item.key} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
