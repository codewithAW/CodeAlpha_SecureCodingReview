# Verification record
| Check | Actual result |
|---|---|
| TypeScript strict check and Vite production build | Passed |
| Direct SQLite query checks | 3 passed against queries extracted from backend/app.py |
| Isolated handler regressions | 4 passed using the actual record, admin and profile handler bodies, in-memory SQLite and test doubles for the web framework |
| Chrome desktop | Passed portable-file startup, keyboard skip link, WebGL stage transition, pause control, search, finding detail, comparison and lab persistence |
| Chrome mobile viewport | Seven routes at 390 × 844 passed the horizontal overflow check |
| Accessibility fallbacks | Reduced-motion shield and WebGL-unavailable fallback both passed |
| Browser errors | Zero uncaught page errors during the completed browser suite |
| Flask HTTP integration | Pending. Flask and Pytest were unavailable and the package registry could not be reached |
| Bandit and pip-audit | Unavailable. Exact command output is captured with the snapshot |
| Visual inspection | audit/homepage.png is a real Chrome screenshot of the reduced-motion shield |

## Repeat
Run python tests/offline.py and python audit/run.py from the root. With development requirements installed, run python -m pytest -q tests/test_workspace.py. Eight HTTP tests cover authentication, authorization, profile validation, scoped search, logout, CSRF and selected headers.

Run npm ci and npm run build in frontend. Run python audit/portable.py from the root. In frontend, set BROWSER_PATH to your Chromium executable and run node check-browser.mjs. On Windows with Chrome:

```powershell
$env:BROWSER_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
node check-browser.mjs
```

The completed browser suite tested the standalone production build from disk. The separate tests/browser.py suite targets a live HTTP preview and requires Python Playwright. Loopback HTTP access from this session could not be confirmed. Frame rate, real mobile hardware, screen-reader behavior, and production deployment have not been measured.
