"""
SEGMENTER
=========
Cut segments around each peak.
"""
import sys
from pathlib import Path
import numpy as np

# core -> processing_data -> src -> config
_root_dir = Path(__file__).parent.parent.parent.parent
if str(_root_dir) not in sys.path:          # Add root dir to sys.path for importing modules from config
    sys.path.insert(0, str(_root_dir))

from config.config_processing_data import (
    SEGMENT_PRE_PEAK_SEC,   # chỉ số thời gian trước đỉnh (s) để bắt đầu cắt đoạn âm thanh
    SEGMENT_DURATION_SEC,   # chỉ số thời gian tổng cộng của đoạn âm thanh (s) sau khi cắt
)


class Segmenter:
    """Cut segments around peaks."""
    
    def __init__(self,            # hàm khởi tọa với các tham số mặc định từ config
                 pre_peak_sec=SEGMENT_PRE_PEAK_SEC,
                 duration_sec=SEGMENT_DURATION_SEC):
        self.pre_peak_sec = pre_peak_sec
        self.duration_sec = duration_sec
    
    #======================================
    # hÀM CẮT 1 ĐOẠN ÂM THANH XUNG QUANH 1 ĐỈNH, tham số là dữ liệu âm thanh, tần số lấy mẫu và chỉ số của đỉnh
    #======================================
    def segment(self, data, sr, peak_idx):  
        """Cut a single segment around one peak."""
        pre_samples = int(self.pre_peak_sec * sr)   # số mẫu tương ứng với khoảng thời gian trước đỉnh (s) để bắt đầu cắt đoạn âm thanh
        total_samples = int(self.duration_sec * sr)  # số mẫu tương ứng với khoảng thời gian tổng cộng của đoạn âm thanh (s) sau khi cắt

        start = max(0, peak_idx - pre_samples)   # tính toán chỉ số bắt đầu của đoạn âm thanh. 
                                                 # cách tính là lấy chỉ số đỉnh trừ đi số mẫu trước đỉnh, 
                                                 # nhưng không được nhỏ hơn 0 (không vượt quá giới hạn đầu của dữ liệu âm thanh)
        end = min(len(data), start + total_samples) # tính toán chỉ số kết thúc của đoạn âm thanh
        segment_data = data[start:end].copy()
        
        return {
            'data': segment_data,
            'start_sample': start,
            'end_sample': end,
            'start_time': start / sr,
            'end_time': end / sr,
            'peak_time': peak_idx / sr,
            'peak_index': peak_idx,
        }
    
    def segment_all(self, data, sr, peaks):
        """Cut segments for ALL peaks."""
        return [self.segment(data, sr, int(p)) for p in peaks]


if __name__ == "__main__":
    import os
    project_root = Path(__file__).parent.parent.parent.parent
    os.chdir(project_root)
    
    from audio_loader import AudioLoader
    from smoother import Smoother
    from peak_detector import PeakDetector
    from segmenter import Segmenter
    
    loader = AudioLoader()
    smoother = Smoother()
    detector = PeakDetector()
    segmenter = Segmenter()
    
    files = loader.get_files('data/raw_data/dau_nhua/v1c1')
    
    if files:
        data, sr = loader.load(files[0])
        
        smoothed = smoother.process(data, sr)
        peaks = detector.detect(smoothed, sr)
        segments = segmenter.segment_all(data, sr, peaks)
        
        print(f"File: {Path(files[0]).name}")
        print(f"Duration: {len(data)/sr:.2f}s")
        print(f"Peaks: {len(peaks)}\n")
        
        print(f"Segments ({len(segments)}):")
        for i, seg in enumerate(segments):
            seg_dur = len(seg['data']) / sr
            print(f"  [{i+1}] peak={seg['peak_time']:.3f}s  "
                  f"start={seg['start_time']:.3f}s  "
                  f"end={seg['end_time']:.3f}s  "
                  f"dur={seg_dur:.3f}s")