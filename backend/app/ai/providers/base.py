from dataclasses import dataclass, field
from typing import Any, Literal, Protocol


class ProviderConfigurationError(Exception):
    pass


class ProviderRequestError(Exception):
    pass


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: object


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    tool_call_id: str | None = None
    name: str | None = None
    provider_data: Any = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class LLMResponse:
    message: Message


class LLMProvider(Protocol):
    def generate(self, messages: list[Message], tools: list[ToolDefinition]) -> LLMResponse:
        ...
