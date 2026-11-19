"""Build one evidence snapshot from reviewed source, SQLite checks and tool output."""
import ast
import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend/public/artifacts"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = (ROOT / "backend/app.py").read_text()
LINES = SOURCE.splitlines()
TREE = ast.parse(SOURCE)
BASE = (ROOT / "audit/baseline.txt").read_text()
CASES = [
 ("record","Owner check missing","High",639,"A01","Record detail","An authenticated member could receive another member’s record.","Scope the database lookup to the current user.","WHERE id=? AND owner=?","test_owner_boundary"),
 ("profile","Private fields in profile response","High",200,"A01","Profile response","Returning the full user row would disclose a stored password verifier to the signed-in user.","Select the two public profile fields explicitly.","SELECT display, role","test_profile_projection"),
 ("display","Unbounded profile display name","Medium",20,"A04","Profile update","Whitespace or oversized names could enter persistent records and disrupt profile rendering.","Validate type and trimmed length before writing.","not 1 <= len","test_display_validation"),
 ("admin","Missing administrator check","Medium",862,"A01","Administrative summary","Any authenticated account could read a restricted aggregate count.","Read the role from the database and deny unauthorized access.",'if role["role"]',"test_admin_boundary")
]


def tool(name, args):
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        version = None
    try:
        result = subprocess.run([sys.executable,"-m",*args],cwd=ROOT,capture_output=True,text=True,timeout=90)
        data = {"version":version,"exit":result.returncode,"stdout":result.stdout,"stderr":result.stderr}
    except subprocess.TimeoutExpired:
        data = {"version":version,"exit":None,"stderr":"Timeout after 90 seconds","stdout":""}
    return data


def sqlite_checks():
    queries = [n.value for n in ast.walk(TREE) if isinstance(n, ast.Constant) and isinstance(n.value,str)]
    with sqlite3.connect(":memory:") as db:
        db.executescript(next(q for q in queries if "CREATE TABLE IF NOT EXISTS users" in q))
        db.execute("INSERT INTO records VALUES(1,1,'Review')")
        db.execute("INSERT INTO users VALUES(1,'fern','synthetic','member','Fern')")
        query = next(q for q in queries if "WHERE id=? AND owner=?" in q)
        assert db.execute(query,(1,1)).fetchone() == (1,"Review")
        assert db.execute(query,(1,2)).fetchone() is None
        profile = db.execute(next(q for q in queries if q.startswith("SELECT display, role")), (1,))
        assert [c[0] for c in profile.description] == ["display","role"]
        search = next(q for q in queries if "instr(lower(title)" in q)
        assert db.execute(search,(1,"view")).fetchall() == [(1,"Review")]
        assert db.execute(search,(2,"view")).fetchall() == []
    return ["Owner-scoped detail lookup","Explicit profile response columns","Owner-scoped literal search"]


def main():
    checks = sqlite_checks()
    junit = OUT / "pytest.xml"
    junit.unlink(missing_ok=True)
    tools = {"pytest":tool("pytest",["pytest","-q","tests/test_workspace.py","--junitxml",str(junit)]),
             "bandit":tool("bandit",["bandit","-r","backend","-f","json"]),
             "pip-audit":tool("pip-audit",["pip_audit","-r","backend/requirements.txt","-f","json"])}
    offline = subprocess.run([sys.executable, "tests/offline.py"], cwd=ROOT, capture_output=True, text=True)
    (OUT / "handlers.txt").write_text(offline.stderr)
    handler_passed = [line.split()[0] for line in offline.stderr.splitlines() if line.startswith("test_") and line.endswith(" ... ok")]
    passed = []
    if junit.exists():
        passed = [c.get("name") for c in ET.parse(junit).iter("testcase") if len(c)==0]
    for name,data in tools.items():
        (OUT / (name+".json")).write_text(json.dumps(data,indent=2))
    findings = []
    for i,(key,title,sev,cwe,owasp,area,impact,fix,needle,test) in enumerate(CASES,1):
        before = BASE.split("["+key+"]\n")[1].split("\n[")[0].strip()
        n = next(i for i,s in enumerate(LINES) if needle in s)
        begin = BASE[:BASE.index(before)].count("\n")+1
        findings.append(dict(id=f"CG-{i:03}",title=title,severity=sev,cwe=cwe,owasp=owasp,
            area=area,impact=impact,fix=fix,before=before,after="\n".join(LINES[n:n+3]),
            source=f"backend/app.py:{n+1}–{n+3}",baseline=f"audit/baseline.txt:{begin}–{begin+len(before.splitlines())-1}",
            test=test,status="Verified" if test in passed or test in handler_passed else "Remediated",method="Manual review"))
    snap=dict(date=dt.datetime.now(dt.timezone.utc).isoformat(),sha256=hashlib.sha256(SOURCE.encode()).hexdigest(),
              findings=findings,handlerPassed=handler_passed,checks=checks,passed=passed,tools=tools)
    (OUT/"audit.json").write_text(json.dumps(snap,indent=2,ensure_ascii=False),encoding="utf-8")
    report = ["# CyberShield CodeGuard | Security assessment","CodeAlpha Task 3 • Abdul Waheed",
        "## Executive summary",f"{len(findings)} design weaknesses reviewed in the isolated baseline. "
        f"{len(passed)} HTTP regression tests passed in this snapshot.","## Scope and architecture",
        "Authorized local review of fictional team records. Flask routes authenticate sessions and query SQLite. "
        "The portfolio consumes a static audit snapshot and has no access to application data.",
        "## Method and severity","Compare source excerpts with corrected handlers, run SQL checks and attempt automated tools. "
        "High denotes exposure of protected records or credential material. Medium denotes limited disclosure or integrity impact.",
        "## Findings"]
    for f in findings:
        report += [f"### {f['id']} • {f['title']} ({f['severity']})",f["impact"],f["baseline"],
                   "```python\n"+f["before"]+"\n```",f["fix"],f["source"],"```python\n"+f["after"]+"\n```",
                   f"Regression: {f['test']} | {f['status']} | CWE-{f['cwe']} | OWASP 2021 {f['owasp']}."]
    report += ["## Verification",f"{len(handler_passed)} isolated handler tests passed. See handlers.txt for the individual results.",*checks,"## Tools and dependency review",
               *[f"{k}: version {v['version'] or 'unavailable'}, exit {v['exit']}. See {k}.json." for k,v in tools.items()],
               "## Residual risk and limitations","Local demonstration only. HTTPS cookie behavior depends on deployment configuration. "
               "Rate limiting, centralized session revocation and independent assessment remain outside this review. "
               "Unavailable dependency analysis leaves advisory exposure undetermined.",
               "## Conclusion","Use the regression suite and rerun analysis before release.",
               "## References","https://cwe.mitre.org/ • https://owasp.org/Top10/2021/"]
    (ROOT/"SECURITY_AUDIT_REPORT.md").write_text("\n\n".join(report),encoding="utf-8")
    print(f"{len(findings)} findings, {len(checks)} SQLite checks, {len(passed)} HTTP tests passed.")


if __name__ == "__main__":
    main()
