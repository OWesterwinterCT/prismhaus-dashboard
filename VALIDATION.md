# Validation record — Review v2

Checked locally on **11 October 2026** with Python 3.12, Streamlit 1.55.0, pandas 2.2.3 and Plotly 6.5.0.

| Check | Result |
| --- | --- |
| 16 automated tests (unittest and Streamlit AppTest) | Passed |
| Both reporting months across all five sections; Instagram/Facebook selection and comparison controls | Passed |
| Anonymous, missing/malformed configuration and wrong-password access | No dashboard data or download control exposed |
| Password verification, account expiry, disabled accounts, password/version rotation and session timeout | Passed |
| Cross-request login throttling | Passed |
| Local account-tool creation and revocation | Passed; only password hashes written |
| Logout and active-session revocation | Dashboard and download control removed |
| Synthetic HoneyBook source counts, payment counts, amounts, net amounts and fees | Reconcile |
| Non-HoneyBook metric rows | Exact parsed equality with original package |
| Social daily, website source, website page and website button CSV files | Byte-identical to original package |
| Other source coverage entries and uploaded logo | Preserved; logo bytes identical |
| Old HoneyBook financial amounts and business-specific notes in release source/data/docs | Removed |
| Exporter presented with sentinel private HoneyBook values | Discarded them; emitted only independent synthetic fixture |
| Pending values and approximate audience comparison rules | Preserved |
| Local HTTP application shell and health endpoint | HTTP 200 |
| Headless Chromium browser: wrong password, successful login, overview/payments, CSV download, logout, fresh-tab gate | Passed |
| Visual review of login, overview and payments screenshots | Logo and layouts reviewed locally |

The browser downloaded the August CSV and verified that every HoneyBook row is labelled illustrative, with synthetic or pending status. Other data uses the original sources. Synthetic data and authentication checks are reproducible with the included tests. The one-time original-file comparison used the prior source ZIP; that ZIP is intentionally not included in this release.

The logo PNG was not edited. The UI displays its nonempty region using an SVG viewport.

## Reproduce the included checks

```powershell
python -m unittest discover -s tests -v
python tools/check_server.py
```

Run these from the project root after installing `requirements.txt`. Browser rendering was additionally checked during packaging; Playwright is not required to run or deploy the dashboard.

## Deployment still to be checked by the owner

No GitHub push, Streamlit Secrets change, hosting visibility change or live deployment was performed. After deploying, verify the build identifier, account expiry/revocation, private-browser login and downloaded CSV as described in `UPDATE_GUIDE.md`. These checks do not constitute a penetration test or certify multi-client isolation.
