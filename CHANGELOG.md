# Changelog

## Unreleased

- Masked substituted input values such as GitHub PATs in `cursor_mcp_smoke.py` command, error, and stderr output, and added tests for the script.
- Made `rk_health.py --strict` meaningful: strict mode now requires the `mature` readiness level before reporting the library as usable.
- Made `auto_standardize_runs.py` tolerate unreadable directories and vanished files during unattended scans.
- Removed the unreferenced legacy README workflow image to shrink clone size.
- Added `seed_demo_db.py --include-run` so the Quick Start demo database can include the freshly standardized smoke run.
- Made generated `run_id` values independent of machine-local absolute paths.
- Added an end-to-end Quick Start demo test.
- Updated contribution checks and Quick Start documentation.

## v0.1.0 - 2026-06-17

- Added first-run bootstrap script for a local ResearchKB smoke workspace.
- Added GitHub Actions CI for compilation, tests, JSON validation, and public hygiene scanning.
- Split experiment metrics contracts into a generic contract and a KV-cache reuse extension.
- Added synthetic `examples/` for smoke runs, failure cases, paper memory, and evidence-grounded agent answers.
- Improved `rk_health.py` with readiness levels, missing-table tolerance, `--root`, `--strict`, and next actions.
- Added pytest coverage for empty, smoke, usable, mature, watch-list, and UTF-16 log cases.
- Added public project hygiene files: `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, and `ROADMAP.md`.
- Cleaned public ignore rules to remove personal-project traces.
- Clarified the first-run onboarding loop in README files.
