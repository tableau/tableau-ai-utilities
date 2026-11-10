// Minimal build-time string-variable substitution for Markdown/MDX content.
//
// Single source of truth for content variables. Author a slug in the form
// `%variable_name%` anywhere in page prose and it is replaced with the value
// below at build time. Percent delimiters are used (not `{{ }}`) because braces
// are interpreted as JSX expressions in MDX; `%…%` is inert text that survives
// parsing and is safe to rewrite in `text` nodes.
export const VARIABLES = {
  product_name: 'Tableau Studio',
  coming_release: 'November 2026 (2026.3.1)',
  site_title: 'Tableau AI Utilities',
};

const TOKEN = /%([a-zA-Z0-9_]+)%/g;

export function applyVariables(value) {
  return value.replace(TOKEN, (match, key) =>
    Object.prototype.hasOwnProperty.call(VARIABLES, key) ? VARIABLES[key] : match,
  );
}

function walk(node) {
  if (node.type === 'text' && typeof node.value === 'string') {
    node.value = applyVariables(node.value);
  }
  if (
    (node.type === 'link' || node.type === 'image' || node.type === 'definition') &&
    typeof node.url === 'string'
  ) {
    node.url = applyVariables(node.url);
  }
  if (Array.isArray(node.children)) {
    for (const child of node.children) {
      walk(child);
    }
  }
}

export default function remarkVariables() {
  return (tree) => {
    walk(tree);
  };
}
