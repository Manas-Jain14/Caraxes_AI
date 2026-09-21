import sounddevice as sd

from app.voice.wake_word import detect_wake_word, get_model


SAMPLE_RATE = 16000
DURATION_SECONDS = 1


def main():
    print("Import check: openWakeWord imports successfully.")
    print("Loading model...")
    model = get_model()
    print("Model loaded successfully:", model)

    print("Recording audio...")
    audio = sd.rec(int(DURATION_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    print("Audio captured: shape=", audio.shape, "dtype=", audio.dtype)

    detected, scores = detect_wake_word(audio)
    print("Wake word detected:", detected)
    print("Detection scores:", scores)


if __name__ == "__main__":
    main()
