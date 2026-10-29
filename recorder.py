import os
import subprocess
import tempfile
from datetime import datetime

import cv2
import imageio.plugins.ffmpeg as ffmpeg_plugin

import config

_FFMPEG = ffmpeg_plugin.get_exe()


def save_clip(frames: list, frame_size: tuple[int, int] | None = None, output_dir: str | None = None) -> str:
    if not frames:
        raise ValueError("Buffer vazio — nenhum frame para salvar.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"replay_{timestamp}.mp4"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        final_path = os.path.join(output_dir, filename)
    else:
        final_path = os.path.join(tempfile.gettempdir(), filename)

    if frame_size is None:
        h, w = frames[0].shape[:2]
        frame_size = (w, h)

    # Salva frames em mp4v temporário e re-encoda para H.264 com ffmpeg
    tmp_path = final_path + ".tmp.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(tmp_path, fourcc, config.FPS, frame_size)
    for frame in frames:
        writer.write(frame)
    writer.release()

    result = subprocess.run([
        _FFMPEG, "-y", "-i", tmp_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-movflags", "+faststart",
        final_path,
    ], capture_output=True)
    os.remove(tmp_path)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg falhou: {result.stderr.decode()[-300:]}")

    size_mb = os.path.getsize(final_path) / (1024 * 1024)
    print(f"Clip salvo: {final_path} ({len(frames)} frames, {size_mb:.1f} MB)")
    return final_path
