"""Điểm chạy huấn luyện và đánh giá MelCNN.

Huấn luyện: python -m models.main
Chỉ đánh giá: python -m models.main --evaluate --model-path pth/best_model.pth
"""

import argparse
from pathlib import Path
import sys
import numpy as np
import torch
from torch.utils.data import DataLoader as TorchDataLoader, TensorDataset

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __package__:
    from .DataLoader import DataLoader
    from .evaluate import ModelEvaluator
    from .load_Data import load_Data
    from .cnn import MelCNN, loss_optimizer
else:
    from DataLoader import DataLoader
    from evaluate import ModelEvaluator
    from load_Data import load_Data
    from cnn import MelCNN, loss_optimizer

from config.config_model_cnn import (
    BATCH_SIZE,
    DROPOUT_RATE,
    EPOCHS,
    LOG_INTERVAL,
    MODEL_PATH,
    NUM_CLASSES,
    PROJECT_ROOT,
)


def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler,
                device, epochs=EPOCHS, model_path=MODEL_PATH, log_interval=LOG_INTERVAL):
    """Huấn luyện, lưu và nạp lại trọng số có accuracy validation cao nhất."""
    if epochs < 1:
        raise ValueError("epochs phải lớn hơn 0.")
    if log_interval < 1:
        raise ValueError("log_interval phải lớn hơn 0.")
    if len(train_loader) == 0 or len(val_loader) == 0:
        raise ValueError("Tập train và validation phải có dữ liệu.")

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model = model.to(device)
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    best_val_acc = -1.0
    print("\n🚀 Bắt đầu huấn luyện...")

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * batch_y.size(0)
            train_total += batch_y.size(0)
            train_correct += (output.argmax(dim=1) == batch_y).sum().item()

        train_loss /= train_total
        train_acc = train_correct / train_total
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                output = model(batch_X)
                loss = criterion(output, batch_y)

                val_loss += loss.item() * batch_y.size(0)
                val_total += batch_y.size(0)
                val_correct += (output.argmax(dim=1) == batch_y).sum().item()

        val_loss /= val_total
        val_acc = val_correct / val_total
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        scheduler.step(val_loss)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)

        if (epoch + 1) % log_interval == 0 or epoch + 1 == epochs:
            print(f"Epoch {epoch + 1:3d}/{epochs} | "
                  f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
                  f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

    print(f"\nBest Validation Accuracy: {best_val_acc:.4f}")
    print(f"Model tốt nhất được lưu tại: {model_path.resolve()}")
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.eval()
    return history, best_val_acc


def prepare_data(data_dir):
    """Chuẩn bị và lưu train/validation/test; chỉ tăng cường tập train."""
    # Nạp Mel-Spectrogram và đưa về kích thước đầu vào của CNN.
    preparation = load_Data()
    X, y = preparation.load_data()
    X = preparation.resize_spectrograms(X)

    # Chia dữ liệu trước khi làm giàu; chỉ làm giàu tập train.
    X_train, X_val, X_test, y_train, y_val, y_test = preparation.split_data(X, y)
    X_train, y_train = preparation.augement_data(X_train, y_train)
    data_dir = preparation.save_data(
        X_train, X_val, X_test, y_train, y_val, y_test,
        output_dir=data_dir,
    )
    return data_dir, preparation.label_encoder.classes_


def main(model_path=MODEL_PATH, evaluate_only=False, data_dir=None):
    """Huấn luyện rồi đánh giá, hoặc chỉ đánh giá trọng số đã có.

    Chế độ đánh giá dùng tập test và ánh xạ nhãn đã lưu, không chia lại dữ liệu.
    """
    model_path = Path(model_path)
    data_dir = Path(data_dir) if data_dir is not None else PROJECT_ROOT / "data" / "data_train"
    if evaluate_only and not model_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy trọng số: {model_path}")

    if evaluate_only:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        class_names = np.load(data_dir / "classes.npy", allow_pickle=False)
        X_test = np.load(data_dir / "X_test.npy", allow_pickle=False)
        y_test = np.load(data_dir / "y_test.npy", allow_pickle=False)
        test_loader = TorchDataLoader(
            TensorDataset(
                torch.as_tensor(X_test, dtype=torch.float32),
                torch.as_tensor(y_test, dtype=torch.long),
            ),
            batch_size=BATCH_SIZE, shuffle=False,
        )
        if len(test_loader) == 0:
            raise ValueError("Tập test phải có dữ liệu.")
    else:
        data_dir, class_names = prepare_data(data_dir)
        data = DataLoader(data_dir=data_dir, batch_size=BATCH_SIZE)
        device = data.device
        test_loader = data.test_loader
        for name, loader in (
            ("Train", data.train_loader),
            ("Val", data.val_loader),
            ("Test", data.test_loader),
        ):
            print(f"{name}: {len(loader.dataset)} mẫu | {len(loader)} batch")

    if len(class_names) != NUM_CLASSES:
        raise ValueError("Số tên lớp không khớp NUM_CLASSES trong cấu hình.")
    print(f"\nDữ liệu: {data_dir.resolve()} | Device: {device}")
    print(f"Ánh xạ nhãn: {dict(enumerate(class_names.tolist()))}")

    model = MelCNN(num_classes=NUM_CLASSES, dropout_rate=DROPOUT_RATE).to(device)
    criterion = torch.nn.CrossEntropyLoss()
    history, best_val_acc = None, None
    if evaluate_only:
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
        print(f"Đánh giá trọng số: {model_path.resolve()}")
    else:
        total_params = sum(parameter.numel() for parameter in model.parameters())
        print(f"CNN parameters: {total_params:,}")
        criterion, optimizer, scheduler = loss_optimizer(model)
        history, best_val_acc = train_model(
            model, data.train_loader, data.val_loader,
            criterion, optimizer, scheduler, device,
            epochs=EPOCHS, model_path=model_path, log_interval=LOG_INTERVAL,
        )

    # Trọng số tốt nhất đã được nạp bởi train_model hoặc từ model_path ở trên.
    test_metrics = ModelEvaluator(
        model=model,
        test_loader=test_loader,
        criterion=criterion,
        device=device,
        class_names=class_names,
    ).evaluate()
    return {
        "model": model,
        "history": history,
        "best_val_acc": best_val_acc,
        "test_metrics": test_metrics,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện và đánh giá MelCNN.")
    parser.add_argument("--evaluate", action="store_true",
                        help="Chỉ đánh giá file .pth, không huấn luyện lại")
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH,
                        help="Đường dẫn lưu hoặc nạp trọng số .pth")
    parser.add_argument("--data-dir", type=Path, default=None,
                        help="Thư mục dữ liệu đã chia (mặc định: data/data_train)")
    args = parser.parse_args()
    main(model_path=args.model_path, evaluate_only=args.evaluate, data_dir=args.data_dir)
