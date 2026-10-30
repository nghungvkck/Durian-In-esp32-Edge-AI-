"""Loss Knowledge Distillation và bộ tối ưu dùng lại khi huấn luyện student."""

import torch
from torch import nn, optim


class Loss_OP:
    """Cung cấp loss distillation, optimizer và scheduler cho student."""

    @staticmethod
    def distillation_loss(
        student_logits,
        teacher_logits,
        labels,
        temperature=2.0,
        alpha=0.1,
    ):
        """Kết hợp alpha * CE với (1 - alpha) * KL * temperature**2.

        alpha là trọng số dành cho nhãn thật; phần còn lại dành cho teacher.
        """
        ce_loss = nn.CrossEntropyLoss()(student_logits, labels)
        student_soft = torch.log_softmax(student_logits / temperature, dim=1)
        teacher_soft = torch.softmax(teacher_logits / temperature, dim=1)
        kd_loss = nn.KLDivLoss(reduction="batchmean")(student_soft, teacher_soft)
        return alpha * ce_loss + (1 - alpha) * kd_loss * temperature ** 2


    @staticmethod
    def create_optimizer(
        student,
        lr=0.001,
        weight_decay=1e-4,
        factor=0.5,
        patience=10,
    ):
        """Trả về Adam và ReduceLROnPlateau; gọi scheduler.step(val_loss)."""
        optimizer = optim.Adam(student.parameters(), lr=lr, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=factor, patience=patience,
        )
        return optimizer, scheduler
