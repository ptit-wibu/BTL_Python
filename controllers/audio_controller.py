import threading
import multiprocessing as mp
from tkinter import messagebox
import numpy as np
import tkinter as tk
import logging

from controllers.audio_loader_controller import AudioLoaderController
from controllers.audio_edit_controller import AudioEditController
from controllers.audio_vocal_controller import AudioVocalController
from controllers.audio_preview_controller import AudioPreviewController
from controllers.audio_export_controller import AudioExportController
from controllers.audio_utils_controller import AudioUtilsController

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioController(
    AudioLoaderController,
    AudioEditController,
    AudioVocalController,
    AudioPreviewController,
    AudioExportController,
    AudioUtilsController,
):
    def __init__(
        self,
        loader,
        processor,
        exporter,
        main_view,
        control_panel,
        waveform_view,
        effect_controller,
    ):
        self.loader = loader
        self.processor = processor
        self.exporter = exporter
        self.main_view = main_view
        self.control_panel = control_panel
        self.waveform_view = waveform_view
        self.effect_controller = effect_controller
        self.project_controller = None  
        self.audio = None
        self.original_audio = None
        self.audio_array = None
        self.sample_rate = None
        self.channels = None
        self.file_path = None
        self.duration = 0
        self.bitrate = None
        self.metadata = {}
        self.preview_process = None
        self.undo_stack = []
        self.redo_stack = []
        self.beat_times = None
        self.tempo = None
        self.is_processing = False
        self.is_seeking = False
        self.queue = mp.Queue()
        self.volume_gain = 0.0
        self.speed = 1.0
        self.pitch_steps = 0.0
        self.reverb_enabled = False
        self.echo_enabled = False
        self.fade_enabled = False
        self.bass_gain = 0.0
        self.mid_gain = 0.0
        self.treble_gain = 0.0
        self._after_id = None
        self._apply_lock = threading.Lock()
        self.current_position = 0
        # self.last_timeline_position = 0
        self.temp_preview_file = None
        self.waveform_view.timeline_slider.bind("<ButtonPress-1>", self.start_seeking)
        self.waveform_view.timeline_slider.bind("<ButtonRelease-1>", self.seek_audio)
