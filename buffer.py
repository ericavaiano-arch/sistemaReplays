import threading
import time
from collections import deque

import cv2

import config


def find_camera() -> int:
    if config.CAMERA_INDEX is not None:
        return config.CAMERA_INDEX
    for index in range(5):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                return index
    raise RuntimeError("Nenhuma câmera encontrada. Verifique se a Iriun Webcam está ativa.")


class FrameBuffer:
    def __init__(self) -> None:
        capacity = config.FPS * config.BUFFER_SECONDS
        self._frames: deque = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self.frame_size: tuple[int, int] | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def snapshot(self) -> list:
        with self._lock:
            return list(self._frames)

    def _capture_loop(self) -> None:
        index = find_camera()
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera no índice {index}.")

        # Tenta configurar a resolução e FPS solicitados
        cap.set(cv2.CAP_PROP_FPS, config.FPS)

        print(f"Câmera iniciada no índice {index}. Capturando a {config.FPS} fps...")

        frame_interval = 1.0 / config.FPS

        while self._running:
            t_start = time.monotonic()
            ret, frame = cap.read()
            if not ret:
                time.sleep(frame_interval)
                continue

            if self.frame_size is None:
                h, w = frame.shape[:2]
                self.frame_size = (w, h)

            with self._lock:
                self._frames.append(frame)

            elapsed = time.monotonic() - t_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        cap.release()
