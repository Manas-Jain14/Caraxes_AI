import os

from faster_whisper import WhisperModel


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _MODEL


def transcribe_audio(audio_path: str) -> str:
    if not audio_path or not os.path.exists(audio_path):
        raise ValueError("Invalid audio file")

    model = get_model()
    segments, _ = model.transcribe(audio_path, language=None, beam_size=5)
    text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
    return text.strip()
