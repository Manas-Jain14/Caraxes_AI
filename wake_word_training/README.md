# Phase 3B — Custom Caraxes Wake-Word Model

This workspace contains the training setup for a custom openWakeWord model that recognizes the wake phrase:

Caraxes

This phase is intentionally limited to model creation and validation. It does not activate the assistant or connect wake-word detection to the voice pipeline.

## Official workflow

The current official workflow for custom openWakeWord models is the training utility in the upstream project:

- GitHub: https://github.com/dscripka/openWakeWord
- Training entry point: `openwakeword/train.py`
- Model export: `openwakeword/train.py` exports a trained model as ONNX, and optionally converts it to TFLite when the conversion stack is available.

The upstream docs state that custom models are trained by:

1. generating synthetic positive speech samples for the target phrase,
2. generating adversarial negative samples that resemble the wake phrase or nearby wording,
3. augmenting the clips with noise, room effects, and background audio,
4. training a small model on top of the shared openWakeWord feature extractor,
5. exporting the best checkpoint as a `.onnx` file for runtime use.

This project follows that workflow rather than inventing a custom training algorithm.

## Required environment

Use the same Python environment as the project runtime:

```powershell
cd C:\Users\Manas\Desktop\Caraxes
.\.venv\Scripts\Activate.ps1
```

The current upstream dependency set expects:

- `openwakeword`
- `torch`
- `torchinfo`
- `torchmetrics`
- `yaml`
- `scipy`
- `numpy`
- `onnxruntime` (Windows)

The model-training workflow also needs the synthetic speech generation repository used by openWakeWord:

https://github.com/dscripka/synthetic_speech_dataset_generation

That repository is external to CARAXES and is not committed to this project to keep the repo lightweight.

## Training-only dependency file

A dedicated training dependency file is kept under this workspace:

```text
wake_word_training/requirements-training.txt
```

This file is for offline wake-word training only. It is intentionally separate from the normal CARAXES runtime requirements so the runtime remains lightweight and stable.

The synthetic speech generator used by the official training workflow has its own dependency requirements and should be treated as a separate training-side dependency rather than a runtime dependency.

Installing this file does not train the model or generate data. It only prepares the environment for the upstream training workflow.

## Data layout

The training workspace is intentionally separated from the runtime code under `backend/app/voice/`.

The structure is:

```text
wake_word_training/
├── README.md
├── custom_model.yml
├── validate_custom_model.py
├── data/
│   ├── README.md
│   ├── background/
│   ├── rir/
│   └── validation/
├── models/
│   └── .gitignore
└── synthetic_speech_dataset_generation/   # external checkout, if used locally
```

Do not commit large audio datasets or generated model binaries.

### Positive data

Positive examples must be English audio clips of the target phrase:

- "Caraxes"

The official workflow recommends generating many synthetic speech examples rather than relying on a small hand-recorded dataset. The generated clips are typically mono, 16 kHz, and 1-3 seconds long.

### Negative/background data

Negative data should represent non-target speech, music, environmental noise, and nearby phrases that can trigger false positives.

The workflow uses:

- `background_paths` for ambient/noise recordings,
- `rir_paths` for room impulse response files,
- `custom_negative_phrases` for adversarial near-miss phrases.

The project intentionally does not commit these large datasets.

## Training configuration

The current configuration file is:

```text
wake_word_training/custom_model.yml
```

It follows the official `openwakeword/train.py` format used by the upstream project.

Key fields include:

- `model_name: caraxes`
- `target_phrase: ["Caraxes"]`
- `output_dir: ./models`
- `piper_sample_generator_path: ./synthetic_speech_dataset_generation`
- `background_paths`
- `rir_paths`
- `custom_negative_phrases`
- `n_samples`, `n_samples_val`, `steps`, `model_type`, etc.

## Training command

The repository now includes a small launcher that validates the config and resolves the paths relative to the training workspace:

```powershell
cd C:\Users\Manas\Desktop\Caraxes
.\.venv\Scripts\python.exe .\wake_word_training\train_custom_model.py --repo-root . --dry-run
.\.venv\Scripts\python.exe .\wake_word_training\train_custom_model.py --repo-root .
```

This invokes the official upstream training flow:

```powershell
cd C:\Users\Manas\Desktop\Caraxes\wake_word_training
python -m openwakeword.train --training_config custom_model.yml --generate_clips --augment_clips --train_model
```

If the synthetic speech generator repository is not checked out locally, the command cannot complete. That is a current environment dependency, not a CARAXES-specific code issue.

## Expected output

The expected final artifact is:

```text
wake_word_training/models/caraxes.onnx
```

The upstream script may also create a TFLite output if the conversion toolchain is available.

## Validation

After the model is generated, validate it with:

```powershell
cd C:\Users\Manas\Desktop\Caraxes\wake_word_training
python validate_custom_model.py --model-path .\models\caraxes.onnx --audio-file .\data\validation\caraxes_test.wav
```

The script loads the `.onnx` model via the current openWakeWord runtime and checks that it produces a numeric confidence score between 0 and 1.

## Known compatibility limitations

- The upstream project currently supports English wake words best.
- Custom model training depends on the external synthetic speech generator repository.
- This repository intentionally does not include the full training dataset or generated model files.
- This phase does not implement real-time detection or assistant activation.
- Phase 3C and Phase 3D remain future work.

## Not implemented yet

- Continuous live wake-word detection
- Triggering STT after wake-word activation
- Assistant activation flow
- VAD, TTS, LangGraph, memory, or RAG
- Desktop UI or tool-calling integration
