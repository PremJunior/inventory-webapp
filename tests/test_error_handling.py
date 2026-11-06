import unittest

from app import app, handle_unexpected_error

class ErrorHandlingTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_missing_browser_page_returns_html_404(self):
        response = self.client.get("/homework")

        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)
        self.assertIn(b"Return home", response.data)

    def test_missing_api_route_returns_json_404(self):
        response = self.client.get("/api/random")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["status_code"], 404)
        self.assertIn("not found", response.get_json()["message"].lower())

    def test_api_wrong_method_returns_json_405(self):
        response = self.client.get("/api/login")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.get_json()["status_code"], 405)

    def test_unexpected_api_error_hides_internal_details(self):
        with app.test_request_context("/api/example"):
            response, status_code = handle_unexpected_error(RuntimeError("secret internal detail"))

            self.assertEqual(status_code, 500)
            self.assertEqual(response.get_json()["status_code"], 500)
            self.assertEqual(
                response.get_json()["message"],
                "Something wrong on our side. Please try again later."
            )

    def test_unexpected_browser_error_renders_html(self):
        with app.test_request_context("/example"):
            body, status_code = handle_unexpected_error(
                RuntimeError("secret internal detail")
            )
        response = app.make_response((body, status_code))
        self.assertEqual(status_code, 500)
        self.assertIn(b"Internal Server Error", response.data)
        self.assertNotIn(b"secret internal detail", response.data)


if __name__ == "__main__":
    unittest.main()