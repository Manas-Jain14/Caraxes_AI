import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.ai.agent import MAX_TOOL_ITERATIONS, TOOLS, generate_agent_response


def completion(content=None, tool_calls=None):
    message = MagicMock()
    message.content = content
    message.tool_calls = tool_calls or []
    message.model_dump.return_value = {
        "role": "assistant",
        "content": content,
        "tool_calls": tool_calls,
    }
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def tool_call(name="read_file", arguments='{"path":"notes/welcome.txt"}', call_id="call-1"):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


class AgentTests(unittest.TestCase):
    @patch("app.ai.agent.get_nebius_client_and_model")
    @patch("app.ai.agent.execute_tool", return_value={"content": "Found it"})
    def test_executes_allowlisted_tool_then_returns_model_response(self, execute_tool, get_client):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            completion(tool_calls=[tool_call()]),
            completion(content="Here is the file."),
        ]
        get_client.return_value = (client, "test-model")

        result = generate_agent_response("Read my note")

        self.assertEqual(result, "Here is the file.")
        execute_tool.assert_called_once_with("read_file", {"path": "notes/welcome.txt"})
        first_call = client.chat.completions.create.call_args_list[0]
        self.assertEqual(first_call.kwargs["tools"], TOOLS)
        second_messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
        self.assertEqual(json.loads(second_messages[-1]["content"]), {"content": "Found it"})

    @patch("app.ai.agent.get_nebius_client_and_model")
    def test_stops_at_tool_iteration_limit(self, get_client):
        client = MagicMock()
        client.chat.completions.create.return_value = completion(tool_calls=[tool_call()])
        get_client.return_value = (client, "test-model")

        with patch("app.ai.agent.execute_tool", return_value={"ok": True}) as execute_tool:
            result = generate_agent_response("Keep going")

        self.assertIn("tool-call limit", result)
        self.assertEqual(client.chat.completions.create.call_count, MAX_TOOL_ITERATIONS + 1)
        self.assertEqual(execute_tool.call_count, MAX_TOOL_ITERATIONS)

    @patch("app.ai.agent.get_nebius_client_and_model")
    def test_malformed_json_is_returned_to_model_as_tool_error(self, get_client):
        client = MagicMock()
        client.chat.completions.create.side_effect = [
            completion(tool_calls=[tool_call(arguments="{")]),
            completion(content="The tool request was invalid."),
        ]
        get_client.return_value = (client, "test-model")

        self.assertEqual(generate_agent_response("Read my note"), "The tool request was invalid.")
        messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
        self.assertEqual(json.loads(messages[-1]["content"]), {"error": "Tool arguments must contain valid JSON"})


if __name__ == "__main__":
    unittest.main()
