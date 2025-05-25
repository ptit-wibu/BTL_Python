import os
import threading
import time
from tkinter import messagebox, filedialog
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioLoaderController:
    def handle_drop(self, event):
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
        file_path = event.data.strip("{}")
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)

    def load_file(self, file_path=None):
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
        if not file_path:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Audio files", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a *.wma")
                ]
            )
        if file_path:
            self.is_processing = True
            self.control_panel.start_progress()
            self.main_view.update_status(
                "Đang tải file âm thanh..."
                if self.main_view.current_lang == "vi"
                else "Loading audio file..."
            )
            threading.Thread(
                target=self._load_file_thread, args=(file_path,), daemon=True
            ).start()

    def _load_file_thread(self, file_path):
        try:
            start_time = time.time()
            (
                self.audio,
                self.audio_array,
                self.sample_rate,
                self.channels,
                self.duration,
                self.bitrate,
                self.metadata,
            ) = self.loader.load_audio(file_path)
            self.original_audio = self.audio
            self.file_path = file_path
            self.save_state()
            self.main_view.root.after(
                0,
                lambda: self.waveform_view.update_waveform(
                    self.audio_array, self.sample_rate
                ),
            )
            self.main_view.root.after(
                0, lambda: self.control_panel.set_cut_defaults(self.duration)
            )
            self.main_view.root.after(
                0, lambda: self.waveform_view.update_timeline(self.duration)
            )
            self.main_view.root.after(
                0, lambda: self.waveform_view.set_timeline_current(0)
            )
            self.main_view.root.after(
                0,
                lambda: self.main_view.update_status(
                    f"Đã tải: {os.path.basename(file_path)} (Thời lượng: {self.duration:.3f}s)"
                    if self.main_view.current_lang == "vi"
                    else f"Loaded: {os.path.basename(file_path)} (Duration: {self.duration:.3f}s)"
                ),
            )
            self.main_view.root.after(
                0,
                lambda: self.control_panel.update_file_info(
                    self.duration,
                    self.channels,
                    self.sample_rate,
                    self.bitrate,
                    self.metadata,
                ),
            )
            self.reset_effects()
            self.beat_times, self.tempo = self.processor.detect_beats(
                self.audio_array, self.sample_rate
            )
            self.main_view.root.after(
                0,
                lambda: self.waveform_view.update_waveform(
                    self.audio_array, self.sample_rate, self.beat_times
                ),
            )
            logging.info(
                f"Loaded file {file_path} in {time.time() - start_time:.2f} seconds"
            )
        except Exception as e:
            self.main_view.root.after(
                0,
                lambda e=e: messagebox.showerror(
                    "Lỗi" if self.main_view.current_lang == "vi" else "Error", str(e)
                ),
            )
        finally:
            self.is_processing = False
            self.main_view.root.after(0, self.control_panel.stop_progress)
