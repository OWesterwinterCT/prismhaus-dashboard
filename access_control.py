"""Small, server-side access control for this single-dashboard review app.

No cookies or URL tokens. Secrets contain salted password hashes, not passwords.
Use a managed identity provider for a production multi-client portal.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
import secrets
import threading
import time

ITERATIONS = 600_000


def password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest.hex()}"


def validate_hash(encoded):
    parts = encoded.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        raise ValueError("Invalid password hash")
    rounds = int(parts[1])
    if not ITERATIONS <= rounds <= 2_000_000:
        raise ValueError("Unsupported hash work factor")
    if len(bytes.fromhex(parts[2])) != 16 or len(bytes.fromhex(parts[3])) != 32:
        raise ValueError("Invalid hash length")
    return parts, rounds


def verify_password(password, encoded):
    try:
        parts, rounds = validate_hash(encoded)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(parts[2]), rounds)
        return hmac.compare_digest(actual.hex(), parts[3])
    except (ValueError, TypeError, AttributeError):
        return False


def utc_timestamp(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Expiry requires a timezone")
    return parsed.astimezone(timezone.utc).timestamp()


@dataclass(frozen=True)
class Account:
    username: str
    password_hash: str
    expires_at: float
    enabled: bool


@dataclass(frozen=True)
class Settings:
    users: dict
    session_minutes: int
    access_version: str

    def fingerprint(self, account):
        fields = [account.username, account.password_hash, account.expires_at,
                  account.enabled, self.session_minutes, self.access_version]
        return hashlib.sha256(json.dumps(fields).encode()).hexdigest()


def parse_settings(raw):
    ttl = raw.get("session_minutes", 60)
    if type(ttl) is not int or not 1 <= ttl <= 480:
        raise ValueError("Session duration must be 1–480 minutes")
    version = raw.get("access_version")
    if not isinstance(version, str) or len(version) < 16:
        raise ValueError("Missing access version")
    users = {}
    for username, config in raw.get("users", {}).items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{2,63}", username):
            raise ValueError("Invalid username")
        encoded = config["password_hash"]
        validate_hash(encoded)
        if type(config.get("enabled")) is not bool:
            raise ValueError("Missing enabled flag")
        users[username] = Account(username, encoded, utc_timestamp(config["expires_at"]), config["enabled"])
    if not users:
        raise ValueError("No accounts configured")
    return Settings(users, ttl, version)


def issue_session(account, settings, now=None):
    now = time.time() if now is None else now
    return {"username": account.username, "fingerprint": settings.fingerprint(account),
            "expires_at": min(account.expires_at, now + settings.session_minutes * 60)}


def valid_session(session, settings, now=None):
    now = time.time() if now is None else now
    if not isinstance(session, dict):
        return False
    account = settings.users.get(session.get("username"))
    return bool(account and account.enabled and now < account.expires_at
                and now < session.get("expires_at", 0)
                and hmac.compare_digest(str(session.get("fingerprint", "")), settings.fingerprint(account)))


class LoginService:
    """Single-process, cross-session throttling. Not a distributed identity service."""
    def __init__(self):
        self.lock = threading.Lock()
        self.failures = {}
        self.dummy_hash = password_hash(secrets.token_urlsafe(32))

    def authenticate(self, username, password, settings, now=None):
        now = time.time() if now is None else now
        username = username.strip().lower()
        account = settings.users.get(username)
        key = username if account else "<unknown>"
        with self.lock:
            # Bound the structure by the configured accounts; restarts reset it.
            self.failures = {k: [t for t in v if t > now - 900]
                             for k, v in self.failures.items() if k in settings.users or k == "<unknown>"}
            recent = self.failures.get(key, [])
            if len(recent) >= 5 or sum(map(len, self.failures.values())) >= 50:
                return None, "Too many attempts. Please try again in 15 minutes."
            encoded = account.password_hash if account else self.dummy_hash
            matches = verify_password(password, encoded)
            if not (matches and account and account.enabled and now < account.expires_at):
                self.failures.setdefault(key, []).append(now)
                return None, "Unable to sign in. Check your details or contact the dashboard owner."
            self.failures.pop(key, None)
            return issue_session(account, settings, now), None
