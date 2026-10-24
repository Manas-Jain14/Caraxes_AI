from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.ai.agent import generate_agent_response
from app.ai.nebius import (
    NebiusConfigurationError,
    NebiusRequestError,
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be empty")
        return value.strip()


class ChatResponse(BaseModel):
    response: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = generate_agent_response(request.message)
        return ChatResponse(response=response)
    except NebiusConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except NebiusRequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
