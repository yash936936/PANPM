.PHONY: docs-components docs-check events-report events-check secrets selftest lint test

docs-components:
	node scripts/docs/gen-components.mjs

docs-check:
	node scripts/docs/gen-components.mjs --check
	node scripts/docs/check-docs.mjs

events-report:
	node scripts/events/failure-report.mjs

events-check:
	node scripts/events/failure-report.mjs --check

secrets:
	node scripts/ci/secret-scan.mjs

selftest:
	node scripts/selftest.mjs

lint:
	ruff check .

test:
	pytest -q
