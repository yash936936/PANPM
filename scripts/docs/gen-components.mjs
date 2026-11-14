#!/usr/bin/env node
// Generate / verify docs/components/<area>.md from the source tree.
//   node scripts/docs/gen-components.mjs          write (keeps hand-written sections)
//   node scripts/docs/gen-components.mjs --check  exit 1 on drift (used by CI)
// Areas (first match wins):
//   1. docs/components.config.json: { "areas": [{ "name": "api", "dir": "src/api", "kind": "service" }], "extensions": [".ts", ".py"], "testDirs": ["test", "tests"] }
//   2. src/bundles/*  (plus src/cli, src/profiles, src/util when present)
//   3. every directory directly under src/
// Languages: .ts/.tsx/.js/.mjs/.cjs/.py by default. Rule: one file per responsibility;
// a source file that lacks a header comment is flagged.
import fs from 'node:fs'
import path from 'node:path'

const ROOT = process.cwd()
const OUT = path.join(ROOT, 'docs/components')
const BEGIN = '<!-- BEGIN GENERATED: do not edit between markers -->'
const END = '<!-- END GENERATED -->'
const check = process.argv.includes('--check')

const rel = (p) => p.split(path.sep).join('/')
const listDir = (d) => (fs.existsSync(d) ? fs.readdirSync(d, { withFileTypes: true }) : [])

const cfgPath = path.join(ROOT, 'docs/components.config.json')
const cfg = fs.existsSync(cfgPath) ? JSON.parse(fs.readFileSync(cfgPath, 'utf8')) : {}
const EXTS = cfg.extensions ?? ['.ts', '.tsx', '.js', '.mjs', '.cjs', '.py']
const TEST_DIRS = cfg.testDirs ?? ['test', 'tests']
const isSource = (f) => EXTS.some((e) => f.endsWith(e))
const isPy = (f) => f.endsWith('.py')

function areas() {
  if (Array.isArray(cfg.areas)) return cfg.areas.map((a) => ({ name: a.name, dir: path.join(ROOT, a.dir), kind: a.kind ?? 'area' })).sort((a, b) => a.name.localeCompare(b.name))
  const out = []
  if (fs.existsSync(path.join(ROOT, 'src/bundles'))) {
    for (const e of listDir(path.join(ROOT, 'src/bundles'))) if (e.isDirectory()) out.push({ name: e.name, dir: path.join(ROOT, 'src/bundles', e.name), kind: 'bundle' })
    for (const n of ['cli', 'profiles', 'util']) if (fs.existsSync(path.join(ROOT, 'src', n))) out.push({ name: n, dir: path.join(ROOT, 'src', n), kind: 'support' })
  } else {
    for (const e of listDir(path.join(ROOT, 'src'))) if (e.isDirectory() && !['__pycache__', 'node_modules'].includes(e.name)) out.push({ name: e.name, dir: path.join(ROOT, 'src', e.name), kind: 'area' })
  }
  return out.sort((a, b) => a.name.localeCompare(b.name))
}

function walk(dir) {
  return listDir(dir).flatMap((e) => (e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)])).sort()
}

function headerComment(src, py = false) {
  if (py) {
    const body = src.replace(/^#!.*\n/, '').replace(/^# -\*-.*\n/, '')
    const d = body.match(/^\s*(?:"""|''')([\s\S]*?)(?:"""|''')/)
    if (d) return d[1].split('\n').map((l) => l.trim()).filter(Boolean)[0] ?? ''
    const c = body.match(/^\s*((?:#[^\n]*\n?)+)/)
    return c ? c[1].split('\n').map((l) => l.replace(/^#\s?/, '').trim()).filter(Boolean)[0] ?? '' : ''
  }
  const m = src.match(/^\s*(?:\/\*\*?([\s\S]*?)\*\/|((?:\/\/[^\n]*\n?)+))/)
  if (!m) return ''
  const raw = (m[1] ?? m[2]).split('\n').map((l) => l.replace(/^\s*(\*|\/\/)\s?/, '').trim()).filter(Boolean)
  return raw[0] ?? ''
}

function exportsOf(src, py = false) {
  const names = new Set()
  if (py) {
    for (const m of src.matchAll(/^(?:async\s+)?(?:def|class)\s+([A-Za-z][A-Za-z0-9_]*)/gm)) names.add(m[1])
    return [...names]
  }
  for (const m of src.matchAll(/^export\s+(?:default\s+)?(?:declare\s+)?(?:abstract\s+)?(class|function\*?|const|let|interface|type|enum)\s+([A-Za-z0-9_$]+)/gm)) names.add(`${m[2]}`)
  for (const m of src.matchAll(/^export\s*\{([^}]+)\}/gm)) m[1].split(',').map((s) => s.trim().split(/\s+as\s+/).pop()).filter(Boolean).forEach((n) => names.add(n))
  return [...names]
}

function bundleDeps(src, self) {
  const deps = new Set()
  for (const m of src.matchAll(/from\s+['"]((?:\.\.\/)+(?:bundles\/)?([a-z0-9-]+))(?:\/[^'"]*)?['"]/g)) if (m[2] !== self && m[2] !== 'util') deps.add(m[2])
  return [...deps]
}

function testsFor(name) {
  const hits = []
  for (const d of TEST_DIRS) for (const e of listDir(path.join(ROOT, d))) {
    if (e.isFile() && (e.name.startsWith(name) || e.name.startsWith(`test_${name}`)) && /(\.(test|spec)\.[cm]?[jt]sx?|^test_.*\.py|_test\.py)$/.test(e.name)) hits.push(`${d}/${e.name}`)
  }
  return hits
}

function generated(area) {
  const files = walk(area.dir).filter((f) => isSource(f) && !/__pycache__/.test(f))
  const deps = new Set()
  const rows = files.map((f) => {
    const src = fs.readFileSync(f, 'utf8')
    if (!isPy(f)) bundleDeps(src, area.name).forEach((d) => deps.add(d))
    const ex = exportsOf(src, isPy(f))
    const note = headerComment(src, isPy(f))
    return `| \`${rel(path.relative(ROOT, f))}\` | ${ex.length ? ex.map((x) => '`' + x + '`').join(', ') : '-'} | ${note || '**(no header comment)**'} |`
  })
  const tests = testsFor(area.name)
  return [
    BEGIN,
    '',
    '### Files and exports',
    '',
    '| File | Exports | Responsibility (first header-comment line) |',
    '|---|---|---|',
    ...rows,
    '',
    `**Imports other areas:** ${deps.size ? [...deps].sort().map((d) => '`' + d + '`').join(', ') : '(none)'}`,
    '',
    `**Tests:** ${tests.length ? tests.map((t) => '`' + t + '`').join(', ') : '(none matched by name)'}`,
    '',
    END,
  ].join('\n')
}

function skeleton(area) {
  return [
    `# Component: ${area.name}`,
    '',
    `> Area type: ${area.kind}. Location: \`${rel(path.relative(ROOT, area.dir))}/\`. Hand-written sections below are yours to edit; the generated block is rewritten by \`npm run docs:components\`.`,
    '',
    '## Purpose',
    '(open — one or two sentences: what this component is responsible for, and what it must NOT do)',
    '',
    '## Route (how control reaches it)',
    '(open — who registers or calls it, in what order, and what it calls next; name the ctx key, hooks or events)',
    '',
    '## Config surface and invariants',
    '(open — config keys, limits, fail-closed behaviour, anything a caller must never assume)',
    '',
    '## Known limits',
    '(open — honest list, linked to decision / debug IDs)',
    '',
    '',
  ].join('\n')
}

fs.mkdirSync(OUT, { recursive: true })
const problems = []
const index = []
for (const area of areas()) {
  const file = path.join(OUT, `${area.name}.md`)
  const block = generated(area)
  let doc = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : skeleton(area) + block + '\n\n---\n**Next:** Return to [`context.md`](../../context.md).\n'
  if (!doc.includes(BEGIN)) doc = doc.replace(/\n---\n\*\*Next:\*\*/, `\n${block}\n\n---\n**Next:**`)
  const next = doc.replace(new RegExp(`${BEGIN}[\\s\\S]*?${END}`), () => block)
  if (!fs.existsSync(file)) problems.push(`missing doc: docs/components/${area.name}.md`)
  else if (next !== doc || fs.readFileSync(file, 'utf8') !== next) problems.push(`stale generated block: docs/components/${area.name}.md`)
  if (/\(open — /.test(next)) console.warn(`warn: docs/components/${area.name}.md still has unfilled (open — ...) sections`)
  if (/\*\*\(no header comment\)\*\*/.test(next)) console.warn(`warn: ${area.name} has source files without a header comment`)
  if (!check) fs.writeFileSync(file, next)
  index.push(`| [${area.name}](${area.name}.md) | ${area.kind} | \`${rel(path.relative(ROOT, area.dir))}/\` |`)
}

const readme = ['# Component docs', '', 'One file per research area. Hand-written sections describe purpose, route, configuration and limits; the generated block stays in sync with `src/` and CI checks for drift. Rule: one source file per responsibility.', '', '| Component | Type | Location |', '|---|---|---|', ...index, '', '---', '**Next:** Return to [`context.md`](../../context.md).', ''].join('\n')
const readmePath = path.join(OUT, 'README.md')
if (fs.existsSync(readmePath) ? fs.readFileSync(readmePath, 'utf8') !== readme : true) { if (check) problems.push('stale: docs/components/README.md'); else fs.writeFileSync(readmePath, readme) }

if (check && problems.length) { console.error('Component docs drift:\n - ' + problems.join('\n - ') + '\nRun: npm run docs:components'); process.exit(1) }
console.log(check ? 'component docs in sync' : `wrote ${index.length} component docs`)
