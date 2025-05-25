import threading
from tkinter import messagebox, filedialog
import tkinter as tk
import os

class AudioExportController:
    def export_audio(self):
        if self.is_processing:
            messagebox.showwarning(
                "Cảnh báo" if self.main_view.current_lang == "vi" else "Warning",
                "Đang xử lý, vui lòng chờ!" if self.main_view.current_lang == "vi" else "Processing, please wait!"
            )
            return
        if self.audio is None:
            messagebox.showwarning(
                "Cảnh báo" if self.main_view.current_lang == "vi" else "Warning",
                "Vui lòng tải file âm thanh trước" if self.main_view.current_lang == "vi" else "Please load an audio file first"
            )
            return
        format = self.control_panel.get_export_format()
        output_path = tk.filedialog.asksaveasfilename(defaultextension=f".{format}", filetypes=[(f"{format.upper()} files", f"*.{format}")])
        if output_path:
            self.is_processing = True
            self.control_panel.start_progress()
            self.main_view.update_status("Đang xuất âm thanh..." if self.main_view.current_lang == "vi" else "Exporting audio...")
            threading.Thread(target=self._export_audio_thread, args=(output_path, format), daemon=True).start()

    def _export_audio_thread(self, output_path, format):
        try:
            self.exporter.export_audio(self.audio, format, output_path, self.file_path, self.sample_rate, self.channels)
            self.main_view.root.after(0, lambda: self.main_view.update_status(
                f"Đã xuất: {os.path.basename(output_path)}" if self.main_view.current_lang == "vi" else f"Exported: {os.path.basename(output_path)}"
            ))
        except Exception as e:
            self.main_view.root.after(0, lambda: messagebox.showerror(
                "Lỗi" if self.main_view.current_lang == "vi" else "Error", str(e)
            ))
        finally:
            self.is_processing = False
            self.main_view.root.after(0, self.control_panel.stop_progress)