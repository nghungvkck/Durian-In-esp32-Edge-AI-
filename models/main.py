from pathlib import Path

import torch

if __package__:
    from .DataLoader import DataLoader
    from .load_Data import load_Data
    from .cnn import MelCNN, loss_optimizer
else:
    from DataLoader import DataLoader
    from load_Data import load_Data
    from cnn import MelCNN, loss_optimizer

from config.config_model_cnn import (
    BATCH_SIZE,
    DROPOUT_RATE,
    EPOCHS,
    LOG_INTERVAL,
    MODEL_PATH,
    NUM_CLASSES,
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


def main():
    # Nạp Mel-Spectrogram và đưa về kích thước đầu vào của CNN.
    preparation = load_Data()
    X, y = preparation.load_data()
    X = preparation.resize_spectrograms(X)

    # Chia dữ liệu trước khi làm giàu; chỉ làm giàu tập train.
    X_train, X_val, X_test, y_train, y_val, y_test = preparation.split_data(X, y)
    X_train, y_train = preparation.augement_data(X_train, y_train)
    data_dir = preparation.save_data(
        X_train, X_val, X_test, y_train, y_val, y_test,
    )

    # Đọc các tập đã lưu và tạo batch cho train/val/test.
    data = DataLoader(data_dir=data_dir, batch_size=BATCH_SIZE)
    print(f"\nDữ liệu được nạp từ: {data.data_dir}")

    for name, loader in (
        ("Train", data.train_loader),
        ("Val", data.val_loader),
        ("Test", data.test_loader),
    ):
        X, y = loader.dataset.tensors
        print(f"\n{name}: {len(loader.dataset)} mẫu | {len(loader)} batch")
        print(f"   - X: shape={tuple(X.shape)}, dtype={X.dtype}")
        print(f"   - y: shape={tuple(y.shape)}, dtype={y.dtype}")

    # Khởi tạo mô hình CNN và chuyển sang thiết bị đang sử dụng.
    model = MelCNN(num_classes=NUM_CLASSES, dropout_rate=DROPOUT_RATE).to(data.device)
    total_params = sum(parameter.numel() for parameter in model.parameters())
    trainable_params = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    print(f"\nCNN parameters: {total_params:,} | Trainable: {trainable_params:,}")
    criterion, optimizer, scheduler = loss_optimizer(model)
    history, best_val_acc = train_model(
        model, data.train_loader, data.val_loader,
        criterion, optimizer, scheduler, data.device,
        epochs=EPOCHS, model_path=MODEL_PATH, log_interval=LOG_INTERVAL,
    )

    return model, history, best_val_acc


if __name__ == "__main__":
    main()
