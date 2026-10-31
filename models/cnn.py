# ============================================================
# File: model.py
#
# Chức năng:
# Định nghĩa kiến trúc mô hình MelCNN cho bài toán phân loại
# Mel-Spectrogram.
#
# Đầu vào:
#   - Tensor Mel-Spectrogram có kích thước [B, 1, 128, 128]
#     trong đó:
#       B   : số lượng mẫu trong batch
#       1   : số kênh
#       128 : số Mel bins
#       128 : số frame thời gian
#
# Đầu ra:
#   - Tensor logits có kích thước [B, num_classes]
#   - Với bài toán 2 lớp: [B, 2]
#   - Hai giá trị đầu ra tương ứng với hai lớp phân loại.
#
# Kiến trúc:
#   Input → CNN Encoder → Flatten → Fully Connected Classifier
# ============================================================

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from skimage.transform import resize
import matplotlib.pyplot as plt
import seaborn as sns

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f"✅ Seed = {seed}")

set_seed(42)

#class Mel CNN
class MelCNN(nn.Module):
    def __init__ (self, num_classes=2 , dropout_rate = 0.5):
        super().__init__()
        
        #Encoder 
        self.encoder = nn.Sequential(
            nn.Conv2d(1,32, kernel_size = 3, padding = 1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2,2),
            
            nn.Conv2d(32,64, kernel_size = 3, padding = 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2,2),
            
            nn.Conv2d(64,128, kernel_size = 3, padding = 1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2,2),
            
            nn.Conv2d(128,256, kernel_size = 3, padding = 1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2,2),
        )
        
        #flatten layer
        self.classifier = nn.Sequential(
            nn.Linear(256*8*8, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        features = self.encoder(x)
        features = features.flatten(start_dim = 1) # Flatten the tensor
        output = self.classifier(features)
        return output

class Loss_OP:
    @staticmethod
    def loss_optimizer(model):
        """Khởi tạo hàm loss, optimizer và scheduler cho mô hình."""
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=10,
        )
        return criterion, optimizer, scheduler
