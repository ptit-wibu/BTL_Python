import os
import tempfile
from pydub import AudioSegment
import pyaudio
import ffmpeg
import threading
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioExporter:
    def __init__(self, waveform_view=None, controller=None):
        self.is_previewing = False
        self.audio_process = None
        self.stream = None
        self.p = None
        self._lock = threading.Lock()
        self.waveform_view = waveform_view
        self.controller = controller
        self.total_bytes_played = 0
        self.bytes_per_sample = 4  # 32-bit float
        # self.temp_files = None

    def export_audio(
        self, audio_segment, format, output_path, input_path, sample_rate, channels
    ):
        """
        Xuất âm thanh sang định dạng được chỉ định (WAV, MP3, OGG, AAC, v.v.).
        Dùng pydub cho WAV và MP3, FFmpeg cho các định dạng khác.
        Sử dụng tempfile để tạo file tạm.
        """
        try:
            logging.info(f"Exporting audio to {output_path} as {format}")
            pydub_formats = ["wav", "mp3"]

            # Tạo file tạm bằng tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_wav = temp_file.name
                # Xuất file WAV tạm thời
                audio_segment.export(temp_wav, format="wav")
                logging.info(f"Created temporary WAV file: {temp_wav}")

                if format in pydub_formats:
                    # Dùng pydub để xuất trực tiếp
                    audio_segment.export(output_path, format=format)
                    logging.info(f"Exported directly using pydub to {output_path}")
                else:
                    # Dùng FFmpeg cho các định dạng khác (AAC, OGG, v.v.)
                    codec = {
                        "aac": "aac",
                        "ogg": "libvorbis",
                        "flac": "flac",
                        "m4a": "aac",
                        "wma": "wmav2",
                    }.get(format, format)
                    stream = ffmpeg.input(temp_wav)
                    stream = ffmpeg.output(
                        stream,
                        output_path,
                        format=format,
                        acodec=codec,
                        ar=sample_rate,
                        ac=channels,
                    )
                    ffmpeg.run(
                        stream,
                        overwrite_output=True,
                        capture_stdout=True,
                        capture_stderr=True,
                    )
                    logging.info(
                        f"Exported using FFmpeg to {output_path} with codec {codec}"
                    )

        except ffmpeg.Error as e:
            error_msg = f"FFmpeg error: {e.stderr.decode()}"
            logging.error(error_msg)
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            raise Exception(f"Error exporting audio: {error_msg}")
        except Exception as e:
            logging.error(f"Export error: {str(e)}")
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            raise Exception(f"Error exporting audio: {str(e)}")

    def preview_audio(self, file_path, sample_rate, channels, start, end):
        with self._lock:
            if self.is_previewing:
                return
            self.is_previewing = True
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                output=True,
            )

            bytes_per_second = sample_rate * channels * self.bytes_per_sample
            start_byte = int(self.controller.current_position * bytes_per_second)
            self.total_bytes_played = start_byte

            threading.Thread(
                target=self._preview_stream,
                args=(file_path, sample_rate, channels, start, end),
                daemon=True,
            ).start()
        except Exception as e:
            self.stop_preview(file_path, None)
            raise Exception(f"Error starting preview: {str(e)}")

    def _preview_stream(self, file_path, sample_rate, channels, current, duration):
        try:
            self.audio_process = (
                ffmpeg.input(file_path, ss=current, t=duration)
                .output(
                    "pipe:",
                    format="f32le",
                    acodec="pcm_f32le",
                    ac=channels,
                    ar=sample_rate,
                )
                .run_async(pipe_stdout=True)
            )
            chunk_size = 1024
            while self.is_previewing:
                data = self.audio_process.stdout.read(chunk_size)
                if not data:
                    break
                self.stream.write(data)
                if not self.controller.is_seeking:
                    self.total_bytes_played += len(data)
                    bytes_per_second = sample_rate * channels * self.bytes_per_sample
                    self.controller.current_position = (
                        self.total_bytes_played / bytes_per_second
                    )
            self.controller.stop_preview()
            #self.stop_preview(file_path, None)
        except Exception as e:
            logging.error(f"Preview error: {str(e)}")
            self.stop_preview(file_path, None)

    def stop_preview(self, file_path, audio_segment):
        with self._lock:
            self.is_previewing = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            if self.audio_process:
                self.audio_process.terminate()
                self.audio_process.wait()
                self.audio_process = None
            if self.p:
                self.p.terminate()
                self.p = None

            logging.info("Preview stopped in audio exporter")

    def get_preview_position(self):
        return 0
