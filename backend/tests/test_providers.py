import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from google.genai import types
from openai import OpenAIError

from app.ai.providers import get_provider
from app.ai.providers.base import (
    LLMResponse,
    Message,
    ProviderConfigurationError,
    ProviderRequestError,
    ToolCall,
    ToolDefinition,
)
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.nebius import NEBIUS_BASE_URL, NebiusProvider


TOOL_SCHEMA = [ToolDefinition(
    name="read_file",
    description="Read a UTF-8 text file.",
    parameters={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
        "additionalProperties": False,
    },
)]


def gemini_response(*parts):
    return SimpleNamespace(candidates=[SimpleNamespace(content=types.Content(
        role="model",
        parts=list(parts),
    ))])


class ProviderFactoryTests(unittest.TestCase):
    @patch.dict(os.environ, {
        "LLM_PROVIDER": "nebius",
        "NEBIUS_API_KEY": "test-key",
        "NEBIUS_MODEL": "test-model",
    })
    @patch("app.ai.providers.nebius.OpenAI")
    def test_selects_nebius_provider(self, _openai):
        self.assertIsInstance(get_provider(), NebiusProvider)

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "gemini",
        "GEMINI_API_KEY": "test-key",
        "GEMINI_MODEL": "test-model",
    })
    @patch("app.ai.providers.gemini.genai.Client")
    def test_selects_gemini_provider(self, _client):
        self.assertIsInstance(get_provider(), GeminiProvider)

    @patch.dict(os.environ, {"LLM_PROVIDER": "unsupported"})
    def test_rejects_unsupported_provider(self):
        with self.assertRaisesRegex(ProviderConfigurationError, "Unsupported LLM_PROVIDER"):
            get_provider()

    @patch.dict(os.environ, {"LLM_PROVIDER": ""})
    def test_requires_explicit_provider_selection(self):
        with self.assertRaisesRegex(ProviderConfigurationError, "Missing LLM_PROVIDER"):
            get_provider()


class NebiusProviderTests(unittest.TestCase):
    @patch.dict(os.environ, {"NEBIUS_API_KEY": "test-key", "NEBIUS_MODEL": "test-model"})
    @patch("app.ai.providers.nebius.OpenAI")
    def test_normalizes_tool_call_and_tool_result_messages(self, openai):
        client = openai.return_value
        native_tool_call = SimpleNamespace(
            id="call-1",
            type="function",
            function=SimpleNamespace(name="read_file", arguments='{"path":"notes/a.txt"}'),
        )
        client.chat.completions.create.side_effect = [
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
                content=None,
                tool_calls=[native_tool_call],
            ))]),
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
                content="Done",
                tool_calls=[],
            ))]),
        ]
        provider = NebiusProvider()
        messages = [
            Message(role="system", content="System"),
            Message(role="user", content="Read a file"),
        ]

        first = provider.generate(messages, TOOL_SCHEMA)
        self.assertEqual(first, LLMResponse(Message(
            role="assistant",
            content=None,
            tool_calls=(ToolCall("call-1", "read_file", {"path": "notes/a.txt"}),),
        )))
        second = provider.generate(messages + [
            first.message,
            Message(role="tool", tool_call_id="call-1", name="read_file", content='{"content":"hello"}'),
        ], TOOL_SCHEMA)

        self.assertEqual(second.message.content, "Done")
        openai.assert_called_once_with(api_key="test-key", base_url=NEBIUS_BASE_URL)
        second_request = client.chat.completions.create.call_args_list[1].kwargs
        self.assertEqual(second_request["messages"][-2]["tool_calls"][0]["function"]["arguments"], '{"path": "notes/a.txt"}')
        self.assertEqual(second_request["messages"][-1]["tool_call_id"], "call-1")
        self.assertEqual(json.loads(second_request["messages"][-1]["content"]), {"content": "hello"})
        self.assertEqual(second_request["tools"][0]["function"]["name"], "read_file")

    @patch.dict(os.environ, {"NEBIUS_API_KEY": "", "NEBIUS_MODEL": "test-model"})
    def test_missing_nebius_key_is_a_provider_configuration_error(self):
        with self.assertRaisesRegex(ProviderConfigurationError, "Nebius API key"):
            NebiusProvider()

    @patch.dict(os.environ, {"NEBIUS_API_KEY": "test-key", "NEBIUS_MODEL": "test-model"})
    @patch("app.ai.providers.nebius.OpenAI")
    def test_nebius_api_error_is_normalized(self, openai):
        openai.return_value.chat.completions.create.side_effect = OpenAIError("provider details")
        with self.assertRaisesRegex(ProviderRequestError, "Nebius request failed") as error:
            NebiusProvider().generate([Message(role="user", content="Hello")], [])
        self.assertNotIn("provider details", str(error.exception))


class GeminiProviderTests(unittest.TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"})
    @patch("app.ai.providers.gemini.genai.Client")
    def test_normalizes_function_call_and_function_response_messages(self, client_factory):
        client = client_factory.return_value
        native_message = types.Content(
            role="model",
            parts=[types.Part(function_call=types.FunctionCall(
                id="gemini-call-1",
                name="read_file",
                args={"path": "notes/a.txt"},
            ))],
        )
        client.models.generate_content.side_effect = [
            SimpleNamespace(candidates=[SimpleNamespace(content=native_message)]),
            gemini_response(types.Part(text="Done")),
        ]
        provider = GeminiProvider()
        messages = [
            Message(role="system", content="System instructions"),
            Message(role="user", content="Read a file"),
        ]

        first = provider.generate(messages, TOOL_SCHEMA)
        self.assertEqual(first.message.tool_calls, (
            ToolCall("gemini-call-1", "read_file", {"path": "notes/a.txt"}),
        ))
        second = provider.generate(messages + [
            first.message,
            Message(role="tool", tool_call_id="gemini-call-1", name="read_file", content='{"content":"hello"}'),
            Message(role="tool", tool_call_id="gemini-call-2", name="read_file", content='{"content":"world"}'),
        ], TOOL_SCHEMA)

        self.assertEqual(second.message.content, "Done")
        client_factory.assert_called_once_with(api_key="test-key")
        first_config = client.models.generate_content.call_args_list[0].kwargs["config"]
        self.assertEqual(first_config.system_instruction, "System instructions")
        self.assertEqual(first_config.tools[0].function_declarations[0].name, "read_file")
        second_contents = client.models.generate_content.call_args_list[1].kwargs["contents"]
        self.assertIs(second_contents[1], native_message)
        function_response = second_contents[2].parts[0].function_response
        self.assertEqual(function_response.id, "gemini-call-1")
        self.assertEqual(function_response.response, {"content": "hello"})
        self.assertEqual(second_contents[2].parts[1].function_response.response, {"content": "world"})

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": ""})
    def test_missing_gemini_model_is_a_provider_configuration_error(self):
        with self.assertRaisesRegex(ProviderConfigurationError, "Gemini model"):
            GeminiProvider()


if __name__ == "__main__":
    unittest.main()
