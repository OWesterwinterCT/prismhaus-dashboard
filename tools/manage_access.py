"""Create or revoke reviewer accounts locally; then copy Secrets to Streamlit."""
import argparse
from datetime import datetime, timedelta, timezone
import getpass
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from access_control import password_hash, parse_settings


def save_config(path, config):
    """Serialize this app's access section only; refuse to overwrite other secrets."""
    raw = config["review_access"]
    lines = ["# PRIVATE: do not commit this file. Copy it into Streamlit App settings > Secrets.",
             "[review_access]", f"session_minutes = {raw['session_minutes']}",
             f"access_version = {json.dumps(raw['access_version'])}"]
    for username, user in sorted(raw["users"].items()):
        lines += ["", f"[review_access.users.{json.dumps(username)}]",
                  f"password_hash = {json.dumps(user['password_hash'])}",
                  f"expires_at = {json.dumps(user['expires_at'])}",
                  f"enabled = {str(user['enabled']).lower()}"]
    text = "\n".join(lines) + "\n"
    parse_settings(tomllib.loads(text)["review_access"])
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=".access-", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["add", "revoke", "list", "invalidate-sessions"])
    parser.add_argument("--username")
    parser.add_argument("--days", type=int, default=7, help="New/renewed account lifetime (default: 7)")
    parser.add_argument("--session-minutes", type=int, help="Session lifetime, 1–480 minutes (default: 60)")
    parser.add_argument("--file", type=Path, default=ROOT / ".streamlit" / "secrets.toml")
    args = parser.parse_args()
    path = args.file.resolve()
    if path.exists():
        config = tomllib.loads(path.read_text(encoding="utf-8"))
        if set(config) != {"review_access"}:
            parser.error("This file contains other settings. Use a dedicated --file and merge its access section manually.")
        parse_settings(config["review_access"])
    else:
        if args.action != "add":
            parser.error("No local secrets file. Add an account first or copy the deployed Secrets here.")
        config = {"review_access": {"session_minutes": 60, "access_version": secrets.token_hex(24), "users": {}}}
    access = config["review_access"]
    if args.session_minutes is not None:
        if not 1 <= args.session_minutes <= 480:
            parser.error("Session duration must be 1–480 minutes")
        access["session_minutes"] = args.session_minutes
    if args.action == "list":
        for username, user in sorted(access["users"].items()):
            print(f"{username}: enabled={user['enabled']}; expires={user['expires_at']}")
        return
    if args.action in {"add", "revoke"}:
        username = (args.username or "").strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{2,63}", username):
            parser.error("Provide --username with 3–64 letters, digits, dots, underscores or hyphens.")
        if args.action == "revoke":
            if username not in access["users"]:
                parser.error("Username not found")
            access["users"][username]["enabled"] = False
        else:
            if not 1 <= args.days <= 365:
                parser.error("Account lifetime must be 1–365 days")
            if username in access["users"]:
                print("This replaces the account password and renews its expiry.")
            password = getpass.getpass("New password (16+ characters), or Enter to generate one: ")
            generated = not password
            if generated:
                password = secrets.token_urlsafe(24)
            elif len(password) < 16 or len(password) > 256:
                parser.error("Use a password between 16 and 256 characters")
            elif password != getpass.getpass("Repeat new password: "):
                parser.error("Passwords do not match")
            expires = (datetime.now(timezone.utc) + timedelta(days=args.days)).isoformat(timespec="seconds")
            access["users"][username] = {"password_hash": password_hash(password), "expires_at": expires, "enabled": True}
            save_config(path, config)
            print(f"Account: {username}\nExpires (UTC): {expires}")
            if generated:
                print(f"Generated password (save it now): {password}")
            print(f"Private Secrets saved to {path}. Upload the full access section to Streamlit Secrets and reboot the app.")
            return
    else:
        access["access_version"] = secrets.token_hex(24)
    save_config(path, config)
    print(f"Updated {path}. Apply it to Streamlit Secrets and reboot the app to enforce the change.")


if __name__ == "__main__":
    main()
