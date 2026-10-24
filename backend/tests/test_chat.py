import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.ai.providers.base import ProviderConfigurationError, ProviderRequestError
from app.main import app


class ChatApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("app.api.chat.generate_agent_response", return_value="Hello from Nemotron")
    def test_chat_preserves_response_contract(self, generate_response):
        response = self.client.post("/api/chat", json={"message": "Hello"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Hello from Nemotron"})
        generate_response.assert_called_once_with("Hello")

    @patch(
        "app.api.chat.generate_agent_response",
        side_effect=ProviderConfigurationError("Missing Nebius API key"),
    )
    def test_chat_reports_missing_provider_configuration(self, _generate_response):
        response = self.client.post("/api/chat", json={"message": "Hello"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Missing Nebius API key"})

    @patch(
        "app.api.chat.generate_agent_response",
        side_effect=ProviderRequestError("Nebius request failed"),
    )
    def test_chat_reports_upstream_failure(self, _generate_response):
        response = self.client.post("/api/chat", json={"message": "Hello"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": "Nebius request failed"})

    def test_chat_rejects_blank_message(self):
        response = self.client.post("/api/chat", json={"message": "  "})

        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
