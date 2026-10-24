import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from google.genai import types

from app.main import app


def gemini_text_response(text):
    return SimpleNamespace(candidates=[SimpleNamespace(content=types.Content(
        role="model",
        parts=[types.Part(text=text)],
    ))])


class AgentProviderModeTests(unittest.TestCase):
    @patch.dict(os.environ, {
        "LLM_PROVIDER": "nebius",
        "NEBIUS_API_KEY": "test-key",
        "NEBIUS_MODEL": "test-model",
    })
    @patch("app.ai.providers.nebius.OpenAI")
    @patch("app.ai.agent.execute_tool", return_value={"entries": []})
    def test_same_agent_loop_and_chat_route_work_with_nebius(self, execute_tool, openai):
        client = openai.return_value
        client.chat.completions.create.side_effect = [
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
                content=None,
                tool_calls=[SimpleNamespace(
                    id="nebius-call",
                    type="function",
                    function=SimpleNamespace(name="list_directory", arguments='{"path":"."}'),
                )],
            ))]),
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Listed.", tool_calls=[]))]),
        ]

        result = TestClient(app).post("/api/chat", json={"message": "List my workspace"})

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"response": "Listed."})
        execute_tool.assert_called_once_with("list_directory", {"path": "."})
        self.assertEqual(client.chat.completions.create.call_count, 2)

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "gemini",
        "GEMINI_API_KEY": "test-key",
        "GEMINI_MODEL": "test-model",
    })
    @patch("app.ai.providers.gemini.genai.Client")
    @patch("app.ai.agent.execute_tool", return_value={"entries": []})
    def test_same_agent_loop_and_chat_route_work_with_gemini(self, execute_tool, client_factory):
        client = client_factory.return_value
        client.models.generate_content.side_effect = [
            SimpleNamespace(candidates=[SimpleNamespace(content=types.Content(
                role="model",
                parts=[types.Part(function_call=types.FunctionCall(
                    id="gemini-call",
                    name="list_directory",
                    args={"path": "."},
                ))],
            ))]),
            gemini_text_response("Listed."),
        ]

        result = TestClient(app).post("/api/chat", json={"message": "List my workspace"})

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"response": "Listed."})
        execute_tool.assert_called_once_with("list_directory", {"path": "."})
        self.assertEqual(client.models.generate_content.call_count, 2)


if __name__ == "__main__":
    unittest.main()
