import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()

NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"


class NebiusConfigurationError(Exception):
    pass


class NebiusRequestError(Exception):
    pass


def generate_nebius_response(message: str) -> str:
    client, model = get_nebius_client_and_model()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            temperature=0.2,
        )
    except OpenAIError:
        raise NebiusRequestError("Nebius request failed; verify the API key and model configuration") from None

    content = response.choices[0].message.content if response.choices else None
    if not content or not content.strip():
        raise NebiusRequestError("Nebius returned an empty response")

    return content.strip()


def get_nebius_client_and_model() -> tuple[OpenAI, str]:
    api_key = os.getenv("NEBIUS_API_KEY")
    model = os.getenv("NEBIUS_MODEL")

    if not api_key or not api_key.strip():
        raise NebiusConfigurationError("Missing Nebius API key")
    if not model or not model.strip():
        raise NebiusConfigurationError("Missing Nebius model")

    return OpenAI(api_key=api_key, base_url=NEBIUS_BASE_URL), model.strip()
