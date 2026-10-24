import json
import os

from openai import OpenAI, OpenAIError
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)

from app.ai.providers.base import (
    LLMResponse,
    Message,
    ProviderConfigurationError,
    ProviderRequestError,
    ToolCall,
    ToolDefinition,
)


NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"


class NebiusProvider:
    def __init__(self) -> None:
        api_key = os.getenv("NEBIUS_API_KEY")
        model = os.getenv("NEBIUS_MODEL")
        if not api_key or not api_key.strip():
            raise ProviderConfigurationError("Missing Nebius API key")
        if not model or not model.strip():
            raise ProviderConfigurationError("Missing Nebius model")

        self._client = OpenAI(api_key=api_key, base_url=NEBIUS_BASE_URL)
        self._model = model.strip()

    def generate(self, messages: list[Message], tools: list[ToolDefinition]) -> LLMResponse:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[_to_openai_message(message) for message in messages],
                tools=[_to_openai_tool(tool) for tool in tools],
                tool_choice="auto",
                temperature=0.2,
            )
        except OpenAIError:
            raise ProviderRequestError("Nebius request failed; verify the API key and model configuration") from None

        choice = response.choices[0] if response.choices else None
        if choice is None or choice.message is None:
            raise ProviderRequestError("Nebius returned an invalid response")

        native_message = choice.message
        content = native_message.content
        tool_calls = []
        for tool_call in native_message.tool_calls or []:
            if tool_call.type != "function":
                raise ProviderRequestError("Nebius returned an unsupported tool-call type")
            tool_calls.append(ToolCall(
                id=tool_call.id or "",
                name=tool_call.function.name or "",
                arguments=_parse_arguments(tool_call.function.arguments),
            ))
        if not tool_calls and (not content or not content.strip()):
            raise ProviderRequestError("Nebius returned an empty response")

        return LLMResponse(Message(role="assistant", content=content, tool_calls=tuple(tool_calls)))


def _parse_arguments(arguments: object) -> object:
    if isinstance(arguments, dict):
        return arguments
    if not isinstance(arguments, str):
        return None
    try:
        return json.loads(arguments)
    except json.JSONDecodeError:
        return None


def _to_openai_message(message: Message) -> ChatCompletionMessageParam:
    if message.role == "system":
        return {"role": "system", "content": message.content or ""}
    if message.role == "user":
        return {"role": "user", "content": message.content or ""}
    if message.role == "assistant":
        assistant_message: ChatCompletionAssistantMessageParam = {
            "role": "assistant",
            "content": message.content,
        }
        if message.name is not None:
            assistant_message["name"] = message.name
        if message.tool_calls:
            assistant_message["tool_calls"] = [
                ChatCompletionMessageToolCallParam(
                    id=call.id,
                    type="function",
                    function={
                        "name": call.name,
                        "arguments": json.dumps(call.arguments, ensure_ascii=False),
                    },
                )
                for call in message.tool_calls
            ]
        return assistant_message

    tool_message: ChatCompletionToolMessageParam = {
        "role": "tool",
        "tool_call_id": message.tool_call_id or "",
        "content": message.content or "",
    }
    return tool_message


def _to_openai_tool(tool: ToolDefinition) -> ChatCompletionToolParam:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        },
    }
