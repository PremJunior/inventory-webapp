import unittest

from app import app


class AdminAccessTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def login_as(self, username):
        with self.client.session_transaction() as session:
            session["logged_in"] = True
            session["username"] = username

    def test_admin_page_redirects_anonymous_user(self):
        response = self.client.get("/admin")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_admin_api_returns_json_for_anonymous_user(self):
        response = self.client.get("/api/admin/users")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"message": "please login"}
        )

    def test_admin_api_rejects_non_admin_user(self):
        self.login_as("not-a-real-admin")

        response = self.client.get("/api/admin/users")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json(),
            {"message": "admin only"}
        )


if __name__ == "__main__":
    unittest.main()