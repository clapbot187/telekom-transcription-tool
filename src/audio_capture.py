import threading
import time
import wave
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Callable, Optional

import numpy as np
import sounddevice as sd


class AudioCapture:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration: float = 0.5
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(sample_rate * chunk_duration)

        self._recording: bool = False
        self._stream: Optional[sd.InputStream] = None
        self._thread: Optional[threading.Thread] = None
        self._audio_queue: Queue = Queue()
        self._recorded_frames: list = []
        self._on_audio_callback: Optional[Callable[[np.ndarray], None]] = None

    def set_audio_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        self._on_audio_callback = callback

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
        if status:
            print(f"Audio callback status: {status}")
        self._audio_queue.put(indata.copy())

    def _record_loop(self) -> None:
        while self._recording:
            try:
                data = self._audio_queue.get(timeout=0.1)
                self._recorded_frames.append(data)
                if self._on_audio_callback:
                    self._on_audio_callback(data)
            except Exception:
                continue

    def start_recording(self) -> bool:
        if self._recording:
            return False

        try:
            self._recorded_frames = []
            self._recording = True

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.chunk_samples,
                callback=self._audio_callback
            )
            self._stream.start()

            self._thread = threading.Thread(target=self._record_loop, daemon=True)
            self._thread.start()

            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            self._recording = False
            return False

    def stop_recording(self) -> Optional[Path]:
        if not self._recording:
            return None

        self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        return self._save_recording()

    def _save_recording(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recordings_dir = Path("recordings")
        recordings_dir.mkdir(exist_ok=True)

        filepath = recordings_dir / f"recording_{timestamp}.wav"

        if self._recorded_frames:
            audio_data = np.concatenate(self._recorded_frames, axis=0)
            audio_data = (audio_data * 32767).astype(np.int16)

            with wave.open(str(filepath), "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())

        return filepath

    def is_recording(self) -> bool:
        return self._recording
