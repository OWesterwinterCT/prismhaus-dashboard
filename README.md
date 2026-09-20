# PrismHaus monthly dashboard

A public Streamlit dashboard for July and August 2026. It covers social performance, website traffic and actions, CRM lead records, recorded payments, and collection status.

**Status: draft. Remaining collection is pending.** Data is a manual snapshot reviewed on 20 September 2026. The public repository contains aggregate figures only; it requires no API credentials or private exports.

## Run locally

Use Python **3.12**. From the project folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, replace the activation command with `.venv\Scripts\activate` (Command Prompt) or `.venv\Scripts\Activate.ps1` (PowerShell).

Open **http://localhost:8501**. Select July or August in the sidebar and choose a section. August defaults to comparison with July; July has no collected previous month. The download button exports displayed monthly figures with their definitions and status.

## Publish to GitHub and Streamlit

1. Create a **public** GitHub repository named `prismhaus-dashboard`. Upload this project's contents at the repository root, including the `data` folder and `.streamlit/config.toml`. Do not upload the earlier private source-data package.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), sign in, select **Create app**, then **Yup, I have an app**.
3. Select the GitHub repository, branch **main**, and entrypoint **app.py**. In Advanced settings, use **Python 3.12**. No secrets are needed.
4. Choose an available `streamlit.app` address and deploy. Set/verify the app's sharing access is public, then check the link while signed out.

These steps follow the [official Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). Committed updates to the selected branch are picked up by Community Cloud.

If you prefer Git from a local terminal, after creating an empty repository:

```bash
git init -b main
git add app.py dashboard_data.py requirements.txt README.md DATA_DICTIONARY.md VALIDATION.md .gitignore .streamlit data tests tools
git commit -m "Build aggregate monthly reporting dashboard"
git remote add origin https://github.com/OWesterwinterCT/prismhaus-dashboard.git
git push -u origin main
```

Authenticate with your normal GitHub flow. Do not put tokens in code, data files, or the repository URL.

## Validate changes

```bash
python -m unittest discover -s tests -v
python tools/check_server.py
```

The checks reconcile monthly totals, preserve missing values, prevent Instagram/Facebook view double counting, verify the public data boundary, and exercise all dashboard sections and month/platform controls using Streamlit AppTest. AppTest simulates the app; browser layout and deployed sharing should also be checked.

## Update the data

The app reads the seven CSVs and `metadata.json` inside `data/`. It does not call live accounts.

- Edit or replace aggregate rows using the schemas in [DATA_DICTIONARY.md](DATA_DICTIONARY.md).
- Preserve unavailable/pending values as blank numbers with the appropriate status. A missing value is not zero.
- Add new reporting months to `metadata.json` only when each required monthly metric has a row, including explicit pending rows. Run validation before publishing.
- For a rebuild from the separately maintained normalized source package, use `python tools/export_public_data.py /path/to/private-package/data`. The exporter explicitly selects public columns and aggregates payments. Keep that private source package outside the repository.
- Update the snapshot date and coverage descriptions. Commit only reviewed aggregate output, then verify the public app after refresh.

## Interpretation

- Instagram monthly views exclude the Facebook component. Its daily Views export includes Facebook and is labeled accordingly.
- Monthly reach/viewers are approximate. Daily unique audiences are not summed, and audiences are not combined across platforms.
- Website clicks, lead records, and payments are separate measures. No end-to-end conversion rate, CPL, or ROAS is inferred.
- Payment currency is unconfirmed. August includes a 450.00 record flagged as trade. Recorded payment amounts are not independently verified cash receipts or attributed revenue.
- The ClickFunnels figures cover only the Visibility Report funnel. Other funnels, booked calls, paid ads, email data, and cross-platform attribution remain pending.

Detailed access questions and outstanding collection can be briefed separately; they do not block this draft.
