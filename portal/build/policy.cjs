const path = require('node:path');
const BASE = '/adk-training/';

function sourcePolicy(resource) {
  const normalized = (resource || '').replaceAll('\\', '/').split('?')[0];
  const match = normalized.match(/\/training\/(module[^/]+)\/(.+)/);
  if (!match) return null;
  return {module: match[1], solution: /(^|\/)lab-solution(?:\.|\/|$)/.test(match[2])};
}
function key(policy) {
  return policy ? `${policy.module}:${policy.solution ? 'solutions' : 'lessons'}` : 'approved';
}
function unique(policies) {
  return [...new Map(policies.filter(Boolean).map(p => [key(p), p])).values()];
}
function isolatedPolicy(policies, name) {
  const distinct = unique(policies);
  if (distinct.length > 1) throw new Error(`Mixed content permissions in ${name}: ${distinct.map(key).join(', ')}`);
  return distinct[0] || null;
}
function routeForFile(file) {
  const relative = file.replaceAll(path.sep, '/');
  if (relative === 'index.html') return BASE;
  return BASE + relative.replace(/index\.html$/, '').replace(/\.html$/, '/');
}
module.exports = {BASE, sourcePolicy, key, unique, isolatedPolicy, routeForFile};
