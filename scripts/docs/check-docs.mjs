#!/usr/bin/env node
// Docs integrity: context.md exists and links the key files; every docs/*.md ends with a Next line;
// relative markdown links resolve. Component drift is checked separately (gen-components --check).
import fs from 'node:fs'
import path from 'node:path'

const problems = []
const need = ['AGENTS.md', 'docs/components/README.md', 'docs/FAILURE-LEDGER.md', 'docs/logs/events.jsonl']
if (!fs.existsSync('context.md')) problems.push('context.md missing')
else {
  const ctx = fs.readFileSync('context.md', 'utf8')
  for (const n of need) if (!ctx.includes(n)) problems.push(`context.md does not mention ${n}`)
}
for (const n of need) if (!fs.existsSync(n)) problems.push(`missing ${n}`)

// Optional: docs/.docs-check-ignore, one path substring per line, skips the Next-line check for matching files.
const ignore = fs.existsSync('docs/.docs-check-ignore')
  ? fs.readFileSync('docs/.docs-check-ignore', 'utf8').split(/\r?\n/).map((l) => l.trim()).filter((l) => l && !l.startsWith('#'))
  : []
const mdFiles = []
const walk = (d) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) { if (!['node_modules', '.git'].includes(e.name)) walk(p) } else if (p.endsWith('.md')) mdFiles.push(p) } }
walk('docs')
for (const f of mdFiles) {
  const src = fs.readFileSync(f, 'utf8')
  if (!/\*\*Next:\*\*[^\n]*context\.md/.test(src) && !f.includes(`${path.sep}evidence${path.sep}`) && !ignore.some((i) => f.split(path.sep).join('/').includes(i))) problems.push(`${f}: no "Next: ... context.md" line`)
  for (const m of src.matchAll(/\]\((?!https?:|#|mailto:)([^)#\s]+)(?:#[^)]*)?\)/g)) {
    const target = path.resolve(path.dirname(f), m[1])
    if (!fs.existsSync(target)) problems.push(`${f}: broken link ${m[1]}`)
  }
}
if (problems.length) { console.error('Docs problems:\n - ' + problems.join('\n - ')); process.exit(1) }
console.log('docs ok')
