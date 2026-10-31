"""Structured pruning cho MelStudent; gọi từ main sau khi nạp trọng số."""

from copy import deepcopy

import torch
from torch import nn


class StudentPruner:
    """Cắt channel theo L1 của bộ lọc Conv2d, giữ nguyên model đầu vào."""

    @staticmethod
    def structured_pruning(model, prune_ratio=0.2):
        """Trả về model đã cắt channel và chép các trọng số được giữ lại.

        Hỗ trợ kiến trúc MelStudent: bốn block Conv2d/BatchNorm2d,
        global average pooling và Linear đầu tiên ở classifier[0].
        """
        if not 0 <= prune_ratio < 1:
            raise ValueError("prune_ratio phải nằm trong khoảng [0, 1).")

        convs = [(i, m) for i, m in enumerate(model.features)
                 if isinstance(m, nn.Conv2d)]
        bns = [(i, m) for i, m in enumerate(model.features)
               if isinstance(m, nn.BatchNorm2d)]
        if len(convs) != 4 or len(bns) != 4:
            raise ValueError("Model phải có 4 lớp Conv2d và 4 lớp BatchNorm2d.")
        if any(conv.groups != 1 for _, conv in convs):
            raise ValueError("Chưa hỗ trợ grouped/depthwise convolution.")
        for block, ((_, conv), (_, bn)) in enumerate(zip(convs, bns)):
            if bn.num_features != conv.out_channels:
                raise ValueError("BatchNorm2d không khớp số channel của Conv2d.")
            if block and conv.in_channels != convs[block - 1][1].out_channels:
                raise ValueError("Các lớp Conv2d phải nối tiếp theo channel.")
        classifier = model.classifier[0]
        if not isinstance(classifier, nn.Linear):
            raise ValueError("classifier[0] phải là nn.Linear.")
        if classifier.in_features != convs[-1][1].out_channels:
            raise ValueError("Đầu vào classifier phải khớp channel Conv2d cuối.")

        keep = []
        for _, conv in convs:
            channels = max(1, int(conv.out_channels * (1 - prune_ratio)))
            importance = conv.weight.detach().abs().sum(dim=(1, 2, 3))
            keep.append(torch.topk(importance, channels).indices.sort().values)

        # Giữ cấu hình pooling, dropout, số lớp, device và dtype của model gốc.
        pruned = deepcopy(model)
        with torch.no_grad():
            for block, ((conv_index, conv), (bn_index, bn)) in enumerate(zip(convs, bns)):
                out_idx = keep[block]
                in_idx = (keep[block - 1] if block else
                          torch.arange(conv.in_channels, device=conv.weight.device))
                new_conv = nn.Conv2d(
                    len(in_idx), len(out_idx), conv.kernel_size,
                    stride=conv.stride, padding=conv.padding,
                    dilation=conv.dilation, bias=conv.bias is not None,
                    padding_mode=conv.padding_mode,
                    device=conv.weight.device, dtype=conv.weight.dtype,
                )
                new_conv.weight.copy_(conv.weight[out_idx][:, in_idx])
                new_conv.weight.requires_grad_(conv.weight.requires_grad)
                if conv.bias is not None:
                    new_conv.bias.copy_(conv.bias[out_idx])
                    new_conv.bias.requires_grad_(conv.bias.requires_grad)
                new_conv.train(conv.training)
                pruned.features[conv_index] = new_conv

                new_bn = deepcopy(bn)
                new_bn.num_features = len(out_idx)
                if bn.affine:
                    new_bn.weight = nn.Parameter(
                        bn.weight[out_idx].clone(), requires_grad=bn.weight.requires_grad,
                    )
                    new_bn.bias = nn.Parameter(
                        bn.bias[out_idx].clone(), requires_grad=bn.bias.requires_grad,
                    )
                if bn.track_running_stats:
                    new_bn.running_mean = bn.running_mean[out_idx].clone()
                    new_bn.running_var = bn.running_var[out_idx].clone()
                pruned.features[bn_index] = new_bn

            new_classifier = nn.Linear(
                len(keep[-1]), classifier.out_features,
                bias=classifier.bias is not None,
                device=classifier.weight.device, dtype=classifier.weight.dtype,
            )
            
            new_classifier.weight.copy_(classifier.weight[:, keep[-1]])
            new_classifier.weight.requires_grad_(classifier.weight.requires_grad)
            if classifier.bias is not None:
                new_classifier.bias.copy_(classifier.bias)
                new_classifier.bias.requires_grad_(classifier.bias.requires_grad)
            new_classifier.train(classifier.training)
            pruned.classifier[0] = new_classifier

        return pruned

