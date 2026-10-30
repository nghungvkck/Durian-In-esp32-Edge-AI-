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
