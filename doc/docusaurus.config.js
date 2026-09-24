const config = {
  title: 'Mastering Google ADK: From First Agent to Production',
  url: 'https://inderanz.github.io',
  baseUrl: '/google-adk-training/',
  favicon: 'img/favicon.png',
  onBrokenLinks: 'warn',
  markdown: {
    mermaid: true,
    preprocessor({fileContent}) {
      // Docusaurus MDX v2/v3 treats raw HTML comments <!-- ... --> as JSX syntax errors.
      // Automatically convert them to safe MDX comments {/* ... */} across all docs.
      return fileContent.replace(/<!--([\s\S]*?)-->/g, '{/*$1*/}');
    },
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
  themes: ['@docusaurus/theme-mermaid'],
  themeConfig: {
    image: 'img/social-card.jpg',
    navbar: {
      title: 'Mastering Google ADK: From First Agent to Production',
      logo: {
        alt: 'Inder Chauhan',
        src: 'img/favicon.png',
      },
      items: [
        {
          to: '/docs/module01-intro-to-ai-agents/',
          label: 'Modules',
          position: 'left',
        },
        {
          href: 'https://github.com/inderanz/google-adk-training',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Course',
          items: [
            {label: 'Start Module 01', to: '/docs/module01-intro-to-ai-agents/'},
            {label: 'All Modules', to: '/docs/'},
          ],
        },
        {
          title: 'Instructor',
          items: [
            {label: 'LinkedIn', href: 'https://www.linkedin.com/in/ichauhan/'},
            {label: 'GitHub', href: 'https://github.com/inderanz/google-adk-training'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Inder Chauhan. Built with Docusaurus.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: './sidebars.js',
          path: '../training',
          routeBasePath: '/docs',
          include: ['**/*.md', '**/*.mdx'],
          async sidebarItemsGenerator({defaultSidebarItemsGenerator, ...args}) {
            const sidebarItems = await defaultSidebarItemsGenerator(args);

            // Recursive function to filter out 'lab-solution' items
            const filterSolutions = (items) => {
              return items.filter((item) => {
                // If it's a category, filter its children recursively
                if (item.type === 'category') {
                  item.items = filterSolutions(item.items);
                  // Keep the category only if it's not empty (optional, but good for clean menus)
                  return item.items.length > 0;
                }
                // If it's a doc, check if its ID is 'lab-solution'
                if (item.type === 'doc') {
                  return !item.id.endsWith('lab-solution');
                }
                return true;
              });
            };

            return filterSolutions(sidebarItems);
          },
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        // Every doc used to live at the site root (routeBasePath: '/').
        // Now docs live under /docs — redirect every old bare URL to its
        // new /docs-prefixed home so no previously-shared link breaks.
        createRedirects(existingPath) {
          if (existingPath.startsWith('/docs/')) {
            return [existingPath.replace(/^\/docs\//, '/')];
          }
          return undefined;
        },
      },
    ],
  ],
};

export default config;
