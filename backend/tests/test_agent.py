import json
import unittest
from unittest.mock import MagicMock, patch

from app.ai.agent import MAX_TOOL_ITERATIONS, TOOLS, generate_agent_response
from app.ai.providers import get_provider
from app.ai.providers.base import LLMProvider, LLMResponse, Message, ToolCall


class AgentTests(unittest.TestCase):
    @patch("app.ai.agent.execute_tool", return_value={"content": "Found it"})
    @patch("app.ai.agent.get_provider")
    def test_uses_provider_interface_for_tool_call_flow(self, get_provider_mock, execute_tool):
        provider = MagicMock(spec=LLMProvider)
        provider.generate.side_effect = [
            LLMResponse(Message(
                role="assistant",
                tool_calls=(ToolCall("call-1", "read_file", {"path": "notes/welcome.txt"}),),
            )),
            LLMResponse(Message(role="assistant", content="Here is the file.")),
        ]
        get_provider_mock.return_value = provider

        result = generate_agent_response("Read my note")

        self.assertEqual(result, "Here is the file.")
        get_provider_mock.assert_called_once_with()
        execute_tool.assert_called_once_with("read_file", {"path": "notes/welcome.txt"})
        self.assertEqual(provider.generate.call_args_list[0].args[1], TOOLS)
        second_messages = provider.generate.call_args_list[1].args[0]
        self.assertEqual(json.loads(second_messages[-1].content), {"content": "Found it"})

    @patch("app.ai.agent.get_provider")
    def test_stops_at_tool_iteration_limit(self, get_provider_mock):
        provider = MagicMock(spec=LLMProvider)
        provider.generate.return_value = LLMResponse(Message(
            role="assistant",
            tool_calls=(ToolCall("call-1", "list_directory", {}),),
        ))
        get_provider_mock.return_value = provider

        with patch("app.ai.agent.execute_tool", return_value={"ok": True}) as execute_tool:
            result = generate_agent_response("Keep going")

        self.assertIn("tool-call limit", result)
        self.assertEqual(provider.generate.call_count, MAX_TOOL_ITERATIONS + 1)
        self.assertEqual(execute_tool.call_count, MAX_TOOL_ITERATIONS)

    @patch("app.ai.agent.get_provider")
    def test_non_object_tool_arguments_are_reported_to_provider(self, get_provider_mock):
        provider = MagicMock(spec=LLMProvider)
        provider.generate.side_effect = [
            LLMResponse(Message(
                role="assistant",
                tool_calls=(ToolCall("call-1", "read_file", ["invalid"]),),
            )),
            LLMResponse(Message(role="assistant", content="The tool request was invalid.")),
        ]
        get_provider_mock.return_value = provider

        self.assertEqual(generate_agent_response("Read my note"), "The tool request was invalid.")
        messages = provider.generate.call_args_list[1].args[0]
        self.assertEqual(json.loads(messages[-1].content), {"error": "Tool arguments must contain valid JSON"})

    def test_agent_imports_only_the_provider_factory_interface(self):
        from app.ai import agent

        self.assertIs(agent.get_provider, get_provider)
        self.assertNotIn("NebiusProvider", agent.__dict__)
        self.assertNotIn("GeminiProvider", agent.__dict__)
        self.assertEqual(
            [tool.name for tool in agent.TOOLS],
            ["list_directory", "read_file", "search_files", "write_file"],
        )

    @patch("app.ai.agent.execute_tool", return_value={"success": True, "path": "notes/new.txt"})
    @patch("app.ai.agent.get_provider")
    def test_executes_mocked_write_file_tool_call(self, get_provider_mock, execute_tool):
        provider = MagicMock(spec=LLMProvider)
        provider.generate.side_effect = [
            LLMResponse(Message(
                role="assistant",
                tool_calls=(ToolCall(
                    "call-write",
                    "write_file",
                    {"path": "notes/new.txt", "content": "Hello"},
                ),),
            )),
            LLMResponse(Message(role="assistant", content="The file was written successfully.")),
        ]
        get_provider_mock.return_value = provider

        result = generate_agent_response("Write a note")

        self.assertEqual(result, "The file was written successfully.")
        execute_tool.assert_called_once_with(
            "write_file",
            {"path": "notes/new.txt", "content": "Hello"},
        )
        self.assertEqual(json.loads(provider.generate.call_args_list[1].args[0][-1].content), {
            "success": True,
            "path": "notes/new.txt",
        })


if __name__ == "__main__":
    unittest.main()
