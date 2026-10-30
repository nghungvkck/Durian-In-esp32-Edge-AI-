"""Các bước chuẩn bị và huấn luyện student bằng Knowledge Distillation."""

from pathlib import Path
import sys

import numpy as np
import torch

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.config_model_cnn import (
    BATCH_SIZE,
    DATA_TRAIN_DIR,
    DROPOUT_RATE,
    EPOCHS,
    KD_ALPHA,
    KD_TEMPERATURE,
    LOG_INTERVAL,
    MODEL_PATH,
    NUM_CLASSES,
    SEED,
    STUDENT_DROPOUT_RATE,
    STUDENT_LEARNING_RATE,
    STUDENT_MODEL_PATH,
    STUDENT_SCHEDULER_FACTOR,
    STUDENT_SCHEDULER_PATIENCE,
    STUDENT_WEIGHT_DECAY,
)
from models.DataLoader import DataLoader
from models.cnn import MelCNN
from models.evaluate import ModelEvaluator

if __package__:
    from .cnn_student import MelStudent
    from .loss_optimizer import Loss_OP
    from .train_student import StudentTrainer
else:
    from cnn_student import MelStudent
    from loss_optimizer import Loss_OP
    from train_student import StudentTrainer

#========================================
# lấy data đã được xử lý
#========================================
def load_data(data_dir=None, batch_size=BATCH_SIZE, seed=SEED):
    """Nạp train/validation/test đã lưu sẵn trong data/data_train.

    Trả về đối tượng DataLoader, gồm train_loader, val_loader, test_loader
    và device để dùng ở các bước huấn luyện tiếp theo.
    """
    if data_dir is None:
        data_dir = DATA_TRAIN_DIR

    data = DataLoader(data_dir=data_dir, batch_size=batch_size, seed=seed)
    for name, loader in (
        ("Train", data.train_loader),
        ("Val", data.val_loader),
        ("Test", data.test_loader),
    ):
        print(f"{name}: {len(loader.dataset)} mẫu | {len(loader)} batch")
    return data


def initialize_teacher(device, teacher_path=None, num_classes=NUM_CLASSES):
    """Nạp pth/best_model.pth, chuyển Teacher sang eval và đóng băng tham số."""
    teacher_path = (
        Path(teacher_path) if teacher_path is not None
        else MODEL_PATH
    )
    if not teacher_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy trọng số Teacher: {teacher_path}")

    teacher = MelCNN(num_classes=num_classes, dropout_rate=DROPOUT_RATE).to(device)
    teacher.load_state_dict(torch.load(
        teacher_path, map_location=device, weights_only=True,
    ))
    teacher.eval()
    for param in teacher.parameters():
        param.requires_grad = False
    print(f"Teacher đã nạp và đóng băng: {teacher_path.resolve()}")
    return teacher


def initialize_student(device, num_classes=NUM_CLASSES,
                       dropout_rate=STUDENT_DROPOUT_RATE):
    """Khởi tạo Student và đưa lên cùng device với Teacher."""
    return MelStudent(
        num_classes=num_classes, dropout_rate=dropout_rate,
    ).to(device)


def compare_parameters(teacher, student):
    """So sánh tổng số tham số, bao gồm cả tham số Teacher đã đóng băng."""
    teacher_params = sum(param.numel() for param in teacher.parameters())
    student_params = sum(param.numel() for param in student.parameters())
    reduction_percent = (1 - student_params / teacher_params) * 100

    print(f"Teacher parameters: {teacher_params:,}")
    print(f"Student parameters: {student_params:,}")
    print(f"Parameter reduction: {reduction_percent:.2f}%")
    return {
        "teacher_params": teacher_params,
        "student_params": student_params,
        "reduction_percent": reduction_percent,
    }


def train_student(student, teacher, data, epochs=EPOCHS, model_path=None,
                  temperature=KD_TEMPERATURE, alpha=KD_ALPHA,
                  lr=STUDENT_LEARNING_RATE, weight_decay=STUDENT_WEIGHT_DECAY,
                  log_interval=LOG_INTERVAL,
                  scheduler_factor=STUDENT_SCHEDULER_FACTOR,
                  scheduler_patience=STUDENT_SCHEDULER_PATIENCE):
    """Huấn luyện và lưu Student có val accuracy tốt nhất vào pth/model_Student.pth."""
    model_path = (
        Path(model_path) if model_path is not None
        else STUDENT_MODEL_PATH
    )
    optimizer, scheduler = Loss_OP.create_optimizer(
        student, lr=lr, weight_decay=weight_decay,
        factor=scheduler_factor, patience=scheduler_patience,
    )
    trainer = StudentTrainer(
        student=student,
        teacher=teacher,
        optimizer=optimizer,
        scheduler=scheduler,
        device=data.device,
        temperature=temperature,
        alpha=alpha,
    )
    history, best_val_acc = trainer.fit(
        data.train_loader, data.val_loader,
        epochs=epochs, model_path=model_path, log_interval=log_interval,
    )
    print(f"Student tốt nhất được lưu tại: {model_path.resolve()}")
    return history, best_val_acc


def evaluate_student(student, data):
    """Đánh giá Student tốt nhất trên tập test với ánh xạ nhãn đã lưu."""
    class_names = np.load(data.data_dir / "classes.npy", allow_pickle=False)
    if len(class_names) != NUM_CLASSES:
        raise ValueError("Số tên lớp không khớp NUM_CLASSES trong cấu hình.")
    return ModelEvaluator(
        model=student,
        test_loader=data.test_loader,
        criterion=torch.nn.CrossEntropyLoss(),
        device=data.device,
        class_names=class_names,
    ).evaluate()


def main():
    """Chuẩn bị, huấn luyện, lưu và đánh giá Student tốt nhất trên tập test."""
    data = load_data()
    teacher = initialize_teacher(data.device)
    student = initialize_student(data.device)
    parameter_stats = compare_parameters(teacher, student)
    history, best_val_acc = train_student(student, teacher, data)
    # StudentTrainer.fit đã nạp lại trọng số có validation accuracy tốt nhất.
    test_metrics = evaluate_student(student, data)
    return {
        "data": data,
        "teacher": teacher,
        "student": student,
        "parameter_stats": parameter_stats,
        "history": history,
        "best_val_acc": best_val_acc,
        "test_metrics": test_metrics,
    }


if __name__ == "__main__":
    main()
