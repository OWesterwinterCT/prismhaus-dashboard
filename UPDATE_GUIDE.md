# Update the PrismHaus dashboard

This is a complete replacement application folder, not a patch. You control GitHub commits and Streamlit deployment. Only HoneyBook figures are synthetic; other source data is unchanged. No live app has been modified by producing this package.

## 1. Replace your local project files

1. Unzip the download outside your repository. Open its `prismhaus-dashboard` folder.
2. Back up your existing project outside the repository, especially any private source files.
3. Copy the contents of the new folder into your existing local repository, replacing matching files and including `assets`, `data`, `tests`, `tools`, and `.streamlit`.
4. Preserve your existing `.git` directory. Do not copy any old ZIP, raw exports, old payment data or backup folders back into the updated project.
5. Open PowerShell in the repository root (the folder containing `app.py`). Check the destination before committing:

```powershell
Get-Location
git status --short
git remote -v
```

If the repository was public, actual financial figures may remain in its old Git history even after this update. Restrict repository access before sharing the demo, or use a new clean repository containing only this package. An app password does not protect a public GitHub repository. Restricting access cannot recall copies already downloaded.

## 2. Install the application locally

Use Python 3.12. These commands use the virtual environment directly, so PowerShell activation-policy changes are unnecessary:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Create your login and the temporary reviewer login

```powershell
.\.venv\Scripts\python.exe tools/manage_access.py add --username oliver --days 90
.\.venv\Scripts\python.exe tools/manage_access.py add --username reviewer --days 7
```

For each account, enter a unique password of at least 16 characters and confirm it, or press Enter to generate a random password. Save a generated password immediately; it is displayed once. The tool reports the exact UTC expiry. The account clock starts when you run the command. You can use separate usernames for MacKenzie and her client, which makes individual revocation possible.

Both accounts are viewers of the same dashboard. `oliver` has no special in-app administrative permissions. You administer access through Secrets.

The tool creates `.streamlit/secrets.toml`, containing salted password hashes. This file is excluded from GitHub. The supplied `.streamlit/secrets.example.toml` is deliberately nonfunctional; do not deploy that placeholder as your real configuration. Never place passwords in commands, GitHub, CSVs or this guide.

## 4. Run and test locally

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_server.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501. Check incorrect credentials, successful login, the logo, both months, each section, the monthly CSV, and logout. HoneyBook displays illustrative values; other data retains its existing figures. The app refuses to load dashboard data when credentials are missing or invalid.

## 5. Commit through PowerShell

Review changed files and confirm that the private Secrets file is ignored:

```powershell
git check-ignore .streamlit/secrets.toml
git ls-files .streamlit/secrets.toml
git diff --stat
```

`git check-ignore` should print the secrets path. `git ls-files` should print nothing. If Secrets was previously tracked, remove it from tracking with `git rm --cached .streamlit/secrets.toml`, then rotate exposed credentials; `.gitignore` alone cannot untrack a committed file.

Stage the application explicitly:

```powershell
git add app.py dashboard_data.py access_control.py login.py branding.py synthetic_honeybook.py
git add requirements.txt README.md UPDATE_GUIDE.md SECURITY.md DATA_DICTIONARY.md VALIDATION.md CHANGELOG.md .gitignore
git add .streamlit/config.toml .streamlit/secrets.example.toml assets data tests tools
git diff --cached --stat
git status --short
```

Review the staged changes. Ensure no private Secrets file, raw exports or backup files appear, then:

```powershell
git commit -m "Add reviewer login, synthetic HoneyBook data and PrismHaus logo"
git push
```

Use the branch your existing Streamlit app deploys. `git push` assumes that branch already has its upstream configured, as in your existing deployment.

## 6. Configure Streamlit Secrets and update the app

1. Open https://share.streamlit.io and manage the existing PrismHaus app.
2. Verify the repository, branch and entrypoint (`app.py`). For a new deployment, choose Python 3.12.
3. Open **App settings > Secrets**. Open your local private file with:

```powershell
notepad .streamlit/secrets.toml
```

4. Copy the entire file into the app's Secrets editor and save. If the app already has unrelated Secrets, preserve them and add/replace only the `[review_access]` section and its users.
5. After the code update and Secrets are saved, reboot the app from its management menu. Until valid Secrets are present, the new app displays an access-configuration message and no dashboard data.
6. If using the built-in username/password screen as the access gate, Community Cloud's Sharing visibility can remain public. The URL is public but the app requires the credentials. If you also enable Streamlit's private viewer sharing, the reviewer must pass both access checks.
7. Open the deployed URL in an incognito/private browser window. Verify login, **Build: 2026-10-11 · Review v2**, the logo, synthetic HoneyBook labels, downloads and logout.
8. Share the dashboard URL, reviewer username/password and expiry through your chosen private channel. Share only the reviewer credentials, not the Secrets file.

Community Cloud currently allows one hosting-level private app. Application-level login is separate and can be used in other apps. This package implements the application login; it does not change your hosting visibility or purchase a service.

## 7. Revoke, renew or rotate access

Always work from your current deployed Secrets. If you edited the cloud copy, first update your local private file so an old local configuration does not re-enable another account.

List local accounts without showing hashes or passwords:

```powershell
.\.venv\Scripts\python.exe tools/manage_access.py list
```

Revoke one reviewer:

```powershell
.\.venv\Scripts\python.exe tools/manage_access.py revoke --username reviewer
```

Renew access and assign a new password:

```powershell
.\.venv\Scripts\python.exe tools/manage_access.py add --username reviewer --days 7
```

Invalidate all current sessions while retaining the accounts:

```powershell
.\.venv\Scripts\python.exe tools/manage_access.py invalidate-sessions
```

**After each change, replace the corresponding Streamlit Secrets section, save and reboot.** A local edit alone cannot affect the deployed app. Reboot disconnects active sessions and resets in-memory throttling; users may log back in only if their account remains enabled and unexpired. Data already viewed or downloaded cannot be recalled.

Default session lifetime is 60 minutes. To change it when creating/renewing an account, add `--session-minutes 30`; this changes the setting for all accounts. There is no persistent remember-me cookie. Active sessions recheck expiry every 30 seconds and on normal interactions. An inactive/disconnected browser can retain previously displayed content; it must reconnect before the app can clear that view.

## Official references

- Sharing and private-app limits: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- Secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- App settings: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-settings
- Native identity-provider login for a future production portal: https://docs.streamlit.io/develop/concepts/connections/authentication
