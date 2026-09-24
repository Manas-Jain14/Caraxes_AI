import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def validate_training_config(config: dict, config_dir: Path) -> dict:
    if not isinstance(config, dict):
        raise ValueError("Training config must be a dictionary.")

    required_fields = [
        "model_name",
        "target_phrase",
        "output_dir",
        "piper_sample_generator_path",
    ]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Training config is missing required field: {field}")

    target_phrase = config["target_phrase"]
    if not isinstance(target_phrase, list) or not target_phrase:
        raise ValueError("Training config field 'target_phrase' must be a non-empty list.")

    output_dir = str(Path(config["output_dir"]).resolve() if Path(config["output_dir"]).is_absolute() else (config_dir / config["output_dir"]).resolve())
    config["output_dir"] = output_dir

    for path_field in ["piper_sample_generator_path"]:
        if path_field in config:
            value = config[path_field]
            if value:
                resolved = (config_dir / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
                config[path_field] = str(resolved)

    for path_field in ["background_paths", "rir_paths"]:
        value = config.get(path_field)
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(f"Training config field '{path_field}' must be a list of paths.")
            resolved_paths = []
            for entry in value:
                resolved_path = (config_dir / str(entry)).resolve() if not Path(str(entry)).is_absolute() else Path(str(entry)).resolve()
                resolved_paths.append(str(resolved_path))
            config[path_field] = resolved_paths

    return config


def ensure_training_directories(config_dir: Path, config: dict) -> None:
    data_dir = config_dir / "data"
    output_dir = Path(config["output_dir"]).resolve()
    for path in [
        data_dir / "background",
        data_dir / "rir",
        data_dir / "validation",
        output_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def run_training(config_path: Path) -> int:
    command = [
        sys.executable,
        "-m",
        "openwakeword.train",
        "--training_config",
        str(config_path),
        "--generate_clips",
        "--augment_clips",
        "--train_model",
    ]
    subprocess.run(command, check=False)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and run the official openWakeWord training pipeline for the Caraxes wake word.")
    parser.add_argument("--config", default="./custom_model.yml", help="Path to the training configuration YAML file.")
    parser.add_argument("--repo-root", default=".", help="Repository root that contains the training workspace.")
    parser.add_argument("--dry-run", action="store_true", help="Validate config and print the training command without executing it.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    default_config = repo_root / "wake_word_training" / "custom_model.yml"
    config_path = (repo_root / args.config).resolve() if args.config != "./custom_model.yml" else default_config

    if not config_path.exists():
        raise FileNotFoundError(f"Training config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    validated = validate_training_config(config, config_path.parent)
    ensure_training_directories(config_path.parent, validated)

    if args.dry_run:
        print(f"Validated config: {config_path}")
        print("Training command:")
        print(" ".join([
            sys.executable,
            "-m",
            "openwakeword.train",
            "--training_config",
            str(config_path),
            "--generate_clips",
            "--augment_clips",
            "--train_model",
        ]))
        return 0

    print(f"Starting custom wake-word training with config: {config_path}")
    return run_training(config_path)


if __name__ == "__main__":
    raise SystemExit(main())
