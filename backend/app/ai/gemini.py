import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def generate_gemini_response(message: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key:
        raise ValueError("Missing Gemini API key")
    if not model:
        raise ValueError("Missing Gemini model")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=message,
        config=types.GenerateContentConfig(temperature=0.2),
    )

    return response.text
