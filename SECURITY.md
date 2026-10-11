# Review-app access model

This package implements a temporary, single-dashboard review login. All accounts have the same view. There is no client selector, tenant boundary, role administration, identity verification, MFA, password-reset service or security audit certification.

## Implemented controls

- Fail closed if access configuration is absent or invalid; authenticate before loading any reporting CSV or rendering dashboard controls.
- Salted PBKDF2-HMAC-SHA256 hashes with 600,000 iterations and a random 16-byte salt. Passwords are neither committed nor stored by the account tool. Forms clear submitted credentials.
- Server-side session state, fixed session lifetime (default 60 minutes), mandatory timezone-aware account expiry and explicit enabled/disabled status.
- Recheck the account configuration on each full app execution and every 30 seconds in an active session. Password/version changes invalidate matching sessions. Cloud Secrets changes must be saved and followed by an app reboot.
- Per-account throttling after five failed attempts within 15 minutes, plus a global failure ceiling in the same process. Unknown usernames share a bucket. Hash comparisons are constant-time; unknown users also undergo password hashing.
- Throttling is an in-memory convenience, not durable/distributed attack protection. It resets on restart and attackers can temporarily lock an account. Use a managed identity provider with stronger abuse controls for a production multi-client portal.
- CORS and XSRF protections enabled; static serving disabled. This app uses Community Cloud's HTTPS when deployed there; local development uses localhost HTTP.

## Data boundary

Only HoneyBook data has been replaced. Non-HoneyBook aggregates retain their existing information. The app uses the same independent synthetic HoneyBook fixture in every view, definition and CSV export. It refuses to render if HoneyBook CSVs do not match that fixture. The exporter cannot bring real HoneyBook values into this demo. Code review is still required when modifying the fixture or validator.

App authentication does not protect a public GitHub repository, its history, old deployments, or files already obtained by a viewer. Keep real business data and Secrets out of public repositories. Replacing a financial CSV in a new commit does not erase its old version. Do not treat logout/revocation as deletion of previously delivered charts, downloads, browser content or export links.

## Before real client data

Use managed identity-provider login, explicit per-client authorization, controlled data storage and hosting appropriate to the client's requirements. Review cross-session caches, exports and access logs in that architecture. This review password screen demonstrates the login interaction; it is not proof of production multi-client isolation.
