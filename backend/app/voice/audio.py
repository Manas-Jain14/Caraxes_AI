import os
import tempfile

import sounddevice as sd
import soundfile as sf


SAMPLE_RATE = 16000
CHANNELS = 1
DURATION_SECONDS = 20


def record_audio(duration_seconds: int = DURATION_SECONDS, sample_rate: int = SAMPLE_RATE) -> str:
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.close()

    device = os.getenv("AUDIO_INPUT_DEVICE")
    if device is not None:
        try:
            device = int(device)
        except ValueError as exc:
            raise ValueError("AUDIO_INPUT_DEVICE must be an integer device index") from exc

    try:
        print("Listening...")
        record_kwargs = {
            "samplerate": sample_rate,
            "channels": CHANNELS,
            "dtype": "float32",
        }
        if device is not None:
            record_kwargs["device"] = device

        recording = sd.rec(
            int(duration_seconds * sample_rate),
            **record_kwargs,
        )
        sd.wait()

        if recording.size == 0:
            raise ValueError("No audio captured")

        sf.write(temp_file.name, recording, sample_rate)
        return temp_file.name
    except Exception:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise
