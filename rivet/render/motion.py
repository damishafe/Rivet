import subprocess
from pathlib import Path

CANVAS = (1080, 1920)
FPS = 24
ZOOM_MAX = 1.10
PRESCALE = 1.25


def _filter(motion: str, frames: int) -> str:
    step = (ZOOM_MAX - 1.0) / max(frames, 1)
    center_x = "iw/2-(iw/zoom/2)"
    center_y = "ih/2-(ih/zoom/2)"
    if motion == "pan_up":
        expr = (f"z='{ZOOM_MAX}':x='{center_x}':y='(ih-ih/zoom)*(1-on/{frames})'")
    elif motion == "pan_down":
        expr = (f"z='{ZOOM_MAX}':x='{center_x}':y='(ih-ih/zoom)*(on/{frames})'")
    else:
        expr = f"z='min(zoom+{step:.6f},{ZOOM_MAX})':x='{center_x}':y='{center_y}'"
    width, height = CANVAS
    scaled_w, scaled_h = round(width * PRESCALE), round(height * PRESCALE)
    return (
        f"scale={scaled_w}:{scaled_h},"
        f"zoompan={expr}:d={frames}:s={width}x{height}:fps={FPS}"
    )


def animate_still(
    still_path: str, out_path: Path, duration_s: float, motion: str = "zoom_in"
) -> None:
    frames = max(1, round(duration_s * FPS))
    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        still_path,
        "-vf",
        _filter(motion, frames),
        "-t",
        f"{duration_s}",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(out_path),
    ]
    subprocess.run(command, check=True, capture_output=True)
