import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from PIL import Image

from rivet.render.assemble import assemble_scenes, mix_narration
from rivet.render.motion import animate_still

ffmpeg_missing = shutil.which("ffmpeg") is None


def _duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def _dimensions(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0", str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    width, height = result.stdout.strip().split("x")
    return int(width), int(height)


@pytest.mark.skipif(ffmpeg_missing, reason="requires ffmpeg")
def test_animate_produces_vertical_clip(tmp_path: Path) -> None:
    still = tmp_path / "still.png"
    Image.new("RGB", (1080, 1920), (40, 40, 44)).save(still)
    clip = tmp_path / "clip.mp4"
    animate_still(str(still), clip, 2.0, "zoom_in")
    assert clip.exists()
    assert abs(_duration(clip) - 2.0) < 0.3
    assert _dimensions(clip) == (1080, 1920)


@pytest.mark.skipif(ffmpeg_missing, reason="requires ffmpeg")
def test_assemble_sums_durations(tmp_path: Path) -> None:
    still = tmp_path / "still.png"
    Image.new("RGB", (1080, 1920), (40, 40, 44)).save(still)
    clips = []
    for index, duration in enumerate([1.0, 1.5]):
        clip = tmp_path / f"clip{index}.mp4"
        animate_still(str(still), clip, duration, "pan_up")
        clips.append(str(clip))
    final = tmp_path / "final.mp4"
    assemble_scenes(clips, final)
    assert abs(_duration(final) - 2.5) < 0.4
    assert _dimensions(final) == (1080, 1920)


def test_assemble_rejects_empty(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        assemble_scenes([], tmp_path / "x.mp4")


@pytest.mark.skipif(ffmpeg_missing, reason="requires ffmpeg")
def test_mix_narration_keeps_video_duration(tmp_path: Path) -> None:
    still = tmp_path / "still.png"
    Image.new("RGB", (1080, 1920), (40, 40, 44)).save(still)
    video = tmp_path / "video.mp4"
    animate_still(str(still), video, 3.0, "zoom_in")
    wav = tmp_path / "narration.wav"
    sf.write(wav, np.zeros(24000, dtype="float32"), 24000)
    out = tmp_path / "mixed.mp4"
    mix_narration(str(video), [(str(wav), 0)], out)
    assert abs(_duration(out) - 3.0) < 0.4
