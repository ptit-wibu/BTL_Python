import os
import multiprocessing as mp
from tkinter import messagebox
from pydub import AudioSegment
import soundfile as sf
from controllers.effect_controller import separate_vocal_worker


class AudioVocalController:
    def separate_vocal(self):
        if self.is_processing:
            messagebox.showwarning(
                "Cảnh báo" if self.main_view.current_lang == "vi" else "Warning",
                (
                    "Đang xử lý, vui lòng chờ!"
                    if self.main_view.current_lang == "vi"
                    else "Processing, please wait!"
                ),
            )
            return
        if self.audio is None:
            messagebox.showwarning(
                "Cảnh báo" if self.main_view.current_lang == "vi" else "Warning",
                (
                    "Vui lòng tải file âm thanh trước"
                    if self.main_view.current_lang == "vi"
                    else "Please load an audio file first"
                ),
            )
            return
        if self._after_id is not None:
            self.main_view.root.after_cancel(self._after_id)
            self._after_id = None
        self.is_processing = True
        self.control_panel.start_progress()
        self.main_view.update_status(
            "Đang tách giọng hát..."
            if self.main_view.current_lang == "vi"
            else "Separating vocals..."
        )
        process = mp.Process(
            target=separate_vocal_worker,
            args=(self.audio_array.copy(), self.sample_rate, self.channels, self.queue),
        )
        process.start()
        self._check_separate_vocal_result()

    def _check_separate_vocal_result(self):
        if not self.queue.empty():
            result = self.queue.get()
            if result[0] == "success":
                vocal, instrumental = result[1], result[2]
                output_dir = os.path.dirname(self.file_path or ".")

                # Chuyển vocal thành AudioSegment
                temp_vocal_wav = os.path.join(output_dir, "temp_vocal.wav")
                sf.write(
                    temp_vocal_wav,
                    vocal.T if len(vocal.shape) > 1 else vocal,
                    self.sample_rate,
                    subtype="PCM_16",
                )
                vocal_segment = AudioSegment.from_wav(temp_vocal_wav)
                self.exporter.export_audio(
                    vocal_segment,
                    "wav",
                    os.path.join(output_dir, "vocal.wav"),
                    self.file_path,
                    self.sample_rate,
                    self.channels,
                )
                os.remove(temp_vocal_wav)

                # Chuyển instrumental thành AudioSegment
                temp_instrumental_wav = os.path.join(
                    output_dir, "temp_instrumental.wav"
                )
                sf.write(
                    temp_instrumental_wav,
                    instrumental.T if len(instrumental.shape) > 1 else instrumental,
                    self.sample_rate,
                    subtype="PCM_16",
                )
                instrumental_segment = AudioSegment.from_wav(temp_instrumental_wav)
                self.exporter.export_audio(
                    instrumental_segment,
                    "wav",
                    os.path.join(output_dir, "instrumental.wav"),
                    self.file_path,
                    self.sample_rate,
                    self.channels,
                )
                os.remove(temp_instrumental_wav)

                self.main_view.root.after(
                    0,
                    lambda: self.main_view.update_status(
                        "Đã tách giọng hát và nhạc nền"
                        if self.main_view.current_lang == "vi"
                        else "Vocals and instrumental separated"
                    ),
                )
            else:
                error_msg = result[1]
                self.main_view.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Lỗi" if self.main_view.current_lang == "vi" else "Error",
                        error_msg,
                    ),
                )
            self.is_processing = False
            self.main_view.root.after(0, self.control_panel.stop_progress)
            self._after_id = None
        else:
            self._after_id = self.main_view.root.after(
                100, self._check_separate_vocal_result
            )
