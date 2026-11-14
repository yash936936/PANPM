#!/usr/bin/env node
// Self-test: builds a throwaway repo and exercises every bundled script, including
// break-on-purpose checks and regressions. Run once after copying scripts into a project:
//   node scripts/selftest.mjs        (exit 0 = all passed; touches only a temp dir)
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'docs-selftest-'))
const w = (f, t) => { fs.mkdirSync(path.dirname(path.join(tmp, f)), { recursive: true }); fs.writeFileSync(path.join(tmp, f), t) }
const run = (script, args = [], env = {}) => spawnSync(process.execPath, [path.join(here, script), ...args], { cwd: tmp, encoding: 'utf8', env: { ...process.env, ...env } })
const git = (...a) => spawnSync('git', a, { cwd: tmp, encoding: 'utf8' })
let pass = 0, fail = 0
const ok = (name, cond, detail = '') => { cond ? pass++ : fail++; console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}${cond ? '' : '  ' + detail}`) }

w('src/alpha/__init__.py', '"""Alpha: does the alpha thing."""\ndef helper():\n    pass\n')
w('src/beta/index.ts', '// Beta: does the beta thing.\nexport class Beta {}\n')
w('tests/test_alpha.py', 'def test_x(): pass\n')
w('context.md', '# ctx\nAGENTS.md docs/components/README.md docs/FAILURE-LEDGER.md docs/logs/events.jsonl\n\n---\n**Next:** x\n')
w('AGENTS.md', 'x\n'); w('docs/logs/events.jsonl', '')

// components
ok('gen-components writes (py + ts)', run('docs/gen-components.mjs').status === 0)
const alpha = fs.readFileSync(path.join(tmp, 'docs/components/alpha.md'), 'utf8')
ok('python docstring + defs picked up', alpha.includes('does the alpha thing') && alpha.includes('`helper`'))
ok('python tests matched', alpha.includes('tests/test_alpha.py'))
ok('--check passes when in sync', run('docs/gen-components.mjs', ['--check']).status === 0)
w('src/beta/index.ts', '// Beta: does the beta thing.\nexport class Beta {}\nexport function added() {}\n')
ok('--check FAILS on drift (broken on purpose)', run('docs/gen-components.mjs', ['--check']).status === 1)
run('docs/gen-components.mjs')

// docs check (scaffold step generates the ledger before check-docs needs it)
run('events/failure-report.mjs')
ok('check-docs passes on good tree', run('docs/check-docs.mjs').status === 0)
w('docs/bad.md', '# no next line\n')
ok('check-docs FAILS without Next line', run('docs/check-docs.mjs').status === 1)
w('docs/.docs-check-ignore', 'bad.md\n')
ok('check-docs ignore file works', run('docs/check-docs.mjs').status === 0)
fs.rmSync(path.join(tmp, 'docs/bad.md')); fs.rmSync(path.join(tmp, 'docs/.docs-check-ignore'))

// redaction regression: no offset digits leaked
const lib = await import(path.join(here, 'events/lib.mjs'))
ok('redact has no offset leak', lib.redact('curl x sk-abcdefghijklmnop done') === 'curl x [redacted] done', lib.redact('curl x sk-abcdefghijklmnop done'))
ok('redact keeps key= prefix', lib.redact('token=abc123456789 ok') === 'token=[redacted] ok')

// signature regression: different failures stay different even with identical runner summary
const summary = '\n Test Files  1 failed | 3 passed (4)\n      Tests  1 failed | 20 passed (21)'
const s1 = lib.signatureOf('FAIL test/a.test.ts > parses dates\nAssertionError: expected 1 to be 2' + summary)
const s2 = lib.signatureOf('FAIL test/z.test.ts > other bug\nTypeError: x is not a function' + summary)
ok('distinct failures get distinct signatures', s1 !== s2, `${s1} | ${s2}`)
ok('signature is not a runner summary', !/passed/.test(s1) && !/passed/.test(s2), s1)
ok('same failure, different line numbers, same signature', lib.signatureOf('Error: boom at line 3') === lib.signatureOf('Error: boom at line 99'))

// HOLD flow
const fails = (n) => { let last; for (let i = 0; i < n; i++) last = run('events/run-logged.mjs', ['--area', 'T', '--', process.execPath, '-e', `console.error('Error: boom ${i}'); process.exit(1)`]); return last }
const third = fails(3)
ok('HOLD banner on 3rd identical failure', /HOLD/.test(third.stderr), third.stderr.slice(-200))
ok('failure-report --check exits 3 on HOLD', run('events/failure-report.mjs', ['--check']).status === 3)
const bad = run('events/log-event.mjs', ['--kind', 'resolution', '--area', 'T', '--signature', 'nope', '--summary', 'x'])
ok('resolution with unknown signature warns', /no existing failure/.test(bad.stderr))
const sig = lib.summarise(lib.readEvents(path.join(tmp, 'docs/logs/events.jsonl')))[0].signature
run('events/log-event.mjs', ['--kind', 'resolution', '--area', 'T', '--signature', sig, '--summary', 'Put on hold, D-001'])
ok('resolution clears HOLD (on-hold)', run('events/failure-report.mjs', ['--check']).status === 0 && /on-hold/.test(fs.readFileSync(path.join(tmp, 'docs/FAILURE-LEDGER.md'), 'utf8')))
const env = run('events/log-event.mjs', ['--summary', 'n', '--actor', 'a'], { EVENTS_HOLD_THRESHOLD: '2' })
ok('log-event works with EVENTS_* env', env.status === 0)

// secret scan (needs git)
if (git('init', '-q').status === 0) {
  git('config', 'user.email', 't@t'); git('config', 'user.name', 't')
  git('add', '-A')
  ok('secret-scan clean tree passes', run('ci/secret-scan.mjs').status === 0)
  w('leak.js', 'const k="sk-" + "abcdefghijklmnopqrstuvwxyz123456"\n'); git('add', 'leak.js')
  const leak = run('ci/secret-scan.mjs')
  ok('secret-scan FAILS on planted key and never prints it', leak.status === 1 && !leak.stderr.includes('sk-abcdef'))
} else console.log('SKIP  secret-scan (git not available)')

fs.rmSync(tmp, { recursive: true, force: true })
console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail ? 1 : 0)
