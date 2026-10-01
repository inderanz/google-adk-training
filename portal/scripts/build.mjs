import {cp, mkdir, readdir, readFile, writeFile, rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {spawnSync, execFileSync} from 'node:child_process';

const root = fileURLToPath(new URL('../../', import.meta.url));
const portal = path.join(root, 'portal');
const content = path.join(portal, 'generated/training');
await mkdir(path.dirname(content), {recursive: true});
// Docusaurus generated registry.js mixes ESM imports with require.resolveWeak.
// Keep webpack's default JS parser rather than inheriting portal's ESM package.
await writeFile(path.join(portal, 'generated/package.json'), '{"private":true}\n');
await rm(content, {recursive: true, force: true});
await rm(path.join(portal, 'generated/docusaurus'), {recursive: true, force: true});
let sourceRoot = root;
let revision = null;
if (process.env.PORTAL_CONTENT_REF) {
  revision = execFileSync('git', ['rev-parse', '--verify', `${process.env.PORTAL_CONTENT_REF}^{commit}`], {cwd: root, encoding: 'utf8'}).trim();
  sourceRoot = path.join(portal, 'generated/source');
  await rm(sourceRoot, {recursive: true, force: true});
  await mkdir(sourceRoot, {recursive: true});
  const rootFiles = execFileSync('git', ['ls-tree', '--name-only', revision], {cwd: root, encoding: 'utf8'}).trim().split('\n').filter(f => f.endsWith('.md'));
  const archive = execFileSync('git', ['archive', revision, 'training', ...rootFiles], {cwd: root, maxBuffer: 256 * 1024 * 1024});
  const extracted = spawnSync('tar', ['-xf', '-', '-C', sourceRoot], {input: archive});
  if (extracted.status !== 0) throw new Error('Could not extract requested content revision');
  console.log(`Using explicitly requested committed content: ${revision}`);
}
await cp(path.join(sourceRoot, 'training'), content, {recursive: true});
// Mirror CI's root-document preparation in a disposable copy only.
for (const file of await readdir(sourceRoot)) {
  if (['README.md', 'CONTRIBUTING.md', 'ATTRIBUTION.md'].includes(file) || /^(timetable|variant)-.*\.md$/.test(file)) {
    const text = (await readFile(path.join(sourceRoot, file), 'utf8')).replaceAll('(./training/', '(./');
    await writeFile(path.join(content, file), text);
  }
}
async function adaptPortalLinks(directory) {
  for (const entry of await readdir(directory, {withFileTypes: true})) {
    const filename = path.join(directory, entry.name);
    if (entry.isDirectory()) await adaptPortalLinks(filename);
    else if (/\.mdx?$/.test(entry.name)) {
      const original = await readFile(filename, 'utf8');
      // Only local link destinations; preserve absolute public GitHub URLs.
      const adapted = original.replace(/(\]\(|(?:href|to)=["'])\/google-adk-training\//g, '$1/adk-training/');
      if (adapted !== original) await writeFile(filename, adapted);
    }
  }
}
await adaptPortalLinks(content);
await writeFile(path.join(portal, 'generated/build-info.json'), JSON.stringify({contentRevision: revision || 'working-tree snapshot', builtAt: new Date().toISOString()}, null, 2));
const result = spawnSync(process.execPath, [
  'node_modules/@docusaurus/core/bin/docusaurus.mjs', 'build',
  '--config', 'docusaurus.portal.config.js', '--out-dir', '../portal/dist',
], {cwd: path.join(root, 'doc'), stdio: 'inherit', env: {...process.env, NODE_ENV: 'production', DOCUSAURUS_GENERATED_FILES_DIR_NAME: path.join(portal, 'generated/docusaurus')}});
if (result.status !== 0) process.exit(result.status || 1);
await mkdir(path.join(portal, 'dist/portal'), {recursive: true});
await cp(path.join(portal, 'public'), path.join(portal, 'dist/portal'), {recursive: true});
console.log('Protected portal build ready. Run npm test and npm run check before deployment.');
