# CyberShield CodeGuard
Application Security Intelligence Platform · CodeAlpha Cyber Security Internship, Task 3 · Abdul Waheed

## Open the finished portfolio on Windows
Extract the entire ZIP into your task3 folder. Double-click **frontend/dist/Open-CodeGuard.html**. Keep its adjacent artifacts folder for working evidence downloads. No installation is needed to view the bundled assessment. The frontend does not contact the Flask API.

## Run from source
Use Node 24 and Python 3.11 or newer. In PowerShell, start in the extracted task3 directory.

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open the URL Vite prints. For the supplied build, run the following from the project root and open http://127.0.0.1:4317/.

```powershell
python -m http.server 4317 --bind 127.0.0.1 --directory frontend/dist
```

## Run the application under review
From the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:CODEGUARD_SECRET = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m flask --app backend.app:create_app seed
.\.venv\Scripts\python -m flask --app backend.app:create_app run --host 127.0.0.1 --port 5000
```

Seed prints randomly generated credentials for new fictional accounts. Run seed once. The API accepts JSON at POST /api/session with name and password. Retain the session cookie. Use the csrf value returned on login in X-CSRF-Token for PATCH /api/profile and DELETE /api/session. GET /api/profile, /api/records?q=notes and /api/records/1 operate in the signed-in user's scope. GET /api/admin/summary requires an administrator. The backend has no HTML homepage.

## Reproduce the assessment
```powershell
.\.venv\Scripts\python audit/run.py
cd frontend
npm ci
npm run build
cd ..
py audit/portable.py
```

The audit executes local source/SQLite checks, isolated handler regressions, Pytest, Bandit and pip-audit. Inspect the timestamp, tool versions, exit codes and stderr in frontend/public/artifacts. Dependency review needs access to an advisory service. Printing the Reports page produces a PDF-friendly assessment. JSON downloads preserve the same snapshot.

## Two-minute submission walkthrough
1. On Overview, let the particles form a symbol. Open Explore Security Audit.
2. Search CG-001. Follow the owner constraint from the baseline query to the secure query and explain the handler regression.
3. Open Security Analysis to show the actual checks and tool availability. Distinguish handler tests from HTTP integration tests.
4. Open Reports and download the canonical evidence. Finish with one decision in the developer lab.

Capture screenshots from your own run at Overview, CG-001 and Reports. Keep the evidence date visible on the report.

## Contents
- frontend/src — React and strict TypeScript, hash navigation, WebGL animation, CSS and ten-question learning lab
- frontend/dist — prebuilt website and offline entry point
- backend — Flask application factory, SQLite initialization and account seeding
- audit — isolated baseline excerpts, scoped review runner and portable build script
- tests — isolated handler, HTTP and browser regressions
- frontend/public/artifacts — canonical JSON, raw tool output and handler test transcript
- SECURITY_AUDIT_REPORT.md — generated assessment
- ARCHITECTURE.md, REQUIREMENTS.md, REMEDIATION_REPORT.md, SECURITY.md, TESTING.md — scope, mapping and reproducibility
