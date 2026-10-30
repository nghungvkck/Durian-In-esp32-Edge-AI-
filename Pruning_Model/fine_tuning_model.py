"""Fine-tune Student sau pruning; không tự chạy khi import."""

from copy import deepcopy

import torch
from torch import nn, optim
from sklearn.metrics import accuracy_score, f1_score, recall_score

from config import config_model_cnn as cfg


class PrunedStudentTrainer:
    def __init__(self, model, device, class_names=None,
                 learning_rate=cfg.PRUNED_LEARNING_RATE,
                 weight_decay=cfg.PRUNED_WEIGHT_DECAY,
                 scheduler_factor=cfg.PRUNED_SCHEDULER_FACTOR,
                 scheduler_patience=cfg.PRUNED_SCHEDULER_PATIENCE):
        self.device = torch.device(device)
        self.model = model.to(self.device)
        self.class_names = list(class_names) if class_names is not None else None
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(
            self.model.parameters(), lr=learning_rate, weight_decay=weight_decay,
        )
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="max", factor=scheduler_factor,
            patience=scheduler_patience,
        )

    def train_epoch(self, train_loader):
        """Train một epoch và trả về loss trung bình theo số mẫu."""
        if len(train_loader) == 0:
            raise ValueError("Tập train phải có dữ liệu.")
        self.model.train()
        total_loss = total = 0
        for images, labels in train_loader:
            images = images.to(self.device)
            labels = labels.to(self.device)
            self.optimizer.zero_grad()
            loss = self.criterion(self.model(images), labels)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item() * labels.size(0)
            total += labels.size(0)
        if total == 0:
            raise ValueError("Tập train phải có dữ liệu.")
        return total_loss / total

    @torch.no_grad()
    def validate(self, val_loader):
        """Tính loss, accuracy, macro F1 và recall từng lớp trên validation."""
        if len(val_loader) == 0:
            raise ValueError("Tập validation phải có dữ liệu.")
        self.model.eval()
        total_loss = total = 0
        predictions, targets = [], []
        num_classes = None
        for images, labels in val_loader:
            images = images.to(self.device)
            labels = labels.to(self.device)
            outputs = self.model(images)
            num_classes = outputs.shape[1]
            total_loss += self.criterion(outputs, labels).item() * labels.size(0)
            total += labels.size(0)
            predictions.extend(outputs.argmax(dim=1).cpu().tolist())
            targets.extend(labels.cpu().tolist())
        if total == 0:
            raise ValueError("Tập validation phải có dữ liệu.")
        if self.class_names is not None and len(self.class_names) != num_classes:
            raise ValueError("Số tên lớp không khớp đầu ra model.")
        labels = list(range(num_classes))
        return {
            "loss": total_loss / total,
            "accuracy": accuracy_score(targets, predictions),
            "macro_f1": f1_score(
                targets, predictions, labels=labels, average="macro", zero_division=0,
            ),
            "recall": recall_score(
                targets, predictions, labels=labels, average=None, zero_division=0,
            ).tolist(),
        }

    def fit(self, train_loader, val_loader, epochs=cfg.PRUNED_FINETUNE_EPOCHS):
        """Fine-tune, khôi phục trọng số có val macro F1 tốt nhất.

        Trả về (history, best_f1). Việc lưu model do main xử lý.
        Mỗi lần gọi fit bắt đầu một lượt chọn trọng số tốt nhất mới.
        """
        if epochs < 1:
            raise ValueError("epochs phải lớn hơn 0.")
        if len(train_loader) == 0 or len(val_loader) == 0:
            raise ValueError("Tập train và validation phải có dữ liệu.")
        history = {
            "train_loss": [], "val_loss": [], "val_acc": [],
            "val_f1": [], "val_recall": [],
        }
        best_f1, best_state = -1.0, None
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            metrics = self.validate(val_loader)
            self.scheduler.step(metrics["macro_f1"])
            history["train_loss"].append(train_loss)
            history["val_loss"].append(metrics["loss"])
            history["val_acc"].append(metrics["accuracy"])
            history["val_f1"].append(metrics["macro_f1"])
            history["val_recall"].append(metrics["recall"])
            if metrics["macro_f1"] > best_f1:
                best_f1 = metrics["macro_f1"]
                best_state = deepcopy(self.model.state_dict())
            print(
                f"Epoch [{epoch + 1:02d}/{epochs}] "
                f"Train Loss: {train_loss:.4f} | Val Loss: {metrics['loss']:.4f} | "
                f"Val Acc: {metrics['accuracy']:.4f} | "
                f"Val Macro F1: {metrics['macro_f1']:.4f}"
            )
        self.model.load_state_dict(best_state)
        self.model.eval()
        return history, best_f1
