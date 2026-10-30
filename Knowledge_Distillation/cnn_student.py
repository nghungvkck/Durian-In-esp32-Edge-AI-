"""Kiến trúc student và lớp điều phối huấn luyện Knowledge Distillation."""

from pathlib import Path

import torch 
from torch import nn

if __package__:
    from .loss_optimizer import Loss_OP
    from .train_student import StudentTrainer
else:
    from loss_optimizer import Loss_OP
    from train_student import StudentTrainer

class MelStudent(nn.Module):
    def __init__(self, num_classes=2, dropout_rate=0.3):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(1, 24, 3, padding=1),
            nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(24, 48, 3, padding=1),
            nn.BatchNorm2d(48),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(48, 96, 3, padding=1),
            nn.BatchNorm2d(96),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(96, 192, 3, padding=1),
            nn.BatchNorm2d(192),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )

        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        self.classifier = nn.Sequential(
            nn.Linear(192, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x


class KnowledgeDistillation:
    """Chuẩn bị teacher/student và huấn luyện khi gọi train()."""

    def __init__(self, device, teacher_path=None, num_classes=2,
                 dropout_rate=0.3, temperature=4.0, alpha=0.5,
                 lr=0.001, weight_decay=1e-4):
        from config.config_model_cnn import MODEL_PATH

        teacher_path = Path(teacher_path) if teacher_path is not None else MODEL_PATH
        if not teacher_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy trọng số teacher: {teacher_path}")

        from models.cnn import MelCNN

        self.device = torch.device(device)
        self.teacher = MelCNN(num_classes=num_classes).to(self.device)
        self.teacher.load_state_dict(torch.load(
            teacher_path, map_location=self.device, weights_only=True,
        ))
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

        self.student = MelStudent(
            num_classes=num_classes, dropout_rate=dropout_rate,
        ).to(self.device)
        self.optimizer, self.scheduler = Loss_OP.create_optimizer(
            self.student, lr=lr, weight_decay=weight_decay,
        )
        self.trainer = StudentTrainer(
            student=self.student,
            teacher=self.teacher,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            device=self.device,
            temperature=temperature,
            alpha=alpha,
        )

    def compare_parameters(self):
        """In và trả về số tham số teacher/student cùng phần trăm giảm."""
        teacher_params = sum(p.numel() for p in self.teacher.parameters())
        student_params = sum(p.numel() for p in self.student.parameters())
        reduction = (1 - student_params / teacher_params) * 100
        print(f"Teacher parameters: {teacher_params:,}")
        print(f"Student parameters: {student_params:,}")
        print(f"Parameter reduction: {reduction:.2f}%")
        return {
            "teacher_params": teacher_params,
            "student_params": student_params,
            "reduction_percent": reduction,
        }

    def train(self, train_loader, val_loader, epochs=100,
              model_path="best_student.pth", log_interval=10):
        """Trả về history và best val accuracy; student được nạp trọng số tốt nhất."""
        return self.trainer.fit(
            train_loader, val_loader,
            epochs=epochs, model_path=model_path, log_interval=log_interval,
        )
