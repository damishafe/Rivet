import subprocess
from pathlib import Path


def assemble_scenes(clip_paths: list[str], out_path: Path, audio_path: str | None = None) -> None:
    if not clip_paths:
        raise ValueError("no clips to assemble")
    concat_file = out_path.with_suffix(".txt")
    concat_file.write_text("".join(f"file '{path}'\n" for path in clip_paths))
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
    ]
    if audio_path is not None:
        command += ["-i", audio_path, "-c:a", "aac", "-shortest"]
    command += [
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]
    subprocess.run(command, check=True, capture_output=True)
    concat_file.unlink(missing_ok=True)
