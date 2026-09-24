import argparse
from pathlib import Path

import numpy as np
import soundfile as sf
from openwakeword.model import Model


def load_audio(path: str) -> np.ndarray:
    data, sample_rate = sf.read(path, dtype="float32", always_2d=False)
    if data.ndim == 2:
        data = data[:, 0]
    if sample_rate != 16000:
        raise ValueError(f"Expected 16 kHz audio, got {sample_rate} Hz")
    return np.asarray(data, dtype=np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a custom openWakeWord ONNX model.")
    parser.add_argument("--model-path", required=True, help="Path to the custom ONNX model.")
    parser.add_argument("--audio-file", required=True, help="Path to a WAV file containing the wake phrase.")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    audio_path = Path(args.audio_file)

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    model = Model(wakeword_models=[str(model_path)], inference_framework="onnx")
    audio = load_audio(str(audio_path))
    prediction = model.predict(audio)

    score = float(next(iter(prediction.values()))) if isinstance(prediction, dict) else float(prediction)
    print(f"Confidence score: {score}")
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Model returned out-of-range score: {score}")


if __name__ == "__main__":
    main()
