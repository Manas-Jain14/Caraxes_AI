import unittest
from pathlib import Path

from wake_word_training.train_custom_model import validate_training_config


class ValidateTrainingConfigTests(unittest.TestCase):
    def test_validate_training_config_accepts_expected_fields(self):
        config = {
            "model_name": "caraxes",
            "target_phrase": ["Caraxes"],
            "output_dir": "./models",
            "piper_sample_generator_path": "./synthetic_speech_dataset_generation",
            "background_paths": ["./data/background"],
            "rir_paths": ["./data/rir"],
        }

        validated = validate_training_config(config, Path("C:/Users/Manas/Desktop/Caraxes/wake_word_training"))

        self.assertEqual(validated["model_name"], "caraxes")
        self.assertEqual(validated["target_phrase"], ["Caraxes"])
        expected_output_dir = str((Path("C:/Users/Manas/Desktop/Caraxes/wake_word_training") / "models").resolve())
        self.assertEqual(validated["output_dir"], expected_output_dir)

    def test_validate_training_config_rejects_missing_target_phrase(self):
        with self.assertRaisesRegex(ValueError, "target_phrase"):
            validate_training_config({"model_name": "caraxes"}, Path("C:/Users/Manas/Desktop/Caraxes/wake_word_training"))


if __name__ == "__main__":
    unittest.main()
