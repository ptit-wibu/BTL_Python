import asyncio
import os
import threading
import time
from tkinter import messagebox
import logging

import ffmpeg

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioPreviewController:
    def preview_audio(self):
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
        try:

            self.is_processing = True
            self.control_panel.start_progress()
            self.main_view.update_status(
                "Đang phát thử..."
                if self.main_view.current_lang == "vi"
                else "Previewing..."
            )
            self.temp_preview_file = os.path.join(
                os.path.dirname(self.file_path or "."), "audio_preview.wav"
            )
            self.audio.export(self.temp_preview_file, format="wav")
            probe = ffmpeg.probe(self.temp_preview_file)
            self.duration = float(probe["format"]["duration"])
            self.exporter.total_bytes_played = 0
            self.exporter.preview_audio(
                self.temp_preview_file,
                self.sample_rate,
                self.channels,
                self.current_position,
                self.duration,
            )
            self.control_panel.preview_button.configure(state="disabled")
            self.control_panel.stop_button.configure(state="normal")
            threading.Thread(
                target=self.update_slider, daemon=True
            ).start()  # Start the slider update thread
        except ValueError as e:
            messagebox.showerror(
                "Lỗi" if self.main_view.current_lang == "vi" else "Error",
                (
                    f"Thời gian không hợp lệ: {str(e)}"
                    if self.main_view.current_lang == "vi"
                    else f"Invalid time: {str(e)}"
                ),
            )
        except Exception as e:
            messagebox.showerror(
                "Lỗi" if self.main_view.current_lang == "vi" else "Error",
                (
                    f"Lỗi phát âm thanh: {str(e)}"
                    if self.main_view.current_lang == "vi"
                    else f"Playback error: {str(e)}"
                ),
            )
        finally:
            self.is_processing = False
            self.control_panel.stop_progress()

    def update_slider(self):
        """Quản lý việc phát thử âm thanh."""
        print("Đang phát thử âm thanh...")
        while self.exporter.is_previewing and self.current_position < self.duration:
            if not self.is_seeking:
                self.waveform_view.set_timeline_current(self.current_position)
            time.sleep(0.1)

        self.main_view.update_status(
            "Đã dừng phát"
            if self.main_view.current_lang == "vi"
            else "Playback stopped"
        )

        logging.info("Preview stopped in audio preview controller")

    def start_seeking(self, event):
        print("Button pressed")
        self.is_seeking = True

    def on_slider_move(self, value):
        """Cập nhật giao diện khi kéo thanh trượt."""
        # print("Button moving")
        if self.is_seeking:
            self.current_position = float(value)
            self.waveform_view.set_timeline_current(
                position=self.current_position, set_slider=False
            )
            logging.debug(f"Đang tua đến vị trí: {self.current_position}")

    def seek_audio(self, event):
        print("Button released")
        if not self.temp_preview_file:
            self.is_seeking = False
            return
        new_position = self.waveform_view.timeline_slider.get()
        if new_position < 0 or new_position > self.duration:
            return
        self.stop_preview()
        self.current_position = new_position
        self.is_seeking = False
        self.preview_audio()

        # threading.Thread(target=self.update_slider, daemon=True).start()

    def stop_preview(self):
        self.exporter.stop_preview(self.temp_preview_file, None)
        self.main_view.update_status(
            "Đã dừng phát"
            if self.main_view.current_lang == "vi"
            else "Playback stopped"
        )
        self.control_panel.preview_button.configure(state="normal")
        #self.control_panel.stop_button.configure(state="disabled")
        if abs(self.current_position - self.duration) < 0.001:
            self.waveform_view.set_timeline_current(0, self.duration)
            self.waveform_view.timeline_slider.set(0)
            self.current_position = 0
        self.is_seeking = False
