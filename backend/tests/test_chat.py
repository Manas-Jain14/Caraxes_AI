import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from openai import OpenAIError

from app.ai.nebius import (
    NebiusConfigurationError,
    NebiusRequestError,
    generate_nebius_response,
)
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
        side_effect=NebiusConfigurationError("Missing Nebius API key"),
    )
    def test_chat_reports_missing_provider_configuration(self, _generate_response):
        response = self.client.post("/api/chat", json={"message": "Hello"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Missing Nebius API key"})

    @patch(
        "app.api.chat.generate_agent_response",
        side_effect=NebiusRequestError("Nebius request failed"),
    )
    def test_chat_reports_upstream_failure(self, _generate_response):
        response = self.client.post("/api/chat", json={"message": "Hello"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": "Nebius request failed"})

    def test_chat_rejects_blank_message(self):
        response = self.client.post("/api/chat", json={"message": "  "})

        self.assertEqual(response.status_code, 422)


class NebiusProviderTests(unittest.TestCase):
    @patch.dict("os.environ", {"NEBIUS_API_KEY": "test-key", "NEBIUS_MODEL": "test-model"})
    @patch("app.ai.nebius.OpenAI")
    def test_success_uses_configured_model_and_chat_completions(self, openai):
        openai.return_value.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="  Hello  "))]
        )

        response = generate_nebius_response("Hello")

        self.assertEqual(response, "Hello")
        openai.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.tokenfactory.nebius.com/v1/",
        )
        openai.return_value.chat.completions.create.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.2,
        )

    @patch.dict("os.environ", {"NEBIUS_API_KEY": "", "NEBIUS_MODEL": "test-model"})
    def test_missing_api_key_is_reported(self):
        with self.assertRaisesRegex(NebiusConfigurationError, "API key"):
            generate_nebius_response("Hello")

    @patch.dict("os.environ", {"NEBIUS_API_KEY": "test-key", "NEBIUS_MODEL": " "})
    def test_missing_model_is_reported(self):
        with self.assertRaisesRegex(NebiusConfigurationError, "model"):
            generate_nebius_response("Hello")

    @patch.dict("os.environ", {"NEBIUS_API_KEY": "test-key", "NEBIUS_MODEL": "test-model"})
    @patch("app.ai.nebius.OpenAI")
    def test_failed_request_does_not_expose_provider_details(self, openai):
        openai.return_value.chat.completions.create.side_effect = OpenAIError("secret provider detail")

        with self.assertRaises(NebiusRequestError) as error:
            generate_nebius_response("Hello")

        self.assertNotIn("secret provider detail", str(error.exception))

    @patch.dict("os.environ", {"NEBIUS_API_KEY": "test-key", "NEBIUS_MODEL": "test-model"})
    @patch("app.ai.nebius.OpenAI")
    def test_empty_response_is_reported(self, openai):
        openai.return_value.chat.completions.create.return_value = MagicMock(choices=[])

        with self.assertRaisesRegex(NebiusRequestError, "empty response"):
            generate_nebius_response("Hello")


if __name__ == "__main__":
    unittest.main()
