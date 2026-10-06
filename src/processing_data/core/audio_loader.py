"""
file load audio from computer
định dangtj wav, mp3, m4a, flac, ogg
"""
import librosa                # thư viện hỗ trợ các thao tác xử lý âm thanh, bao gồm việc tải và phân tích các tệp âm thanh
from pathlib import Path      # thư viện hỗ trợ thao tác với đường dẫn tệp và thư mục

AUDIO_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac', '.ogg')  # các dịnh dạng âm thanh được hỗ trợ


class AudioLoader:
    """Load audio files."""
    
    def __init__(self, sample_rate=None, mono=True):
        self.sample_rate = sample_rate    # tần số lấy mẫu ( sample rate) của âm thanh 
        self.mono = mono                  # nếu mono=True, âm thanh sẽ được chuyển đổi thành tín hiệu đơn kênh (mono) khi tải, 
                                          # nếu mono=False, âm thanh sẽ được giữ nguyên kênh (stereo hoặc nhiều kênh)
    
    def load(self, filepath):
        """Load 1 audio file. Returns (data, sr)."""
        data, sr = librosa.load(filepath, sr=self.sample_rate, mono=self.mono)  # load audio file
        return data, sr                                                         # trả về dữ liệu âm thanh và tần số lấy mẫu của tệp âm thanh đã tải
    
    def get_files(self, folder):                                                # hàm lấy danh sách các tệp âm thanh trong thư mục 
        """Get list of audio files in folder (recursive)."""
        folder = Path(folder)
        files = []
        for f in folder.rglob('*'):
            if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
                files.append(str(f))
        return sorted(files)


# if __name__ == "__main__":
#     import os
#     project_root = Path(__file__).parent.parent.parent.parent
#     os.chdir(project_root)
    
#     loader = AudioLoader()
#     files = loader.get_files('data/raw_data/dau_nhua/v1c1')
#     print(f"Found {len(files)} files")
    
#     if files:
#         data, sr = loader.load(files[0])
#         print(f"Loaded: {Path(files[0]).name}")
#         print(f"SR: {sr}")
#         print(f"Duration: {len(data)/sr:.2f}s")