"""Huấn luyện, validation và lưu trọng số student bằng Knowledge Distillation."""

from pathlib import Path

import torch

if __package__:
    from .loss_optimizer import Loss_OP
else:
    from loss_optimizer import Loss_OP


class StudentTrainer:
    def __init__(self, student, teacher, optimizer, scheduler, device,
                 temperature=4.0, alpha=0.5):
        self.student = student.to(device)
        self.teacher = teacher.to(device)
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.temperature = temperature
        self.alpha = alpha

    def train_epoch(self, train_loader):
        """Huấn luyện một epoch, trả về loss trung bình theo batch và accuracy."""
        if len(train_loader) == 0:
            raise ValueError("Tập train phải có dữ liệu.")
        self.student.train()
        self.teacher.eval()
        total_loss = correct = total = 0

        for batch_X, batch_y in train_loader:
            batch_X = batch_X.to(self.device)
            batch_y = batch_y.to(self.device)
            self.optimizer.zero_grad()
            student_logits = self.student(batch_X)
            with torch.no_grad():
                teacher_logits = self.teacher(batch_X)
            loss = Loss_OP.distillation_loss(
                student_logits, teacher_logits, batch_y,
                self.temperature, self.alpha,
            )
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
            correct += (student_logits.argmax(dim=1) == batch_y).sum().item()
            total += batch_y.size(0)

        return total_loss / len(train_loader), correct / total

    def validate(self, val_loader):
        """Đánh giá trên validation, không cập nhật trọng số."""
        if len(val_loader) == 0:
            raise ValueError("Tập validation phải có dữ liệu.")
        self.student.eval()
        self.teacher.eval()
        total_loss = correct = total = 0

        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                student_logits = self.student(batch_X)
                teacher_logits = self.teacher(batch_X)
                loss = Loss_OP.distillation_loss(
                    student_logits, teacher_logits, batch_y,
                    self.temperature, self.alpha,
                )
                total_loss += loss.item()
                correct += (student_logits.argmax(dim=1) == batch_y).sum().item()
                total += batch_y.size(0)

        return total_loss / len(val_loader), correct / total

    def save_model(self, model_path):
        """Lưu state_dict của student vào đường dẫn chỉ định."""
        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.student.state_dict(), model_path)

    def load_model(self, model_path):
        """Nạp trọng số student và chuyển sang chế độ đánh giá."""
        self.student.load_state_dict(torch.load(
            model_path, map_location=self.device, weights_only=True,
        ))
        self.student.eval()

    def fit(self, train_loader, val_loader, epochs=100,
            model_path="best_student.pth", log_interval=10):
        """Train, lưu/nạp lại trọng số tốt nhất; trả về history và best val accuracy."""
        if epochs < 1 or log_interval < 1:
            raise ValueError("epochs và log_interval phải lớn hơn 0.")
        if len(train_loader) == 0 or len(val_loader) == 0:
            raise ValueError("Tập train và validation phải có dữ liệu.")
        best_student_acc = -1.0
        history = {
            "train_loss": [], "train_acc": [],
            "val_loss": [], "val_acc": [],
        }

        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc = self.validate(val_loader)
            history["train_loss"].append(train_loss)
            history["train_acc"].append(train_acc)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)
            self.scheduler.step(val_loss)

            if val_acc > best_student_acc:
                best_student_acc = val_acc
                self.save_model(model_path)

            if (epoch + 1) % log_interval == 0 or epoch + 1 == epochs:
                print(
                    f"Epoch {epoch + 1:3d}/{epochs} | "
                    f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
                    f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
                )

        print(f"\nBest Student Val Accuracy: {best_student_acc:.4f}")
        self.load_model(model_path)
        return history, best_student_acc
