"""Pipeline nạp Student, pruning, fine-tune và đánh giá trên tập test."""

from pathlib import Path
import random
import sys

import numpy as np
import torch

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config_model_cnn as cfg
from Knowledge_Distillation.cnn_student import MelStudent
from models.DataLoader import DataLoader
from models.evaluate import ModelEvaluator
from Pruning_Model.cnn_pruned import StudentPruner
from Pruning_Model.fine_tuning_model import PrunedStudentTrainer


def load_data(data_dir=cfg.DATA_TRAIN_DIR, batch_size=cfg.BATCH_SIZE, seed=cfg.SEED):
    data = DataLoader(data_dir=data_dir, batch_size=batch_size, seed=seed)
    class_names = np.load(data.data_dir / "classes.npy", allow_pickle=False)
    if len(class_names) != cfg.NUM_CLASSES:
        raise ValueError("Số tên lớp không khớp NUM_CLASSES trong cấu hình.")
    for name, loader in (
        ("Train", data.train_loader), ("Val", data.val_loader), ("Test", data.test_loader),
    ):
        if len(loader) == 0:
            raise ValueError(f"Tập {name} phải có dữ liệu.")
        print(f"{name}: {len(loader.dataset)} mẫu | {len(loader)} batch")
    print(f"Ánh xạ nhãn: {dict(enumerate(class_names.tolist()))}")
    return data, class_names


def load_student(device=None, model_path=cfg.STUDENT_MODEL_PATH):
    """Nạp MelStudent từ pth/model_Student.pth và trả về model trên device."""
    device = torch.device(device if device is not None else
                          ("cuda" if torch.cuda.is_available() else "cpu"))
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = cfg.PROJECT_ROOT / model_path
    if not model_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy trọng số Student: {model_path}")
    student = MelStudent(
        num_classes=cfg.NUM_CLASSES, dropout_rate=cfg.STUDENT_DROPOUT_RATE,
    ).to(device)
    student.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    student.eval()
    print(f"Đã nạp Student: {model_path.resolve()}")
    return student


def compare_parameters(original_model, pruned_model):
    """In và trả về số tham số trước/sau pruning."""
    original_params = sum(p.numel() for p in original_model.parameters())
    pruned_params = sum(p.numel() for p in pruned_model.parameters())
    reduction = (1 - pruned_params / original_params) * 100 if original_params else 0.0
    print(f"Original params   : {original_params:,}")
    print(f"Pruned params     : {pruned_params:,}")
    print(f"Parameter reduction: {reduction:.2f}%")
    return {
        "original_params": original_params,
        "pruned_params": pruned_params,
        "reduction_percent": reduction,
    }


def save_model(model, model_path):
    """Lưu trọng số; khi nạp lại cần dựng đúng kiến trúc của model."""
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = cfg.PROJECT_ROOT / model_path
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)
    print(f"Đã lưu model: {model_path.resolve()}")
    return model_path


def prune_student(student, prune_ratio=cfg.PRUNE_RATIO):
    """Cắt channel và so sánh tham số, không lưu model trung gian."""
    pruned = StudentPruner.structured_pruning(student, prune_ratio=prune_ratio)
    parameter_stats = compare_parameters(student, pruned)
    return pruned, parameter_stats


def fine_tune(pruned_student, data, class_names,
              epochs=cfg.PRUNED_FINETUNE_EPOCHS, model_path=None):
    if model_path is None:
        model_path = cfg.FINETUNED_PRUNED_MODEL_PATH
    trainer = PrunedStudentTrainer(
        pruned_student, data.device, class_names,
        learning_rate=cfg.PRUNED_LEARNING_RATE,
        weight_decay=cfg.PRUNED_WEIGHT_DECAY,
        scheduler_factor=cfg.PRUNED_SCHEDULER_FACTOR,
        scheduler_patience=cfg.PRUNED_SCHEDULER_PATIENCE,
    )
    history, best_f1 = trainer.fit(data.train_loader, data.val_loader, epochs=epochs)
    # fit() đã khôi phục trọng số có validation macro F1 cao nhất.
    save_model(pruned_student, model_path)
    print(f"Best validation macro F1: {best_f1:.4f}")
    return history, best_f1


def evaluate_student(student, data, class_names):
    return ModelEvaluator(
        model=student, test_loader=data.test_loader,
        criterion=torch.nn.CrossEntropyLoss(), device=data.device,
        class_names=class_names,
    ).evaluate()


def main(prune_ratio=cfg.PRUNE_RATIO, epochs=cfg.PRUNED_FINETUNE_EPOCHS):
    random.seed(cfg.SEED)
    np.random.seed(cfg.SEED)
    torch.manual_seed(cfg.SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(cfg.SEED)

    print("\n[1/5] Nạp dữ liệu")
    data, class_names = load_data()
    print("\n[2/5] Nạp Student đã train")
    student = load_student(data.device)
    print(f"\n[3/5] Pruning {prune_ratio:.0%} channel mỗi lớp Conv2d")
    pruned_student, parameter_stats = prune_student(student, prune_ratio=prune_ratio)
    print("\n[4/5] Fine-tune Student sau pruning")
    history, best_f1 = fine_tune(pruned_student, data, class_names, epochs=epochs)
    print("\n[5/5] Đánh giá model tốt nhất trên tập test")
    test_metrics = evaluate_student(pruned_student, data, class_names)
    return {
        "student": pruned_student,
        "parameter_stats": parameter_stats,
        "history": history,
        "best_val_f1": best_f1,
        "test_metrics": test_metrics,
    }


if __name__ == "__main__":
    main()
