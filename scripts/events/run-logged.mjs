#!/usr/bin/env node
// Run a command, log its outcome (redacted), refresh the failure ledger,
// and print a HOLD banner if the same failure has recurred past the threshold.
//   node scripts/events/run-logged.mjs --area S3 -- node --version
//   node scripts/events/run-logged.mjs --area CI --shell -- npm test     (Windows .cmd tools need --shell)
import { spawnSync } from 'node:child_process'
import { appendEvent, signatureOf, redact, readEvents, summarise, DEFAULT_HOLD_THRESHOLD } from './lib.mjs'
import { writeLedger } from './failure-report.mjs'

const argv = process.argv.slice(2)
const sep = argv.indexOf('--')
if (sep < 0 || sep === argv.length - 1) { console.error('usage: run-logged.mjs [--area X] [--shell] -- <command> [args]'); process.exit(2) }
const opts = argv.slice(0, sep)
const cmd = argv.slice(sep + 1)
const area = opts.includes('--area') ? opts[opts.indexOf('--area') + 1] : undefined
const useShell = opts.includes('--shell')

const started = Date.now()
const r = useShell
  ? spawnSync(cmd.join(' '), { shell: true, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
  : spawnSync(cmd[0], cmd.slice(1), { shell: false, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
const out = (r.stdout || '') + (r.stderr || '')
process.stdout.write(r.stdout || '')
process.stderr.write(r.stderr || '')

const code = r.error ? 127 : (r.status ?? 1)
const ok = code === 0
const combined = r.error ? `${r.error.message}\n${out}` : out
const sig = ok ? undefined : signatureOf(combined)
const tail = redact(combined.split(/\r?\n/).slice(-12).join('\n'))
appendEvent({
  kind: 'command', area, cmd: redact(cmd.join(' ')), exit: code, outcome: ok ? 'success' : 'failure',
  durationMs: Date.now() - started, signature: sig, tail: ok ? undefined : tail,
})
writeLedger()
if (!ok) {
  const row = summarise(readEvents()).find((x) => x.area === (area || '-') && x.signature === sig)
  if (row && row.status === 'HOLD') {
    console.error(`\n=== HOLD: this failure has now occurred ${row.count} times (threshold ${DEFAULT_HOLD_THRESHOLD}) ===\nSignature: ${row.signature}\nStop retrying. Follow AGENTS.md "Repeated failure rule": write it up, then change the part wholesale or put it on hold with a logged decision.`)
  }
}
process.exit(code)
