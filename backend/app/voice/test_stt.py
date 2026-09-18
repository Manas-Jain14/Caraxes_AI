import os

from app.ai.gemini import generate_gemini_response
from app.voice.audio import record_audio
from app.voice.speech_to_text import transcribe_audio


def main():
    audio_path = record_audio()
    try:
        print("Transcribing...")
        transcript = transcribe_audio(audio_path)
        print(f"You said: {transcript}")

        if not transcript.strip():
            print("No speech detected. Exiting.")
            return

        print("Sending to Gemini...")
        response = generate_gemini_response(transcript)
        print(f"Gemini response: {response}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    main()
