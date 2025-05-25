import asyncio
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class WaveformView:
    def __init__(self, parent, controller, languages, current_lang):
        self.controller = controller
        self.languages = languages
        self.current_lang = current_lang
        self.is_manual_sliding = False

        # Define theme colors
        self.dark_blue = "#0A1E3D"
        self.medium_blue = "#0C2655"
        self.light_blue = "#1C3F75"
        self.accent_green = "#03fcc6"
        self.accent_cyan = "#00FFFF"
        self.text_color = "white"
        self.fg_color = "#02fa55"
        self.grid_color = "#2D3748"

        # Waveform main frame
        self.waveform_frame = ctk.CTkFrame(parent, fg_color=self.dark_blue)
        self.waveform_frame.pack(fill="both", expand=True, pady=0)

        # File name display
        self.file_name_label = ctk.CTkLabel(
            self.waveform_frame, text="", anchor="center", text_color=self.text_color
        )
        self.file_name_label.pack(fill="x", pady=0)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(11, 3), facecolor=self.dark_blue)
        self.ax.set_facecolor(self.dark_blue)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.tick_params(axis="both", colors="white", labelsize=7)
        self.ax.grid(True, linestyle="--", alpha=0.7, color=self.grid_color)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.waveform_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.fig.tight_layout()

        # Time indicators
        self.time_indicators_frame = ctk.CTkFrame(
            self.waveform_frame, fg_color=self.dark_blue
        )
        self.time_indicators_frame.pack(fill="x", pady=5)

        self.current_time_label = ctk.CTkLabel(
            self.time_indicators_frame, text="00:00.0", text_color=self.text_color
        )
        self.current_time_label.pack(side="left", padx=5)

        self.total_time_label = ctk.CTkLabel(
            self.time_indicators_frame, text="00:00.0", text_color=self.text_color
        )
        self.total_time_label.pack(side="right", padx=5)

        # Controls frame
        self.controls_frame = ctk.CTkFrame(parent, fg_color=self.dark_blue)
        self.controls_frame.pack(fill="x", pady=0)
        '''
        self.play_button = ctk.CTkButton(
            self.controls_frame, text="▶", width=40, command=None
        )
        self.play_button.pack(side="left", padx=10, pady=15)
        '''
        self.timeline_frame = ctk.CTkFrame(self.controls_frame, fg_color=self.dark_blue)
        self.timeline_frame.pack(side="top", fill="x", expand=True, padx=10)

        self.timeline_slider = ctk.CTkSlider(
            self.timeline_frame,
            from_=0,
            to=100,
            orientation="horizontal",
        )
        self.timeline_slider.set(0)
        self.timeline_slider.pack(fill="x", expand=True)
        
        self.volume_label = ctk.CTkLabel(
            self.controls_frame, text="", text_color=self.text_color
        )
        self.volume_label.pack(side="left", padx=5)

        self.format_frame = ctk.CTkFrame(self.controls_frame, fg_color=self.dark_blue)
        self.format_frame.pack(side="left", padx=10)
        '''
        self.format_combobox = ctk.CTkComboBox(
            self.format_frame,
            values=["mp3", "wav", "ogg", "flac"],
            width=100,
            state="readonly",
            command=None,
        )
        self.format_combobox.set("mp3")
        self.format_combobox.pack(side="left", padx=5)
        '''
    def bind_slider_events(self):
        self.timeline_slider.configure(command=self.controller.on_slider_move)

    def update_waveform(self, audio_array, sr, beat_times=None):
        self.ax.clear()
        if len(audio_array.shape) > 1:
            audio_array = audio_array[0]
        time_axis = np.linspace(0, len(audio_array) / sr, len(audio_array))
        self.ax.plot(time_axis, audio_array, color=self.accent_green)

        interval = 1
        max_time = len(audio_array) / sr
        beat_times = np.arange(0, max_time, interval)
        for beat in beat_times:
            self.ax.axvline(x=beat, color=self.accent_green, linestyle="--", alpha=0.3)

        file_name = os.path.basename(self.controller.file_path)
        self.ax.set_title(file_name, fontsize=10, color=self.fg_color, pad=7)
        self.ax.tick_params(axis="both", colors=self.fg_color)
        self.ax.grid(True, linestyle="--", alpha=0.7, color=self.grid_color)
        self.ax.set_facecolor("#2D3748")
        self.fig.set_facecolor("#1E293B")

        self.fig.tight_layout()
        self.canvas.draw()

    def update_timeline(self, duration):
        self.timeline_slider.configure(to=duration)
        self.total_time_label.configure(text=f"{duration:.2f}s")

    def set_timeline_current(self, position, set_slider=True):
        if set_slider:
            self.timeline_slider.set(position)
        self.current_time_label.configure(text=f"{position:.2f}s")
