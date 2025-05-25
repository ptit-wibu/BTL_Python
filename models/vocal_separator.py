from spleeter.separator import Separator
import numpy as np
import librosa


class VocalSeparator:
    def __init__(self):
        self.separator = Separator("spleeter:2stems")

    def separate_vocal(self, audio_array, sample_rate, channels):
        # Đảm bảo audio ở định dạng float32
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)

        # Resample về 44100 Hz nếu cần
        if sample_rate != 44100:
            audio_array = librosa.resample(
                audio_array, orig_sr=sample_rate, target_sr=44100
            )
            sample_rate = 44100

        # Nếu là mono, chuyển sang stereo
        if len(audio_array.shape) == 1:
            audio_array = np.stack([audio_array, audio_array], axis=-1)
        elif audio_array.shape[0] == 2:
            audio_array = audio_array.T  # Spleeter mong đợi (samples, channels)

        # Tách bằng Spleeter
        separation = self.separator.separate(audio_array)

        # Lấy vocal và accompaniment
        vocal = separation["vocals"].T  # Chuyển lại về (channels, samples)
        instrumental = separation["accompaniment"].T

        # Nếu gốc là mono, lấy một kênh
        if channels == 1:
            vocal = vocal[0]
            instrumental = instrumental[0]

        return vocal, instrumental
