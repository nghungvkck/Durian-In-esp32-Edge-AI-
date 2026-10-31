
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from esp_ppq.api import espdl_quantize_torch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "data_train"
CHECKPOINT = PROJECT_ROOT / "pth" / "best_pruned_student.pth"
OUTPUT_MODEL = PROJECT_ROOT / "espdl" / "durian_student_pruned.espdl"

DEVICE = "cpu"
TARGET = "esp32s3"
BATCH_SIZE = 8
MAX_CALIB_STEPS = 32


class PrunedMelStudent(nn.Module):
    def __init__(self, state_dict, dropout_rate=0.3):
        super().__init__()

        channels = [
            state_dict[f"features.{i}.weight"].shape[0]
            for i in (0, 4, 8, 12)
        ]
        hidden = state_dict["classifier.0.weight"].shape[0]
        num_classes = state_dict["classifier.3.weight"].shape[0]

        self.features = nn.Sequential(
            nn.Conv2d(1, channels[0], 3, padding=1),
            nn.BatchNorm2d(channels[0]),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(channels[0], channels[1], 3, padding=1),
            nn.BatchNorm2d(channels[1]),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(channels[1], channels[2], 3, padding=1),
            nn.BatchNorm2d(channels[2]),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(channels[2], channels[3], 3, padding=1),
            nn.BatchNorm2d(channels[3]),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        self.classifier = nn.Sequential(
            nn.Linear(channels[3], hidden),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)


def main():
    print("\n[1/5] Checking checkpoint and dataset...")

    if not CHECKPOINT.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT}")

    x_path = DATA_DIR / "X_train.npy"

    if not x_path.is_file():
        raise FileNotFoundError(f"Calibration dataset not found: {x_path}")

    print(f"Checkpoint: {CHECKPOINT}")
    print(f"Dataset: {x_path}")

    print("\n[2/5] Loading pruned model...")

    state_dict = torch.load(
        CHECKPOINT,
        map_location=DEVICE,
        weights_only=True,
    )

    model = PrunedMelStudent(state_dict)
    model.load_state_dict(state_dict, strict=True)
    model.to(DEVICE)
    model.eval()

    channels = [
        state_dict[f"features.{i}.weight"].shape[0]
        for i in (0, 4, 8, 12)
    ]

    print("Model loaded successfully.")
    print(f"Convolution channels: {channels}")

    print("\n[3/5] Preparing calibration data...")

    X = np.load(x_path, allow_pickle=False)

    if X.ndim != 4:
        raise ValueError(
            f"Expected X_train shape [N, 1, H, W], got {X.shape}"
        )

    if X.shape[1] != 1:
        raise ValueError(
            f"Expected 1 input channel, got shape {X.shape}"
        )

    if X.shape[2:] != (128, 128):
        raise ValueError(
            f"Expected input size 128x128, got {X.shape[2:]}"
        )

    if len(X) == 0:
        raise ValueError("Calibration dataset is empty.")

    if not np.isfinite(X).all():
        raise ValueError("Calibration data contains NaN or Inf.")

    X = torch.from_numpy(X.astype(np.float32, copy=False))

    dataset = TensorDataset(X)

    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        drop_last=False,
    )

    calib_steps = min(MAX_CALIB_STEPS, len(dataloader))

    print(f"Input shape: {tuple(X.shape)}")
    print(f"Calibration samples: {len(X)}")
    print(f"Calibration steps: {calib_steps}")

    # Verify the input format before quantization.
    sample_batch = next(iter(dataloader))[0]

    print(f"Test batch shape: {tuple(sample_batch.shape)}")

    if sample_batch.ndim != 4 or sample_batch.shape[1] != 1:
        raise ValueError(
            f"Incorrect batch shape: {tuple(sample_batch.shape)}"
        )

    with torch.no_grad():
        test_output = model(sample_batch[:1])

    print(f"Model output shape: {tuple(test_output.shape)}")

    if test_output.shape[1] != 2:
        raise ValueError(
            f"Expected 2 output classes, got {test_output.shape[1]}"
        )

    print("\n[4/5] Quantizing model to INT8 for ESP32-S3...")

    OUTPUT_MODEL.parent.mkdir(parents=True, exist_ok=True)

    espdl_quantize_torch(
        model=model,
        espdl_export_file=str(OUTPUT_MODEL),
        calib_dataloader=dataloader,
        calib_steps=calib_steps,
        input_shape=[1, *X.shape[1:]],
        target=TARGET,
        quant_type="w8a8",
        device=DEVICE,
        error_report=True,
        export_test_values=True,
        verbose=1,
    )

    print("\n[5/5] Checking exported model...")

    if not OUTPUT_MODEL.is_file():
        raise RuntimeError(
            f"Quantization finished, but model was not found: {OUTPUT_MODEL}"
        )

    print(f"Export successful: {OUTPUT_MODEL}")
    print(f"File size: {OUTPUT_MODEL.stat().st_size / 1024:.2f} KB")
    print("\nDone.")


if __name__ == "__main__":
    main()