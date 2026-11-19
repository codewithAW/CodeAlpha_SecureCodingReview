# Security scope
This local project contains fictional team records. Conduct review on the included source and isolated dataset. Keep the API bound to loopback. For HTTPS hosting set CODEGUARD_HTTPS=1 and supply a stable private CODEGUARD_SECRET. The local HTTP setting permits development cookies over loopback.

Reviewed areas include query parameterization, text rendering, record ownership, password hashing, secret generation, CSRF tokens, session settings, input validation, error handling and response headers. JSON response types, case-specific unit checks and manual inspection have different coverage. See TESTING.md for executed checks. Rate limiting, production identity management and session revocation are outside this scope.

Share source locations and expected behavior with the maintainer when reporting a defect. Omit live credentials, private rows and signing keys.
