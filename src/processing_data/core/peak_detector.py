"""
PEAK DETECTOR
=============
Detect peaks in smoothed audio signal.
"""
import sys   # thư viện hỗ trợ các thao tác liên quan đến hệ thống, như quản lý đường dẫn và tham số dòng lệnh
from pathlib import Path  # thư viện hỗ trợ thao tác với đường dẫn tệp và thư mục
import numpy as np
from scipy.signal import find_peaks  # thư viện hỗ trợ các thao tác xử lý tín hiệu, 
                                     # trong đó có hàm find_peaks để phát hiện các đỉnh trong tín hiệu


_root_dir = Path(__file__).parent.parent.parent.parent   # core -> processing_data -> src -> config
if str(_root_dir) not in sys.path:    # Add root dir to sys.path for importing modules from config
    sys.path.insert(0, str(_root_dir))  

from config.config_processing_data import (
    PEAK_THRESHOLD_RATIO,   # ngưỡng phát hiện 
    PEAK_MIN_DISTANCE_SEC,  # khoảng cách tối thiểu giữa các đỉnh (s)
)

class PeakDetector:
    """Detect peaks in smoothed audio signal."""
    
    def __init__(self,                  # hàm khởi tạo với các tham số mặc định từ config
                 threshold_ratio=PEAK_THRESHOLD_RATIO,
                 min_distance_sec=PEAK_MIN_DISTANCE_SEC):
        self.threshold_ratio = threshold_ratio
        self.min_distance_sec = min_distance_sec
    
    def detect(self, smoothed_data, sr):
        """Detect peaks in SMOOTHED audio signal."""
        threshold = self.threshold_ratio * np.max(smoothed_data)    # tính toán ngưỡng dựa trên giá trị cực đại của dữ liệu đã làm mịn
        min_distance = int(sr * self.min_distance_sec)             # tính toán khoảng cách tối thiểu giữa các đỉnh dựa trên tần số lấy mẫu và khoảng thời gian tối thiểu
        peaks, _ = find_peaks(smoothed_data, height=threshold, distance=min_distance)  # sử dụng hàm find_peaks từ scipy để phát hiện các đỉnh trong dữ liệu đã làm mịn, với các điều kiện về ngưỡng và khoảng cách tối thiểu
        return peaks  # trả về 1 list các chỉ số của các đỉnh được phát hiện trong dữ liệu đã làm mịn


if __name__ == "__main__":
    import os
    project_root = Path(__file__).parent.parent.parent.parent  # core -> processing_data -> src -> config
    os.chdir(project_root)   # thay đổi thư mục làm việc hiện tại sang thư mục gốc của dự án để đảm bảo rằng các tệp và mô-đun có thể được truy cập đúng cách
    
    from audio_loader import AudioLoader
    from smoother import Smoother
    from peak_detector import PeakDetector
    
    loader = AudioLoader()   # gọi các lớp AudioLoader
    smoother = Smoother()    # goi các lớp Smoother
    detector = PeakDetector() # gọi các lớp PeakDetector
    
    files = loader.get_files('data/raw_data/dau_nhua/v1c1')
    
    if files:
        data, sr = loader.load(files[0])
        smoothed = smoother.process(data, sr)
        peaks = detector.detect(smoothed, sr)
        
        print(f"File: {Path(files[0]).name}")
        print(f"Duration: {len(data)/sr:.2f}s")
        print(f"Peaks: {len(peaks)}")
        print(f"Times: {[f'{p/sr:.2f}s' for p in peaks]}")