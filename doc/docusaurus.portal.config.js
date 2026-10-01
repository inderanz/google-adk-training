import config from './docusaurus.config.js';

// A separate profile: the default GitHub Pages build is deliberately unchanged.
export default {
  ...config,
  url: 'https://gyanhq.com',
  baseUrl: '/adk-training/',
  trailingSlash: true,
  noIndex: true,
  customFields: {...config.customFields, portal: true},
  presets: [[
    '@docusaurus/preset-classic',
    {
      ...config.presets[0][1],
      docs: {
        ...config.presets[0][1].docs,
        path: '../portal/generated/training',
        // Solutions are now visible in navigation; the Worker enforces release.
        sidebarItemsGenerator: undefined,
      },
      sitemap: false,
    },
  ]],
  themeConfig: {
    ...config.themeConfig,
    navbar: {
      ...config.themeConfig.navbar,
      title: 'GyanHQ · ADK Training',
      items: [
        {href: '/adk-training/learn/', label: 'Course catalogue', position: 'left'},
        {href: 'https://gyanhq.com/', label: 'GyanHQ', position: 'right'},
      ],
    },
  },
  // The portal has its own canonical URLs; public-site redirects remain there.
  plugins: ['./../portal/build/plugin.cjs'],
};
