import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import {
  githubRepoUrlFromGithubOrigin,
  OFFICIAL_ORIGIN,
  outboundEnvFromGithubOrigin,
  siteBaseUrlFromEnv,
  siteOriginFromEnv,
} from './src/extLinks/resolve';
import remarkExtLinks from './src/remark/extLinks.mjs';
import remarkVariables, {applyVariables, VARIABLES} from './src/remark/variables.mjs';

// The official public GitHub Pages origin. Any build whose GITHUB_ORIGIN is not
// this value is treated as an unofficial (e.g. an internal enterprise preview)
// build: it is served under a different base path and marked noIndex so it
// cannot be crawled or mistaken for the public site. Defaults preserve the
// public build at https://tableau.github.io/tableau-ai-utilities/.
const githubOrigin = siteOriginFromEnv(process.env.GITHUB_ORIGIN);
const isOfficial = githubOrigin === OFFICIAL_ORIGIN;
const baseUrl = siteBaseUrlFromEnv(process.env.GITHUB_BASE_PATH);
// Outbound sibling-docs env is independent of chrome: unset GITHUB_ORIGIN
// (local start/build) selects stage bases, even though chrome defaults official.
const extLinkEnv = outboundEnvFromGithubOrigin(process.env.GITHUB_ORIGIN);
// Navbar/footer/edit "GitHub" links: official origin → github.com; preview
// (unset GITHUB_ORIGIN, git.soma CI, local start) → git.soma repo.
const githubRepoUrl = githubRepoUrlFromGithubOrigin(
  process.env.GITHUB_ORIGIN,
  process.env.GITHUB_SERVER_URL,
  process.env.GITHUB_REPOSITORY,
);
const [githubOrg, githubProject] = githubRepoUrl.replace(/\/$/, '').split('/').slice(-2);

const config: Config = {
  title: VARIABLES.site_title,
  tagline: 'Skills that change how Tableau Agent authors, checks, and ships workbooks',
  favicon: 'img/logo.svg',
  trailingSlash: false,

  future: {
    v4: true,
  },

  url: githubOrigin,
  baseUrl,

  noIndex: !isOfficial,

  organizationName: githubOrg,
  projectName: githubProject,
  deploymentBranch: 'gh-pages',

  onBrokenLinks: 'warn',
  onBrokenAnchors: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
    parseFrontMatter: async (params) => {
      const result = await params.defaultParseFrontMatter(params);
      for (const [key, value] of Object.entries(result.frontMatter)) {
        if (typeof value === 'string') {
          result.frontMatter[key] = applyVariables(value);
        }
      }
      return result;
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  customFields: {
    extLinkEnv,
    githubRepoUrl,
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          editUrl: `${githubRepoUrl}/tree/main/`,
          beforeDefaultRemarkPlugins: [remarkExtLinks, remarkVariables],
          async sidebarItemsGenerator({defaultSidebarItemsGenerator, ...args}) {
            const items = await defaultSidebarItemsGenerator(args);
            const hide = new Set(['plugins/index']);
            function strip(
              nodes: typeof items,
            ): typeof items {
              const out: typeof items = [];
              for (const item of nodes) {
                if (item.type === 'doc' && 'id' in item && hide.has(item.id)) {
                  continue;
                }
                if (item.type === 'category') {
                  out.push({...item, items: strip(item.items)});
                  continue;
                }
                out.push(item);
              }
              return out;
            }
            return strip(items);
          },
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    docs: {
      sidebar: {
        autoCollapseCategories: true,
      },
    },
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: VARIABLES.site_title,
      logo: {
        alt: 'Tableau',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'custom-github',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Catalog',
          items: [
            {label: 'Overview', to: '/'},
            {label: 'Search Skills', to: '/skills'},
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'GitHub', href: githubRepoUrl},
            {label: 'Tableau MCP', href: 'https://tableau.github.io/tableau-mcp/'},
          ],
        },
      ],
      copyright: `Copyright ©${new Date().getFullYear()} Salesforce, Inc. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
