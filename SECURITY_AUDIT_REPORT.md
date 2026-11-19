# CyberShield CodeGuard | Security assessment

CodeAlpha Task 3 • Abdul Waheed

## Executive summary

4 design weaknesses reviewed in the isolated baseline. 0 HTTP regression tests passed in this snapshot.

## Scope and architecture

Authorized local review of fictional team records. Flask routes authenticate sessions and query SQLite. The portfolio consumes a static audit snapshot and has no access to application data.

## Method and severity

Compare source excerpts with corrected handlers, run SQL checks and attempt automated tools. High denotes exposure of protected records or credential material. Medium denotes limited disclosure or integrity impact.

## Findings

### CG-001 • Owner check missing (High)

An authenticated member could receive another member’s record.

audit/baseline.txt:4–4

```python
row = db().execute("SELECT id,title FROM records WHERE id=?", (key,)).fetchone()
```

Scope the database lookup to the current user.

backend/app.py:115–117

```python
        row = db().execute("SELECT id,title FROM records WHERE id=? AND owner=?",
                           (key, session["uid"])).fetchone()
        if row is None:
```

Regression: test_owner_boundary | Verified | CWE-639 | OWASP 2021 A01.

### CG-002 • Private fields in profile response (High)

Returning the full user row would disclose a stored password verifier to the signed-in user.

audit/baseline.txt:6–7

```python
row = db().execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
return jsonify(dict(row))
```

Select the two public profile fields explicitly.

backend/app.py:99–101

```python
        row = db().execute("SELECT display, role FROM users WHERE id=?", (session["uid"],)).fetchone()
        return jsonify(dict(row))

```

Regression: test_profile_projection | Verified | CWE-200 | OWASP 2021 A01.

### CG-003 • Unbounded profile display name (Medium)

Whitespace or oversized names could enter persistent records and disrupt profile rendering.

audit/baseline.txt:9–10

```python
display = body()["display"]
db().execute("UPDATE users SET display=? WHERE id=?", (display, session["uid"]))
```

Validate type and trimmed length before writing.

backend/app.py:95–97

```python
            if not isinstance(display, str) or not 1 <= len(display.strip()) <= 80:
                abort(400)
            db().execute("UPDATE users SET display=? WHERE id=?", (display.strip(), session["uid"]))
```

Regression: test_display_validation | Verified | CWE-20 | OWASP 2021 A04.

### CG-004 • Missing administrator check (Medium)

Any authenticated account could read a restricted aggregate count.

audit/baseline.txt:12–12

```python
return jsonify(records=db().execute("SELECT count(*) FROM records").fetchone()[0])
```

Read the role from the database and deny unauthorized access.

backend/app.py:125–127

```python
        if role["role"] != "admin":
            abort(403)
        return jsonify(records=db().execute("SELECT count(*) FROM records").fetchone()[0])
```

Regression: test_admin_boundary | Verified | CWE-862 | OWASP 2021 A01.

## Verification

4 isolated handler tests passed. See handlers.txt for the individual results.

Owner-scoped detail lookup

Explicit profile response columns

Owner-scoped literal search

## Tools and dependency review

pytest: version unavailable, exit 1. See pytest.json.

bandit: version unavailable, exit 1. See bandit.json.

pip-audit: version unavailable, exit 1. See pip-audit.json.

## Residual risk and limitations

Local demonstration only. HTTPS cookie behavior depends on deployment configuration. Rate limiting, centralized session revocation and independent assessment remain outside this review. Unavailable dependency analysis leaves advisory exposure undetermined.

## Conclusion

Use the regression suite and rerun analysis before release.

## References

https://cwe.mitre.org/ • https://owasp.org/Top10/2021/