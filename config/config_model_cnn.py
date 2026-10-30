#=========================
# PATH
#=========================
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BASE_PATH = PROJECT_ROOT / "data" / "processed" / "data_lan7_no_smooth"

N_MELS = 128
NOISE_FACTOR = 0.005
SHIFT_MAX = 10
FACTOR_RANGE = (0.8, 1.2)

# Mô hình và huấn luyện
BATCH_SIZE = 32
NUM_CLASSES = 2
DROPOUT_RATE = 0.5
EPOCHS = 100
LOG_INTERVAL = 10
MODEL_PATH = PROJECT_ROOT / "pth" / "best_model.pth"

# Knowledge Distillation: dữ liệu, Student và các siêu tham số huấn luyện
DATA_TRAIN_DIR = PROJECT_ROOT / "data" / "data_train"
STUDENT_MODEL_PATH = PROJECT_ROOT / "pth" / "model_Student.pth"
SEED = 42
STUDENT_DROPOUT_RATE = 0.3
KD_TEMPERATURE = 4.0
KD_ALPHA = 0.5  # Trọng số CE; phần (1 - KD_ALPHA) dành cho loss từ Teacher
STUDENT_LEARNING_RATE = 0.001
STUDENT_WEIGHT_DECAY = 1e-4
STUDENT_SCHEDULER_FACTOR = 0.5
STUDENT_SCHEDULER_PATIENCE = 10
