# Regression and gotcha register

Quality trial started 2026-10-20. Review friction around 2026-11-20. Pass counters below record new, independently evidenced runs only, not historical results.

## Regressions

No regression checks recorded yet. Entry format: - [YYYY-MM-DD] <bug> -> check: <deterministic re-run command> | consecutive passes: n/5. Do not record historical results as passes.

Five recorded consecutive passes make a check eligible for automation; adding CI is a separate code change. Record revision, environment and evidence before increasing a count. No automatic edits or release approval follow from a counter.

## Gotchas


- [2026-10-20] Historical archive: known limitations are documented as learnings - do not silently "fix" history; new work is documented as new work | source: owner decision 2026-10-10 (option A: publish as archive) | version: current | validity: permanent | projects: Build-a-blog.
- [2026-10-20] Comments/likes/contact flows have not had a security audit - do not describe the app as fully secure in copy | source: revival workstream record, 2026-10-14 | version: current | validity: until those flows are audited | projects: Build-a-blog.
- [2026-10-20] No live backend: the old Heroku deploy is retired; the README's local run instructions are the way to try it | source: revival workstream record, 2026-10 | version: current | validity: until new hosting exists | projects: Build-a-blog.

## Check entry points

Django blog (historical) - inspect the repo's test tooling; no live deploy. Report exactly what ran and where.

If a gotcha is independently observed in a second project, propose a shared rule with both sources.
