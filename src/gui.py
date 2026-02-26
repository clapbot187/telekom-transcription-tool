import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable, Optional

from .api_client import APIClient
from .audio_capture import AudioCapture
from .config import Config


class TranscriptionGUI:
    def __init__(self, config: Config):
        self.config = config
        self.audio_capture = AudioCapture(
            sample_rate=config.sample_rate,
            channels=config.channels,
            chunk_duration=config.chunk_duration
        )
        self.api_client = APIClient(config)

        self.root = tk.Tk()
        self.root.title("Telekom Transcription Tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self._recording = False
        self._current_audio_path: Optional[Path] = None
        self._transcription_callback: Optional[Callable[[str], None]] = None

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        self.start_btn = ttk.Button(
            control_frame,
            text="Start Recording",
            command=self._on_start
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)

        self.stop_btn = ttk.Button(
            control_frame,
            text="Stop Recording",
            command=self._on_stop,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=1, sticky=tk.W)

        result_frame = ttk.LabelFrame(main_frame, text="Transcription", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.transcribe_btn = ttk.Button(
            actions_frame,
            text="Transcribe",
            command=self._on_transcribe,
            state=tk.DISABLED
        )
        self.transcribe_btn.pack(side=tk.LEFT, padx=5)

        self.enhance_btn = ttk.Button(
            actions_frame,
            text="Enhance with GPT",
            command=self._on_enhance,
            state=tk.DISABLED
        )
        self.enhance_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            actions_frame,
            text="Clear",
            command=self._on_clear
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            actions_frame,
            text="Copy to Clipboard",
            command=self._on_copy
        ).pack(side=tk.RIGHT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_start(self) -> None:
        if not self.config.is_valid:
            messagebox.showerror(
                "Configuration Error",
                "API key not configured. Please set up config.json or TRANSCRIPTION_API_KEY environment variable."
            )
            return

        if self.audio_capture.start_recording():
            self._recording = True
            self._current_audio_path = None
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.transcribe_btn.config(state=tk.DISABLED)
            self.enhance_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Recording...")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "Recording audio...")
        else:
            messagebox.showerror("Error", "Failed to start recording. Check your microphone.")

    def _on_stop(self) -> None:
        self._current_audio_path = self.audio_capture.stop_recording()
        self._recording = False

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Recording saved")
        self.result_text.delete(1.0, tk.END)

        if self._current_audio_path:
            self.result_text.insert(1.0, f"Audio saved to: {self._current_audio_path}\n\nClick 'Transcribe' to process.")
            self.transcribe_btn.config(state=tk.NORMAL)

    def _on_transcribe(self) -> None:
        if not self._current_audio_path:
            return

        self.status_label.config(text="Transcribing...")
        self.transcribe_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            text = self.api_client.whisper.transcribe(self._current_audio_path)
            self.result_text.delete(1.0, tk.END)

            if text:
                self.result_text.insert(1.0, text)
                self.status_label.config(text="Transcription complete")
                self.enhance_btn.config(state=tk.NORMAL)

                if self._transcription_callback:
                    self._transcription_callback(text)
            else:
                self.result_text.insert(1.0, "Transcription failed. Please try again.")
                self.status_label.config(text="Transcription failed")
                self.transcribe_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"Error: {str(e)}")
            self.status_label.config(text="Error occurred")
            self.transcribe_btn.config(state=tk.NORMAL)

    def _on_enhance(self) -> None:
        current_text = self.result_text.get(1.0, tk.END).strip()
        if not current_text:
            return

        self.status_label.config(text="Enhancing with GPT...")
        self.enhance_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            enhanced = self.api_client.gpt.enhance(current_text)

            if enhanced:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, enhanced)
                self.status_label.config(text="Enhancement complete")
            else:
                self.status_label.config(text="Enhancement failed")
                self.enhance_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"Enhancement error: {str(e)}")
            self.status_label.config(text="Enhancement error")
            self.enhance_btn.config(state=tk.NORMAL)

    def _on_clear(self) -> None:
        self.result_text.delete(1.0, tk.END)
        self._current_audio_path = None
        self.status_label.config(text="Ready")
        self.transcribe_btn.config(state=tk.DISABLED)
        self.enhance_btn.config(state=tk.DISABLED)

    def _on_copy(self) -> None:
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_label.config(text="Copied to clipboard")

    def _on_close(self) -> None:
        if self._recording:
            self.audio_capture.stop_recording()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()

    def set_transcription_callback(self, callback: Callable[[str], None]) -> None:
        self._transcription_callback = callback
