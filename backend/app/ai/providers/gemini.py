import json
import os

from google import genai
from google.genai import errors, types

from app.ai.providers.base import (
    LLMResponse,
    Message,
    ProviderConfigurationError,
    ProviderRequestError,
    ToolCall,
    ToolDefinition,
)


class GeminiProvider:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")
        if not api_key or not api_key.strip():
            raise ProviderConfigurationError("Missing Gemini API key")
        if not model or not model.strip():
            raise ProviderConfigurationError("Missing Gemini model")

        self._client = genai.Client(api_key=api_key)
        self._model = model.strip()
        self._call_number = 0

    def generate(self, messages: list[Message], tools: list[ToolDefinition]) -> LLMResponse:
        system_instruction = "\n".join(
            message.content or "" for message in messages if message.role == "system"
        )
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=_to_gemini_contents(messages),
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction or None,
                    tools=[_to_gemini_tool(tools)],
                    temperature=0.2,
                ),
            )
        except errors.APIError:
            raise ProviderRequestError(
                "Gemini request failed; verify the API key and model configuration"
            ) from None

        candidate = response.candidates[0] if response.candidates else None
        native_message = candidate.content if candidate else None
        if native_message is None:
            raise ProviderRequestError("Gemini returned an invalid response")

        text_parts = []
        tool_calls = []
        for part in native_message.parts or []:
            if part.text:
                text_parts.append(part.text)
            function_call = part.function_call
            if function_call is not None:
                self._call_number += 1
                tool_calls.append(ToolCall(
                    id=function_call.id or f"gemini-{self._call_number}",
                    name=function_call.name or "",
                    arguments=function_call.args or {},
                ))

        content = "".join(text_parts) or None
        if not tool_calls and not (content and content.strip()):
            raise ProviderRequestError("Gemini returned an empty response")
        return LLMResponse(Message(
            role="assistant",
            content=content,
            tool_calls=tuple(tool_calls),
            provider_data=native_message,
        ))


def _to_gemini_tool(tools: list[ToolDefinition]) -> types.Tool:
    declarations = [
        types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters_json_schema=tool.parameters,
        )
        for tool in tools
    ]
    return types.Tool(function_declarations=declarations)


def _to_gemini_contents(messages: list[Message]) -> list[types.ContentUnionDict]:
    contents: list[types.ContentUnionDict] = []
    index = 0
    while index < len(messages):
        message = messages[index]
        if message.role == "system":
            index += 1
        elif message.role == "assistant" and message.provider_data is not None:
            contents.append(message.provider_data)
            index += 1
        elif message.role == "assistant":
            parts = []
            if message.content:
                parts.append(types.Part(text=message.content))
            parts.extend(
                types.Part(function_call=types.FunctionCall(
                    id=call.id,
                    name=call.name,
                    args=call.arguments if isinstance(call.arguments, dict) else {},
                ))
                for call in message.tool_calls
            )
            contents.append(types.Content(role="model", parts=parts))
            index += 1
        elif message.role == "tool":
            parts = []
            while index < len(messages) and messages[index].role == "tool":
                tool_message = messages[index]
                try:
                    result = json.loads(tool_message.content or "{}")
                except json.JSONDecodeError:
                    result = {"error": "Tool returned invalid JSON"}
                parts.append(types.Part(function_response=types.FunctionResponse(
                    id=tool_message.tool_call_id,
                    name=tool_message.name,
                    response=result if isinstance(result, dict) else {"result": result},
                )))
                index += 1
            contents.append(types.Content(
                role="user",
                parts=parts,
            ))
        else:
            contents.append(types.Content(role="user", parts=[types.Part(text=message.content or "")]))
            index += 1
    return contents
