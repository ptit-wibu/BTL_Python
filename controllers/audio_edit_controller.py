import threading
import os
import numpy as np
from tkinter import messagebox
from pydub import AudioSegment
import soundfile as sf


class AudioEditController:
    def save_state(self):
        state = {
            "audio": self.audio,
            "audio_array": (
                self.audio_array.copy() if self.audio_array is not None else None
            ),
            "sample_rate": self.sample_rate,
            "duration": self.duration,
            "volume_gain": self.volume_gain,
            "speed": self.speed,
            "pitch_steps": self.pitch_steps,
            "reverb_enabled": self.reverb_enabled,
            "echo_enabled": self.echo_enabled,
            "fade_enabled": self.fade_enabled,
            "bass_gain": self.bass_gain,
            "mid_gain": self.mid_gain,
            "treble_gain": self.treble_gain,
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack or len(self.undo_stack) < 2:
            return
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        previous_state = self.undo_stack[-1]
        self.audio = previous_state["audio"]
        self.audio_array = previous_state["audio_array"]
        self.sample_rate = previous_state["sample_rate"]
        self.duration = previous_state["duration"]
        self.volume_gain = previous_state["volume_gain"]
        self.speed = previous_state["speed"]
        self.pitch_steps = previous_state["pitch_steps"]
        self.reverb_enabled = previous_state["reverb_enabled"]
        self.echo_enabled = previous_state["echo_enabled"]
        self.fade_enabled = previous_state["fade_enabled"]
        self.bass_gain = previous_state["bass_gain"]
        self.mid_gain = previous_state["mid_gain"]
        self.treble_gain = previous_state["treble_gain"]
        self.waveform_view.update_waveform(
            self.audio_array, self.sample_rate, self.beat_times
        )
        self.control_panel.volume_slider.set(self.volume_gain)
        self.control_panel.speed_slider.set(self.speed)
        self.control_panel.pitch_slider.set(self.pitch_steps)
        self.control_panel.bass_slider.set(self.bass_gain)
        self.control_panel.mid_slider.set(self.mid_gain)
        self.control_panel.treble_slider.set(self.treble_gain)
        self.control_panel.set_cut_defaults(self.duration)
        self.waveform_view.update_timeline(self.duration)

    def redo(self):
        if not self.redo_stack:
            return
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        self.audio = state["audio"]
        self.audio_array = state["audio_array"]
        self.sample_rate = state["sample_rate"]
        self.duration = state["duration"]
        self.volume_gain = state["volume_gain"]
        self.speed = state["speed"]
        self.pitch_steps = state["pitch_steps"]
        self.reverb_enabled = state["reverb_enabled"]
        self.echo_enabled = state["echo_enabled"]
        self.fade_enabled = state["fade_enabled"]
        self.bass_gain = state["bass_gain"]
        self.mid_gain = state["mid_gain"]
        self.treble_gain = state["treble_gain"]
        self.waveform_view.update_waveform(
            self.audio_array, self.sample_rate, self.beat_times
        )
        self.control_panel.volume_slider.set(self.volume_gain)
        self.control_panel.speed_slider.set(self.speed)
        self.control_panel.pitch_slider.set(self.pitch_steps)
        self.control_panel.bass_slider.set(self.bass_gain)
        self.control_panel.mid_slider.set(self.mid_gain)
        self.control_panel.treble_slider.set(self.treble_gain)
        self.control_panel.set_cut_defaults(self.duration)
        self.waveform_view.update_timeline(self.duration)

    def cut_audio(self):
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
            start = self.control_panel.start_entry.get().strip()
            end = self.control_panel.end_entry.get().strip()
            if not start or not end:
                raise ValueError("Thời gian bắt đầu và kết thúc không được để trống")
            start = float(start)
            end = float(end)
            if start < 0 or end <= start or end > self.duration:
                raise ValueError(
                    f"Thời gian không hợp lệ: Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc và trong phạm vi {self.duration:.3f}s"
                )
            self.is_processing = True
            self.control_panel.start_progress()
            self.main_view.update_status(
                "Đang cắt âm thanh..."
                if self.main_view.current_lang == "vi"
                else "Cutting audio..."
            )
            threading.Thread(
                target=self._cut_audio_thread, args=(start, end), daemon=True
            ).start()
        except ValueError as e:
            messagebox.showerror(
                "Lỗi" if self.main_view.current_lang == "vi" else "Error",
                (
                    f"Thời gian không hợp lệ: {str(e)}"
                    if self.main_view.current_lang == "vi"
                    else f"Invalid time: {str(e)}"
                ),
            )

    def _cut_audio_thread(self, start, end):
        try:
            self.audio = self.processor.cut_audio(self.audio, start, end, self.duration)
            self.original_audio = self.audio
            self._update_audio_arrays(self.audio)
            self.save_state()
            self.main_view.root.after(
                0,
                lambda: self.waveform_view.update_waveform(
                    self.audio_array, self.sample_rate, self.beat_times
                ),
            )
            self.main_view.root.after(
                0, lambda: self.control_panel.set_cut_defaults(self.duration)
            )
            self.main_view.root.after(
                0, lambda: self.waveform_view.update_timeline(self.duration)
            )
            self.main_view.root.after(
                0,
                lambda: self.main_view.update_status(
                    "Đã cắt âm thanh"
                    if self.main_view.current_lang == "vi"
                    else "Audio cut completed"
                ),
            )
        except Exception as e:
            self.main_view.root.after(
                0,
                lambda: messagebox.showerror(
                    "Lỗi" if self.main_view.current_lang == "vi" else "Error", str(e)
                ),
            )
        finally:
            self.is_processing = False
            self.main_view.root.after(0, self.control_panel.stop_progress)

    def apply_all(self):
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
        with self._apply_lock:
            if self.is_processing:
                return
            self.is_processing = True
        self.control_panel.start_progress()
        self.main_view.update_status(
            "Đang xử lý hiệu ứng..."
            if self.main_view.current_lang == "vi"
            else "Applying effects..."
        )
        threading.Thread(target=self._apply_all_thread, daemon=True).start()

    def _apply_all_thread(self):
        try:
            with self._apply_lock:
                if self.original_audio is not None:
                    self._update_audio_arrays(self.original_audio)
                else:
                    raise ValueError("Không có âm thanh gốc để áp dụng hiệu ứng")

                self.volume_gain = float(self.control_panel.volume_slider.get())
                self.speed = float(self.control_panel.speed_slider.get())
                self.pitch_steps = float(self.control_panel.pitch_slider.get())
                self.bass_gain = float(self.control_panel.bass_slider.get())
                self.mid_gain = float(self.control_panel.mid_slider.get())
                self.treble_gain = float(self.control_panel.treble_slider.get())
                audio = self.original_audio

                if self.volume_gain != 0:
                    audio = self.processor.change_volume(self.volume_gain, audio)
                    self._update_audio_arrays(audio)

                if self.speed != 1.0:
                    audio_array, sr = self.processor.change_speed(
                        self.speed, self.audio_array, self.sample_rate
                    )
                    temp_wav = os.path.join(
                        os.path.dirname(self.file_path or "."), "temp_speed.wav"
                    )
                    sf.write(
                        temp_wav,
                        audio_array.T if len(audio_array.shape) > 1 else audio_array,
                        sr,
                    )
                    audio = AudioSegment.from_wav(temp_wav)
                    try:
                        os.remove(temp_wav)
                    except Exception as e:
                        print(f"Warning: Could not remove {temp_wav}: {str(e)}")
                    self._update_audio_arrays(audio)

                if self.pitch_steps != 0:
                    audio_array, sr = self.processor.change_pitch(
                        self.pitch_steps, self.audio_array, self.sample_rate
                    )
                    temp_wav = os.path.join(
                        os.path.dirname(self.file_path or "."), "temp_pitch.wav"
                    )
                    sf.write(
                        temp_wav,
                        audio_array.T if len(audio_array.shape) > 1 else audio_array,
                        sr,
                    )
                    audio = AudioSegment.from_wav(temp_wav)
                    try:
                        os.remove(temp_wav)
                    except Exception as e:
                        print(f"Warning: Could not remove {temp_wav}: {str(e)}")
                    self._update_audio_arrays(audio)

                if self.reverb_enabled:
                    audio_array = self.processor.add_reverb(audio, self.channels)
                    temp_wav = os.path.join(
                        os.path.dirname(self.file_path or "."), "temp_reverb.wav"
                    )
                    if len(audio_array.shape) > 1:
                        sf.write(
                            temp_wav, audio_array, self.sample_rate, subtype="PCM_16"
                        )
                    else:
                        sf.write(
                            temp_wav, audio_array, self.sample_rate, subtype="PCM_16"
                        )
                    try:
                        audio = AudioSegment.from_wav(temp_wav)
                    except Exception as e:
                        raise Exception(f"Error reading temp_reverb.wav: {str(e)}")
                    try:
                        os.remove(temp_wav)
                    except Exception as e:
                        print(f"Warning: Could not remove {temp_wav}: {str(e)}")
                    self._update_audio_arrays(audio)

                if self.echo_enabled:
                    audio = self.processor.add_echo(audio)
                    self._update_audio_arrays(audio)

                if self.fade_enabled:
                    audio = self.processor.fade_in_out(audio)
                    self._update_audio_arrays(audio)

                if self.bass_gain != 0 or self.mid_gain != 0 or self.treble_gain != 0:
                    audio_array, sr = self.processor.apply_equalizer(
                        self.audio_array,
                        self.sample_rate,
                        self.channels,
                        self.bass_gain,
                        self.mid_gain,
                        self.treble_gain,
                    )
                    temp_wav = os.path.join(
                        os.path.dirname(self.file_path or "."), "temp_eq.wav"
                    )
                    sf.write(
                        temp_wav,
                        audio_array.T if len(audio_array.shape) > 1 else audio_array,
                        sr,
                    )
                    audio = AudioSegment.from_wav(temp_wav)
                    try:
                        os.remove(temp_wav)
                    except Exception as e:
                        print(f"Warning: Could not remove {temp_wav}: {str(e)}")
                    self._update_audio_arrays(audio)

                self.audio = audio
                self.save_state()
                self.main_view.root.after(
                    0,
                    lambda: self.waveform_view.update_waveform(
                        self.audio_array, self.sample_rate, self.beat_times
                    ),
                )
                self.main_view.root.after(
                    0, lambda: self.control_panel.set_cut_defaults(self.duration)
                )
                self.main_view.root.after(
                    0, lambda: self.waveform_view.update_timeline(self.duration)
                )
                self.main_view.root.after(
                    0,
                    lambda: self.main_view.update_status(
                        "Đã áp dụng hiệu ứng"
                        if self.main_view.current_lang == "vi"
                        else "Effects applied"
                    ),
                )
        except Exception as e:
            self.main_view.root.after(
                0,
                lambda: messagebox.showerror(
                    "Lỗi" if self.main_view.current_lang == "vi" else "Error", str(e)
                ),
            )
        finally:
            self.is_processing = False
            self.main_view.root.after(0, self.control_panel.stop_progress)

    def toggle_reverb(self):
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
        self.reverb_enabled = not self.reverb_enabled
        self.apply_all()

    def toggle_echo(self):
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
        self.echo_enabled = not self.echo_enabled
        self.apply_all()

    def toggle_fade(self):
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
        self.fade_enabled = not self.fade_enabled
        self.apply_all()

    def reset_effects(self):
        if self.audio is None:
            self.main_view.update_status(
                "Không có âm thanh để đặt lại"
                if self.main_view.current_lang == "vi"
                else "No audio to reset"
            )
            return
        self.volume_gain = 0.0
        self.speed = 1.0
        self.pitch_steps = 0.0
        self.reverb_enabled = False
        self.echo_enabled = False
        self.fade_enabled = False
        self.bass_gain = 0.0
        self.mid_gain = 0.0
        self.treble_gain = 0.0
        self.control_panel.volume_slider.set(0)
        self.control_panel.speed_slider.set(1.0)
        self.control_panel.pitch_slider.set(0)
        self.control_panel.bass_slider.set(0)
        self.control_panel.mid_slider.set(0)
        self.control_panel.treble_slider.set(0)
        self.control_panel.set_cut_defaults(self.duration)
        self.main_view.update_status(
            "Đã đặt lại hiệu ứng và thời gian cắt"
            if self.main_view.current_lang == "vi"
            else "Effects and cut times reset"
        )
