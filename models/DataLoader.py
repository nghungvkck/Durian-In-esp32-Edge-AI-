from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader as TorchDataLoader, TensorDataset


class DataLoader:
    """Nạp dữ liệu .npy đã chia sẵn để huấn luyện và đánh giá mô hình."""

    def __init__(self, data_dir=None, batch_size=32, seed=42):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data" / "data_train"
        self.data_dir = Path(data_dir)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')     # kiểm tra GPU có trên máy hay ko 
        print(f"✅ Device = {self.device}")

        self.train_dataset = self._load_dataset("train")
        self.val_dataset = self._load_dataset("val")
        self.test_dataset = self._load_dataset("test")

        self.train_loader = TorchDataLoader(
            self.train_dataset, batch_size=batch_size, shuffle=True,
            generator=torch.Generator().manual_seed(seed),
        )
        self.val_loader = TorchDataLoader(
            self.val_dataset, batch_size=batch_size, shuffle=False,
        )
        self.test_loader = TorchDataLoader(
            self.test_dataset, batch_size=batch_size, shuffle=False,
        )

    def _load_dataset(self, split):
        X = np.load(self.data_dir / f"X_{split}.npy", allow_pickle=False)
        y = np.load(self.data_dir / f"y_{split}.npy", allow_pickle=False)
        return TensorDataset(
            torch.as_tensor(X, dtype=torch.float32),
            torch.as_tensor(y, dtype=torch.long),
        )
