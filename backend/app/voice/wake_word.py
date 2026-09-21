import os
from typing import cast

import openwakeword
import numpy as np
from openwakeword import Model
from openwakeword.utils import download_models


_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        model_path = openwakeword.MODELS["hey_jarvis"]["model_path"].replace(".tflite", ".onnx")
        if not os.path.exists(model_path):
            download_models(["hey_jarvis"])
        _MODEL = Model(["hey_jarvis"], inference_framework="onnx")
    return _MODEL


def detect_wake_word(audio_chunk) -> tuple[bool, dict[str, float]]:
    audio = np.asarray(audio_chunk, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio[:, 0]

    scores = cast(dict[str, float], get_model().predict(audio, timing=False))
    detected = any(float(score) > 0.5 for score in scores.values())
    return detected, scores
