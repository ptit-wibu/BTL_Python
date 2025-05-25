import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES
import customtkinter as ctk


class MainView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.languages = {
            "vi": {
                "title": "Audio Editor - L.N.Duc and P.C.Huan",
                "status": "Vui lòng tải file âm thanh",
                "language": "Ngôn ngữ:",
                "load": "Tải âm thanh",
                "format": "Định dạng:",
                "export": "Xuất âm thanh",
                "cut": "Cắt (giây):",
                "apply_cut": "Áp dụng cắt",
                "volume": "Âm lượng (dB):",
                "speed": "Tốc độ:",
                "pitch": "Cao độ (semitones):",
                "apply": "Áp dụng tất cả",
                "reverb": "Thêm Reverb",
                "echo": "Thêm Echo",
                "fade": "Fade In/Out",
                "eq": "Equalizer",
                "vocal": "Tách giọng hát",
                "preview": "Nghe thử",
                "stop": "Dừng",
                "undo": "Undo",
                "redo": "Redo",
                "control_frame": "Điều khiển âm thanh",
                "waveform": "Dạng sóng",
                "file_info": "Thông tin file: Chưa tải file",
                "timeline": "Thanh thời gian:",
                "bass": "Bass:",
                "mid": "Mid:",
                "treble": "Treble:",
                "duration": "Thời lượng",
                "channels": "Kênh",
                "sample_rate": "Tần số",
                "bitrate": "Bitrate",
                "title_label": "Tựa đề",
                "artist": "Nghệ sĩ",
                "size": "Kích thước",
            },
            "en": {
                "title": "Audio Editor - L.N.Duc and P.C.Huan",
                "status": "Please load an audio file",
                "language": "Language:",
                "load": "Load Audio",
                "format": "Format:",
                "export": "Export Audio",
                "cut": "Cut (seconds):",
                "apply_cut": "Apply Cut",
                "volume": "Volume (dB):",
                "speed": "Speed:",
                "pitch": "Pitch (semitones):",
                "apply": "Apply All",
                "reverb": "Add Reverb",
                "echo": "Add Echo",
                "fade": "Fade In/Out",
                "eq": "Equalizer",
                "vocal": "Separate Vocal",
                "preview": "Preview",
                "stop": "Stop",
                "undo": "Undo",
                "redo": "Redo",
                "control_frame": "Audio Controls",
                "waveform": "Waveform",
                "file_info": "File Info: No file loaded",
                "timeline": "Timeline:",
                "bass": "Bass:",
                "mid": "Mid:",
                "treble": "Treble:",
                "duration": "Duration",
                "channels": "Channels",
                "sample_rate": "Sample Rate",
                "bitrate": "Bitrate",
                "title_label": "Title",
                "artist": "Artist",
                "size": "Size",
            },
        }
        self.current_lang = "vi"

        # Define theme colors
        self.dark_blue = "#0A1E3D"
        self.medium_blue = "#0C2655"
        self.light_blue = "#1C3F75"
        self.accent_green = "#00FF99"
        self.accent_cyan = "#00FFFF"
        self.text_color = "white"

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.title(self.languages[self.current_lang]["title"])
        #self.root.geometry("1000x600")
        #self.root.state("zoomed")
        screen_width = self.root.winfo_screenwidth()-20
        screen_height = self.root.winfo_screenheight()-80
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.configure(bg=self.dark_blue)

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.dark_blue)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_top_controls()

        self.status = ctk.CTkLabel(
            self.main_frame,
            text=self.languages[self.current_lang]["status"],
            text_color="white",
            fg_color=self.light_blue,
            height=30,
            anchor="center",
        )
        self.status.pack(side="bottom", fill="x", pady=5)

    def create_top_controls(self):
        top_frame = ctk.CTkFrame(self.main_frame, fg_color=self.dark_blue)
        top_frame.pack(side="top", fill="x", pady=0)

        # Right side language selection
        lang_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        lang_frame.pack(side="right", padx=5)

        self.lang_label = ctk.CTkLabel(
            lang_frame,
            text=self.languages[self.current_lang]["language"],
            text_color="white",
        )
        self.lang_label.pack(side="left", padx=5)

        self.lang_combobox = ctk.CTkOptionMenu(
            lang_frame,
            values=["Tiếng Việt", "English"],
            fg_color=self.medium_blue,
            button_color=self.light_blue,
            text_color="white",
        )
        self.lang_combobox.set("Tiếng Việt")
        self.lang_combobox.pack(side="left", padx=5)

    def bind_drop_event(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.controller.handle_drop)

    def bind_language_event(self):
        self.lang_combobox.configure(command=self.controller.change_language)

    def update_status(self, message):
        self.status.configure(text=message)
