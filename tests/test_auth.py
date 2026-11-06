import unittest

from app import app

class protectedApiTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_items_api_allows_logged_in_user(self):
        with self.client.session_transaction() as session:
            session["logged_in"] = True
            session["username"] = "test-user"

        response = self.client.get("/api/items")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_items_api_requires_login(self):
        response = self.client.get("/api/items")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"message" : "please login"}
        )

if __name__ == "__main__":
    unittest.main()