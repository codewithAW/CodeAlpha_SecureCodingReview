# CodeAlpha Task 3 coverage
| Requirement | Implementation | Evidence |
|---|---|---|
| Select a language and application | Python Flask team-records application backed by SQLite | backend/app.py |
| Review source for weaknesses | Manual comparison of four isolated original excerpts with corrected handlers | audit/baseline.txt and frontend/public/artifacts/audit.json |
| Use manual inspection or static analysis | Handler and query inspection plus repeatable Bandit invocation | audit/run.py and artifacts/bandit.json |
| Recommend secure practices | Per-finding remediation, corrected code and developer exercises | Remediation and Developer lab |
| Document findings and fixes | Generated Markdown, printable report, JSON and named regression tests | SECURITY_AUDIT_REPORT.md and tests/ |

Scanner availability and HTTP integration coverage are recorded separately from manual inspection.
