"""Access and sanitization regression tests. Test credentials are never deployed."""
import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import time
import tomllib
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest
from access_control import LoginService, password_hash, verify_password, parse_settings, issue_session, valid_session
from dashboard_data import load_data, public_monthly_table
from synthetic_honeybook import tables, validate_demo

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "local-test-password-only-42"
HASH = password_hash(PASSWORD)


def configuration():
    return {"session_minutes": 60, "access_version": "test-version-not-a-live-config",
            "users": {"unit_reviewer": {"password_hash": HASH, "expires_at": "2099-01-01T00:00:00+00:00", "enabled": True}}}


def login_app(app, password=PASSWORD):
    app.text_input[0].set_value("unit_reviewer")
    app.text_input[1].set_value(password)
    app.button[0].click().run(timeout=30)
    return app


def authenticated_app():
    app = AppTest.from_file(str(ROOT / "app.py"))
    app.secrets["review_access"] = configuration()
    app.run(timeout=30)
    return login_app(app)


class AccessChecks(unittest.TestCase):
    def test_account_manager_creates_and_revokes_private_settings(self):
        from tools.manage_access import main
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "secrets.toml"
            args = ["manage_access.py", "add", "--username", "local_reviewer", "--days", "7", "--file", str(path)]
            with patch("sys.argv", args), patch("getpass.getpass", side_effect=[PASSWORD, PASSWORD]), redirect_stdout(io.StringIO()) as output:
                main()
            self.assertNotIn(PASSWORD, output.getvalue())
            self.assertNotIn(PASSWORD, path.read_text())
            config = parse_settings(tomllib.loads(path.read_text())["review_access"])
            self.assertTrue(verify_password(PASSWORD, config.users["local_reviewer"].password_hash))
            self.assertGreater(config.users["local_reviewer"].expires_at, time.time())
            with patch("sys.argv", ["manage_access.py", "revoke", "--username", "local_reviewer", "--file", str(path)]), redirect_stdout(io.StringIO()):
                main()
            self.assertFalse(parse_settings(tomllib.loads(path.read_text())["review_access"]).users["local_reviewer"].enabled)

    def test_hash_verification_and_invalid_settings(self):
        self.assertTrue(verify_password(PASSWORD, HASH))
        self.assertFalse(verify_password("wrong", HASH))
        self.assertFalse(verify_password(PASSWORD, "plaintext"))
        raw = configuration()
        raw["users"]["unit_reviewer"]["expires_at"] = "2099-01-01"
        with self.assertRaises(ValueError):
            parse_settings(raw)
        with self.assertRaises(ValueError):
            parse_settings({})

    def test_expiry_revocation_rotation_and_session_timeout(self):
        raw = configuration()
        settings = parse_settings(raw)
        now = time.time()
        account = settings.users["unit_reviewer"]
        session = issue_session(account, settings, now)
        self.assertTrue(valid_session(session, settings, now))
        self.assertFalse(valid_session(session, settings, now + 3600))
        for field, value in [("enabled", False), ("expires_at", "2000-01-01T00:00:00Z"), ("password_hash", password_hash("a-new-password-for-test"))]:
            updated = copy.deepcopy(raw)
            updated["users"]["unit_reviewer"][field] = value
            self.assertFalse(valid_session(session, parse_settings(updated), now))
        raw["access_version"] = "another-session-version-for-test"
        self.assertFalse(valid_session(session, parse_settings(raw), now))

    def test_bad_credentials_and_throttle_across_requests(self):
        service, settings = LoginService(), parse_settings(configuration())
        now = time.time()
        for _ in range(5):
            self.assertIsNone(service.authenticate("unit_reviewer", "wrong", settings, now)[0])
        self.assertIn("Too many", service.authenticate("unit_reviewer", PASSWORD, settings, now)[1])
        self.assertIsNotNone(service.authenticate("unit_reviewer", PASSWORD, settings, now + 901)[0])
        self.assertIsNone(service.authenticate("unknown", PASSWORD, settings, now)[0])
        for changes in [{"enabled": False}, {"expires_at": "2000-01-01T00:00:00Z"}]:
            raw = configuration()
            raw["users"]["unit_reviewer"].update(changes)
            self.assertIsNone(service.authenticate("unit_reviewer", PASSWORD, parse_settings(raw), now)[0])

    def test_anonymous_does_not_load_data_or_render_download(self):
        app = AppTest.from_file(str(ROOT / "app.py"))
        app.secrets["review_access"] = configuration()
        with patch("dashboard_data.load_data", side_effect=AssertionError("Data accessed before login")) as loader:
            app.run(timeout=30)
            self.assertFalse(app.exception)
            loader.assert_not_called()
        self.assertFalse(app.metric)
        self.assertFalse(app.get("download_button"))
        login_app(app, "incorrect")
        self.assertFalse(app.metric)
        self.assertTrue(app.error)

    def test_missing_or_malformed_secrets_fail_closed(self):
        for raw in [None, {}]:
            app = AppTest.from_file(str(ROOT / "app.py"))
            app.secrets.clear()
            # A nonempty test mapping prevents fallback to local saved accounts.
            app.secrets["__test_isolation__"] = True
            if raw is not None:
                app.secrets["review_access"] = raw
            app.run(timeout=30)
            self.assertFalse(app.exception)
            self.assertFalse(app.metric)
            self.assertFalse(app.get("download_button"))
            self.assertTrue(app.error)

    def test_logout_and_revocation_remove_dashboard(self):
        app = authenticated_app()
        self.assertFalse(app.exception)
        self.assertTrue(app.metric)
        app.button(key="review_logout").click().run(timeout=30)
        self.assertFalse(app.metric)
        self.assertFalse(app.get("download_button"))
        login_app(app)
        self.assertTrue(app.metric)
        raw = configuration()
        raw["users"]["unit_reviewer"]["enabled"] = False
        app.secrets["review_access"] = raw
        app.run(timeout=30)
        self.assertFalse(app.metric)
        self.assertFalse(app.get("download_button"))

    def test_session_timeout_removes_dashboard(self):
        app = authenticated_app()
        app.session_state["_review_access"]["expires_at"] = 0
        app.run(timeout=30)
        self.assertFalse(app.metric)
        self.assertFalse(app.get("download_button"))


class DemoChecks(unittest.TestCase):
    def test_fixture_and_downloads(self):
        frames, _ = load_data()
        validate_demo(frames["metrics"], frames["crm_sources"], frames["payment_methods"])
        for month in ["2026-07", "2026-08"]:
            export = public_monthly_table(frames["metrics"], month)
            hb = export[export.Platform == "HoneyBook"]
            self.assertTrue(hb.Definition.str.startswith("Illustrative HoneyBook data").all())
            self.assertTrue(set(hb.Status) <= {"synthetic", "pending_collection"})
        tampered = frames["metrics"].copy()
        tampered.loc[(tampered.platform == "HoneyBook") & (tampered.metric == "recorded_payment_total"), "value"] = 123456
        with self.assertRaises(AssertionError):
            validate_demo(tampered, frames["crm_sources"], frames["payment_methods"])

    def test_exporter_cannot_import_real_honeybook(self):
        from tools.export_public_data import export, SCHEMAS
        frames, _ = load_data()
        with tempfile.TemporaryDirectory() as temporary:
            source, destination = Path(temporary) / "source", Path(temporary) / "output"
            source.mkdir()
            for output, (input_name, columns) in SCHEMAS.items():
                frame = frames[output.removesuffix(".csv")].copy()
                if output == "metrics.csv":
                    frame.loc[frame.platform == "HoneyBook", "value"] = 987654321
                    frame.loc[frame.platform == "HoneyBook", "scope"] = "REAL_HONEYBOOK_SENTINEL"
                frame[columns].to_csv(source / input_name, index=False)
            # No private CRM source/payment files exist: the exporter must not require them.
            export(source, destination)
            text = (destination / "metrics.csv").read_text()
            self.assertNotIn("REAL_HONEYBOOK_SENTINEL", text)
            self.assertNotIn("987654321", text)
            validate_demo(pd.read_csv(destination / "metrics.csv"), pd.read_csv(destination / "crm_sources.csv"), pd.read_csv(destination / "payment_methods.csv"))


if __name__ == "__main__":
    unittest.main()
