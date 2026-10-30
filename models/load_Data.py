#=======================================
#file load data và làm giàu dữ liệu qua trình traning
#======================================


import os
from pathlib import Path
import sys
import numpy as np
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

__ROOT_DIR = Path(__file__).parent.parent
if str(__ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(__ROOT_DIR))

from config.config_model_cnn import (
    BASE_PATH,
    FACTOR_RANGE,
    N_MELS,
    NOISE_FACTOR,
    SHIFT_MAX
)

class load_Data:
    """Nạp, xử lý, làm giàu và lưu dữ liệu Mel-Spectrogram."""

    def __init__(self, base_path=BASE_PATH):
        self.base_path = Path(base_path)
        self.label_encoder = LabelEncoder()

    def load_data(self):
        """Nạp dữ liệu, trả về X, y; lưu ánh xạ nhãn trong self.label_encoder."""
        X_list = []
        y_list = []
        for label in ['xanh', 'chin']:
            folder_path = os.path.join(self.base_path, label)
            if not os.path.exists(folder_path):
                print(f"Folder {folder_path} does not exist.")
                continue

            files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]
            for file in files:
                file_path = os.path.join(folder_path, file)
                try:
                    data = np.load(file_path)
                    if data.ndim != 2:
                        continue  # Skip if data is not 2D
                    if data.shape[0] != N_MELS and data.shape[1] != N_MELS:
                        data = data.T  # Transpose if the shape is not (N_MELS, 128):
                    if data.shape[0] == N_MELS:
                        X_list.append(data)
                        y_list.append(label)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        # print(f"Loaded {len(X_list)} samples.")
        # print(f"Class distribution: {Counter(y_list)}")


        # Convert lists to numpy arrays
        X = np.asarray(X_list, dtype=np.float32)
        y = self.label_encoder.fit_transform(y_list)

        # Chuẩn hóa
        X = (X - np.min(X)) / (np.max(X) - np.min(X))
        X= np.expand_dims(X, axis=-1)  # Add channel dimension

        print("\n LOAD COMPLETE!")
        print(f"   - Total samples: {len(X)}")
        print(f"   - X shape: {X.shape}")
        print(f"   - y shape: {y.shape}")

        return X, y

    # hàm resize dữ liệu về kích thước 128 x128
    def resize_spectrograms(self, X, target_size=(N_MELS, N_MELS)):
        X_resized = []
        for x in X:
            if x.ndim == 3:
                x = x.squeeze(-1)  # Remove channel dimension if present
            if x.ndim == 2:
                if x.shape[0] != target_size[0]:
                    x = x.T 
                x_resized = resize(x, target_size, mode='constant', anti_aliasing=True)
                X_resized.append(x_resized)
            else:
                raise ValueError(f"Unexpected shape {x.shape} for spectrogram.")
        X_resized = np.array(X_resized) 
        X_resized = X_resized[:, np.newaxis, :, :]
        return X_resized

    def split_data(self, X, y, random_state=42):
        """Chia dữ liệu train/val/test theo tỷ lệ 70/15/15, giữ tỷ lệ nhãn.

        Gọi trước khi augmentation; chỉ tăng cường dữ liệu của tập train.
        Trả về X_train, X_val, X_test, y_train, y_val, y_test.
        """
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.30, random_state=random_state, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.50,
            random_state=random_state, stratify=y_temp
        )
        return X_train, X_val, X_test, y_train, y_val, y_test

    # Enrichment data augmentation: Resize spectrograms to a target shape 
    def add_noise(self, mel_spec, noise_factor=NOISE_FACTOR):
    # thêm nhiễu gaussian vào spectrogram
        noise = np.random.randn(*mel_spec.shape)* noise_factor
        return mel_spec + noise

    def time_shift(self, mel_spec, shift_max=SHIFT_MAX):
    # dịch chuyển thời gian của spectrogram
        shift = np.random.randint(-shift_max, shift_max)
        return np.roll(mel_spec, shift, axis=1)

    def adjust_brightness(self, mel_spec, factor_range=FACTOR_RANGE):
    # điều chỉnh độ sáng của spectrogram
        factor = np.random.uniform(*factor_range)
        return mel_spec * factor


    def augement_data(self, X, y, random_state=42):
        """Làm giàu nhãn ít mẫu để cân bằng hai nhãn, trả về (X, y).

        X có dạng (N, H, W) hoặc (N, 1, H, W). Chỉ dùng cho tập train.
        """
        X, y = np.asarray(X), np.asarray(y)
        if X.ndim not in (3, 4) or (X.ndim == 4 and X.shape[1] != 1):
            raise ValueError("X phải có dạng (N, H, W) hoặc (N, 1, H, W).")
        if y.ndim != 1 or len(X) != len(y):
            raise ValueError("y phải là mảng 1 chiều có cùng số mẫu với X.")
        labels, counts = np.unique(y, return_counts=True)
        if len(labels) != 2:
            raise ValueError("Cần đủ hai nhãn để cân bằng dữ liệu.")
        target_count = int(counts.max() - counts.min())
        if target_count == 0:
            return X.copy(), y.copy()

        minority_label = labels[np.argmin(counts)]
        X_minority = X[y == minority_label]
        X_aug = []
        current_count = len(X_minority)

        while len(X_aug) < target_count:
            idx = np.random.randint(0, current_count)
            x = X_minority[idx].copy()
            if X.ndim == 4:
                x = x[0]  # Bỏ chiều kênh để time_shift dịch đúng trục thời gian.

            # Randomly choose an augmentation method
            aug_type = np.random.choice(['noise', 'shift', 'brightness', 'combined'])

            if aug_type == 'noise':
                x = self.add_noise(x, noise_factor = np.random.uniform(0.001, 0.01))
            elif aug_type == 'shift':
                x = self.time_shift(x, shift_max = np.random.randint(5,15))
            elif aug_type == 'brightness':
                x = self.adjust_brightness(x, factor_range = (0.8, 1.2))
            else:
                x= self.add_noise(x, 0.001)
                if np.random.rand() > 0.5:
                    x = self.time_shift(x, 10)
                if np.random.rand() > 0.5:
                    x = self.adjust_brightness(x)
            if X.ndim == 4:
                x = x[np.newaxis, :, :]
            X_aug.append(x)

        X_aug = np.asarray(X_aug, dtype=X.dtype)
        y_aug = np.full(target_count, minority_label, dtype=y.dtype)
        X_balanced = np.concatenate([X, X_aug], axis=0)
        y_balanced = np.concatenate([y, y_aug], axis=0)
        indices = np.random.default_rng(random_state).permutation(len(y_balanced))
        return X_balanced[indices], y_balanced[indices]

    # Hàm save data
    def save_data(self, X_train, X_val, X_test, y_train, y_val, y_test,
                  output_dir=None):
        """Lưu các tập dữ liệu và ánh xạ nhãn thành file .npy."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parent.parent / "data" / "data_train"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, values in {
            "X_train": X_train,
            "y_train": y_train,
            "X_val": X_val,
            "y_val": y_val,
            "X_test": X_test,
            "y_test": y_test,
            "classes": self.label_encoder.classes_,
        }.items():
            np.save(output_dir / f"{name}.npy", values)

        print(f"\n SAVE COMPLETE! Dữ liệu đã lưu tại: {output_dir}")
        return output_dir
