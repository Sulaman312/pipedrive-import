import os
import unittest
from unittest.mock import patch

from src.web import create_app
from src import web_app as compatibility_module


class WebAppStructureTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"APP_USERNAME": "admin", "APP_PASSWORD": "secret"})
        environment.start()
        self.addCleanup(environment.stop)
        self.app = create_app()
        self.app.config.update(TESTING=True)

    def test_existing_paths_and_legacy_endpoints_are_preserved(self):
        expected = {
            "index": "/",
            "upload": "/upload",
            "preview": "/jobs/abc",
            "download": "/jobs/abc/download/V3.xlsx",
            "run_import": "/jobs/abc/import",
            "import_status": "/jobs/abc/import/status",
            "import_result": "/jobs/abc/import/result",
            "login": "/login",
            "logout": "/logout",
        }
        with self.app.test_request_context():
            self.assertEqual(self.app.url_for("index"), expected["index"])
            self.assertEqual(self.app.url_for("upload"), expected["upload"])
            self.assertEqual(self.app.url_for("preview", job_id="abc"), expected["preview"])
            self.assertEqual(
                self.app.url_for("download", job_id="abc", version="V3", extension="xlsx"),
                expected["download"],
            )
            for endpoint in ("run_import", "import_status", "import_result"):
                self.assertEqual(self.app.url_for(endpoint, job_id="abc"), expected[endpoint])
            self.assertEqual(self.app.url_for("login"), expected["login"])
            self.assertEqual(self.app.url_for("logout"), expected["logout"])
        self.assertTrue(callable(compatibility_module.import_v3))
        self.assertTrue(callable(compatibility_module.build_preview))
        self.assertTrue(callable(compatibility_module.run_import))

    def test_authentication_and_index_behavior_are_preserved(self):
        client = self.app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        with client.session_transaction() as session:
            session["authenticated"] = True
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload source file", response.data)

    def test_missing_import_mode_is_rejected(self):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["authenticated"] = True
        response = client.post("/jobs/example/import", data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Import mode is missing or invalid"})

    def test_webhook_path_bypasses_login_redirect(self):
        client = self.app.test_client()
        response = client.post("/webhooks/pipedrive")
        self.assertNotEqual(response.status_code, 302)
        self.assertNotIn("/login", response.headers.get("Location", ""))


if __name__ == "__main__":
    unittest.main()
