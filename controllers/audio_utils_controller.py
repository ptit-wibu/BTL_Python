import numpy as np
from pydub import AudioSegment
import tkinter as tk


class AudioUtilsController:
    def _update_audio_arrays(self, audio_segment):
        self.audio_array = np.array(audio_segment.get_array_of_samples())
        if self.channels == 2:
            self.audio_array = self.audio_array.reshape(-1, 2).T
        else:
            self.audio_array = self.audio_array.reshape(-1)
        self.audio_array = self.audio_array / (2**15)
        self.sample_rate = audio_segment.frame_rate
        self.duration = len(audio_segment) / 1000.0

    def change_language(self, event=None):
        lang = self.main_view.lang_combobox.get()
        self.main_view.current_lang = "vi" if lang == "Tiếng Việt" else "en"
        self.control_panel.current_lang = self.main_view.current_lang
        self.waveform_view.current_lang = self.main_view.current_lang
        lang_dict = self.main_view.languages[self.main_view.current_lang]
        self.main_view.root.title(lang_dict["title"])
        self.main_view.status.configure(text=lang_dict["status"])
        self.main_view.lang_label.configure(text=lang_dict["language"])
        # self.control_panel.control_frame.config(text=lang_dict["control_frame"])
        self.control_panel.file_info_label.configure(text=lang_dict["file_info"])
        self.control_panel.load_button.configure(text=lang_dict["load"])
        self.control_panel.format_label.configure(text=lang_dict["format"])
        self.control_panel.export_button.configure(text=lang_dict["export"])
        self.control_panel.undo_button.configure(text=lang_dict["undo"])
        self.control_panel.redo_button.configure(text=lang_dict["redo"])
        self.control_panel.cut_label.configure(text=lang_dict["cut"])
        self.control_panel.apply_cut_button.configure(text=lang_dict["apply_cut"])
        self.control_panel.volume_label.configure(text=lang_dict["volume"])
        self.control_panel.speed_label.configure(text=lang_dict["speed"])
        self.control_panel.pitch_label.configure(text=lang_dict["pitch"])
        self.control_panel.apply_all_button.configure(text=lang_dict["apply"])
        self.control_panel.eq_label.configure(text=lang_dict["eq"])
        self.control_panel.bass_label.configure(text=lang_dict["bass"])
        self.control_panel.mid_label.configure(text=lang_dict["mid"])
        self.control_panel.treble_label.configure(text=lang_dict["treble"])
        self.control_panel.reverb_button.configure(text=lang_dict["reverb"])
        self.control_panel.echo_button.configure(text=lang_dict["echo"])
        self.control_panel.fade_button.configure(text=lang_dict["fade"])
        self.control_panel.vocal_button.configure(text=lang_dict["vocal"])
        self.control_panel.preview_button.configure(text=lang_dict["preview"])
        self.control_panel.stop_button.configure(text=lang_dict["stop"])
        # self.waveform_view.timeline_label.config(text=lang_dict["timeline"])
        # self.waveform_view.ax.set_title(
        #     lang_dict["waveform"], fontsize=14, color="black"
        # )
        self.waveform_view.canvas.draw()
        if self.audio_array is not None:
            self.waveform_view.set_timeline_current(0)
            self.control_panel.update_file_info(
                self.duration,
                self.channels,
                self.sample_rate,
                self.bitrate,
                self.metadata,
            )

    def seek_timeline(self, position):
        position = float(position)
        self.waveform_view.set_timeline_current(position)
