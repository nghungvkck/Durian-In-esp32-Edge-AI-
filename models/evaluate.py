"""Các hàm đánh giá mô hình, được gọi từ models/main.py."""

import torch
from sklearn.metrics import classification_report, confusion_matrix


class ModelEvaluator:
    """Đánh giá mô hình với dữ liệu và hàm loss do bên gọi cung cấp."""

    def __init__(self, model, test_loader, criterion, device, class_names):
        self.model = model.to(device)
        self.test_loader = test_loader
        self.criterion = criterion
        self.device = device
        self.class_names = class_names

    def evaluate(self):
        """In và trả về loss, accuracy, precision/recall/F1 và ma trận nhầm lẫn."""
        if len(self.test_loader) == 0:
            raise ValueError("Tập test phải có dữ liệu.")

        self.model.eval()
        test_loss = 0.0
        y_true, y_pred = [], []
        with torch.no_grad():
            for batch_X, batch_y in self.test_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                output = self.model(batch_X)
                test_loss += self.criterion(output, batch_y).item() * batch_y.size(0)
                y_true.extend(batch_y.cpu().tolist())
                y_pred.extend(output.argmax(dim=1).cpu().tolist())

        test_loss /= len(y_true)
        test_acc = sum(true == pred for true, pred in zip(y_true, y_pred)) / len(y_true)
        class_names = [str(name) for name in self.class_names]
        labels = list(range(len(class_names)))
        report = classification_report(
            y_true, y_pred, labels=labels, target_names=class_names,
            output_dict=True, zero_division=0,
        )
        matrix = confusion_matrix(y_true, y_pred, labels=labels)

        print(f"\nTest Loss: {test_loss:.4f} | Test Accuracy: {test_acc:.4f}")
        print(classification_report(
            y_true, y_pred, labels=labels, target_names=class_names,
            digits=4, zero_division=0,
        ))
        print(f"Ma trận nhầm lẫn (hàng: nhãn thật, cột: dự đoán; thứ tự: {class_names}):")
        print(matrix)
        return {
            'test_loss': test_loss,
            'test_acc': test_acc,
            'classification_report': report,
            'confusion_matrix': matrix,
        }
