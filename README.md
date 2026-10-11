# PrismHaus monthly dashboard — review v2

A login-protected review of July and August 2026. **Only HoneyBook uses synthetic data.** Facebook, Instagram, Squarespace and ClickFunnels retain the original reporting figures. Remaining data collection stays pending.

**Start with [UPDATE_GUIDE.md](UPDATE_GUIDE.md)** for the Windows PowerShell, GitHub and Streamlit steps.

## What's included

- Original reporting sections, period comparison, platform selector, page search and monthly CSV download.
- Independently created HoneyBook leads, source counts, payments, net amounts, fees and payment methods; clearly labelled as illustrative in the app and exports. USD is confirmed.
- The supplied PrismHaus logo, displayed in the top-left sidebar and login screen. The PNG is unchanged; only its empty canvas is excluded from the displayed viewport.
- Username/password login, logout, per-account expiry and revocation, 60-minute sessions by default, and single-process login throttling.
- No working account, plaintext password, original HoneyBook export, or private local secrets file in this package.

## Local setup (Python 3.12)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/manage_access.py add --username reviewer --days 7
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The account tool asks for a password, or generates one if you press Enter. Store the generated password when it is shown. It saves only its salted hash to `.streamlit/secrets.toml`. Open http://localhost:8501 and use the account you created.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_server.py
```

See [VALIDATION.md](VALIDATION.md) for the results from this build and [SECURITY.md](SECURITY.md) for the access model and its limits.

## Data updates

Data remains a manual snapshot. The seven CSVs and `metadata.json` are inside `data/`. Non-HoneyBook values were retained from the original package. See [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

`synthetic_honeybook.py` contains the independent HoneyBook fixture. The app verifies every HoneyBook row against it before rendering the dashboard. Replacing a CSV with real HoneyBook values fails validation. This is an accidental-import safeguard, not a substitute for repository access control or review.

`tools/export_public_data.py` retains its original export interface but discards every source HoneyBook metric and never opens private CRM source or payment files. It injects the synthetic fixture instead. It only supports the two reviewed months; extend the fixture deliberately before adding periods. Keep the private assembly package outside this repository.

## Scope

All reviewer accounts see this same dashboard; multi-client permissions are not implemented. There is no live data connection or automatic account integration. This update does not verify or alter Meta access. Confirmed calls, advertising spend and attribution remain pending. Synthetic HoneyBook figures cannot establish a conversion rate, CPL or ROAS for the original website/social data.

Build identifier shown in the sidebar: **2026-10-11 · Review v2**.
