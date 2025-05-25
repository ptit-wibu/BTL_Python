import tkinter as tk
import customtkinter as ctk


class ControlPanel:
    def __init__(self, parent, controller, languages, current_lang):
        self.controller = controller
        self.languages = languages
        self.current_lang = current_lang

        # Theme colors
        self.dark_blue = "#0A1E3D"
        self.medium_blue = "#0C2655"
        self.light_blue = "#1C3F75"
        self.accent_green = "#00FF99"
        self.accent_cyan = "#00FFFF"
        self.text_color = "white"

        # Create control panel frame
        self.control_frame = ctk.CTkFrame(
            parent, fg_color=self.dark_blue, corner_radius=10
        )
        self.control_frame.pack(fill="x", pady=5)

        # File info label
        self.file_info_label = ctk.CTkLabel(
            self.control_frame,
            text=self.languages[self.current_lang]["file_info"],
            text_color=self.text_color,
        )
        self.file_info_label.pack(fill="x", pady=5)

        # Sub-sections
        self.create_load_export_frame()
        self.create_edit_controls_frame()
        self.create_audio_controls_frame()
        self.create_effects_frame()

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self.control_frame, progress_color=self.accent_green
        )
        self.progress.set(0)
        self.progress.pack(fill="x", pady=5)

    def create_load_export_frame(self):
        frame = ctk.CTkFrame(self.control_frame, fg_color=self.medium_blue)
        frame.pack(fill="x", pady=5)

        self.load_button = ctk.CTkButton(
            frame, text=self.languages[self.current_lang]["load"]
        )
        self.load_button.pack(side="left", padx=10)

        self.format_frame = ctk.CTkFrame(frame, fg_color=self.medium_blue)
        self.format_frame.pack(side="left")

        self.format_label = ctk.CTkLabel(
            self.format_frame,
            text=self.languages[self.current_lang]["format"],
            text_color=self.text_color,
        )
        self.format_label.pack(side="left", padx=5)
        
        self.format_combobox = ctk.CTkOptionMenu(
            self.format_frame, values=["mp3", "wav", "ogg", "flac", "aac"]
        )
        self.format_combobox.set("mp3")
        self.format_combobox.pack(side="left", padx=5)

        self.export_button = ctk.CTkButton(
            frame, text=self.languages[self.current_lang]["export"]
        )
        self.export_button.pack(side="left", padx=10)

        self.undo_button = ctk.CTkButton(
            frame, text=self.languages[self.current_lang]["undo"], width=50
        )
        self.undo_button.pack(side="right", padx=10)

        self.redo_button = ctk.CTkButton(
            frame, text=self.languages[self.current_lang]["redo"], width=50
        )
        self.redo_button.pack(side="right", padx=10)

    def create_edit_controls_frame(self):
        frame = ctk.CTkFrame(self.control_frame, fg_color=self.medium_blue)
        frame.pack(fill="x", pady=5)

        self.cut_label = ctk.CTkLabel(
            frame,
            text=self.languages[self.current_lang]["cut"],
            text_color=self.text_color,
        )
        self.cut_label.pack(side="left", padx=10)

        self.start_entry = ctk.CTkEntry(frame, width=80, justify="center")
        self.start_entry.pack(side="left", padx=10)

        self.end_entry = ctk.CTkEntry(frame, width=80, justify="center")
        self.end_entry.pack(side="left", padx=10)

        self.apply_cut_button = ctk.CTkButton(
            frame, text=self.languages[self.current_lang]["apply_cut"]
        )
        self.apply_cut_button.pack(side="left", padx=10)

    def create_audio_controls_frame(self):
        frame = ctk.CTkFrame(self.control_frame, fg_color=self.medium_blue)
        frame.pack(fill="x", pady=10)

        for label_text, attr_name, from_, to_, default in [
            ("volume", "volume_slider", -20, 20, 0),
            ("speed", "speed_slider", 0.5, 2.0, 1.0),
            ("pitch", "pitch_slider", -12, 12, 0),
        ]:
            sub_frame = ctk.CTkFrame(frame, fg_color=self.medium_blue)
            sub_frame.pack(side="left", fill="x", expand=True, padx=10)

            label = ctk.CTkLabel(
                sub_frame,
                text=self.languages[self.current_lang][label_text],
                text_color=self.text_color,
            )
            label.pack(side="left", padx=10)

            slider = ctk.CTkSlider(sub_frame, from_=from_, to=to_)
            slider.set(default)
            slider.pack(side="left", fill="x", expand=True, padx=10)

            # Save label and slider to instance attributes
            setattr(self, f"{label_text}_label", label)
            setattr(self, attr_name, slider)

        self.apply_all_button = ctk.CTkButton(
            frame, text=self.languages[self.current_lang]["apply"]
        )
        self.apply_all_button.pack(side="right", padx=10)

    def create_effects_frame(self):
        main_frame = ctk.CTkFrame(self.control_frame, fg_color=self.medium_blue)
        main_frame.pack(fill="x", pady=10)

        self.eq_frame = ctk.CTkFrame(main_frame, fg_color=self.light_blue)
        self.eq_label = ctk.CTkLabel(
            self.eq_frame,
            text=self.languages[self.current_lang]["eq"],
            text_color=self.text_color,
        )
        self.eq_label.pack(side="top", padx=10, pady=5)
        self.eq_frame.pack(fill="x", pady=10)

        for label_text, attr_name in [
            ("bass", "bass_slider"),
            ("mid", "mid_slider"),
            ("treble", "treble_slider"),
        ]:
            sub_frame = ctk.CTkFrame(self.eq_frame, fg_color=self.medium_blue)
            sub_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)

            label = ctk.CTkLabel(
                sub_frame,
                text=self.languages[self.current_lang][label_text],
                text_color=self.text_color,
            )
            label.pack(side="top")

            slider = ctk.CTkSlider(sub_frame, from_=-12, to=12)
            slider.pack(side="top", fill="x", expand=True)
            setattr(self, attr_name, slider)
            setattr(self, f"{label_text}_label", label)

        effects_frame = ctk.CTkFrame(main_frame, fg_color=self.light_blue)
        effects_frame.pack(fill="x", pady=5)

        for label_text, attr_name in [
            ("reverb", "reverb_button"),
            ("echo", "echo_button"),
            ("fade", "fade_button"),
            ("vocal", "vocal_button"),
        ]:
            button = ctk.CTkButton(
                effects_frame,
                text=self.languages[self.current_lang][label_text],
                corner_radius=20,
            )
            button.pack(side="left", padx=10, fill="x", expand=True)
            setattr(self, attr_name, button)
            setattr(self, f"{label_text}_button", button)

        playback_frame = ctk.CTkFrame(main_frame, fg_color=self.light_blue)
        playback_frame.pack(fill="x", pady=5)

        for label_text, attr_name in [
            ("preview", "preview_button"),
            ("stop", "stop_button"),
        ]:
            button = ctk.CTkButton(
                playback_frame,
                text=self.languages[self.current_lang][label_text],
                corner_radius=20,
            )
            button.pack(side="left", padx=10, fill="x", expand=True)
            setattr(self, attr_name, button)

    def bind_button_events(self):
        if self.controller is not None:
            self.load_button.configure(command=self.controller.load_file)
            self.export_button.configure(command=self.controller.export_audio)
            if hasattr(self.controller, "undo"):
                self.undo_button.configure(command=self.controller.undo)
            else:
                print("Warning: undo method not found in AudioController")
            if hasattr(self.controller, "redo"):
                self.redo_button.configure(command=self.controller.redo)
            else:
                print("Warning: redo method not found in AudioController")
            self.apply_cut_button.configure(command=self.controller.cut_audio)
            self.apply_all_button.configure(command=self.controller.apply_all)
            self.reverb_button.configure(command=self.controller.toggle_reverb)
            self.echo_button.configure(command=self.controller.toggle_echo)
            self.fade_button.configure(command=self.controller.toggle_fade)
            self.vocal_button.configure(command=self.controller.separate_vocal)
            self.preview_button.configure(command=self.controller.preview_audio)
            self.stop_button.configure(command=self.controller.stop_preview)
            self.preview_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    def start_progress(self):
        self.progress["value"] = 0
        self.progress.start()

    def stop_progress(self):
        self.progress.stop()
        self.progress["value"] = 100
        self.progress.set(100)

    def get_export_format(self):
        return self.format_combobox.get()

    def set_cut_defaults(self, duration):
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.start_entry.insert(0, "0.000")
        self.end_entry.insert(0, f"{duration:.3f}")

    def update_file_info(self, duration, channels, sample_rate, bitrate, metadata):
        info = (
            f"Thời lượng: {duration:.2f}s | Kênh: {channels} | Tần số: {sample_rate} Hz | "
            f"Bitrate: {bitrate/1000:.1f} kbps | Tựa đề: {metadata['title']} | "
            f"Nghệ sĩ: {metadata['artist']} | Kích thước: {metadata['size']:.2f} MB"
            if self.current_lang == "vi"
            else f"Duration: {duration:.2f}s | Channels: {channels} | Sample Rate: {sample_rate} Hz | "
            f"Bitrate: {bitrate/1000:.1f} kbps | Title: {metadata['title']} | "
            f"Artist: {metadata['artist']} | Size: {metadata['size']:.2f} MB"
        )
        self.file_info_label.configure(text=info)
