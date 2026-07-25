import subprocess
from pathlib import Path


def _srt_time(seconds: float) -> str:
    total_ms = round(seconds * 1000)
    hours, total_ms = divmod(total_ms, 3_600_000)
    minutes, total_ms = divmod(total_ms, 60_000)
    secs, millis = divmod(total_ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(cues: list[tuple[str, float, float]], out_path: Path) -> None:
    blocks = [
        f"{index}\n{_srt_time(start)} --> {_srt_time(end)}\n{text}\n"
        for index, (text, start, end) in enumerate(cues, start=1)
        if text
    ]
    out_path.write_text("\n".join(blocks))


def mix_narration(video_path: str, clips: list[tuple[str, int]], out_path: Path) -> None:
    if not clips:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-c", "copy", str(out_path)],
            check=True,
            capture_output=True,
        )
        return
    inputs: list[str] = ["-i", video_path]
    filters: list[str] = []
    labels: list[str] = []
    for index, (wav, offset_ms) in enumerate(clips, start=1):
        inputs += ["-i", wav]
        filters.append(f"[{index}]adelay={offset_ms}|{offset_ms}[a{index}]")
        labels.append(f"[a{index}]")
    filter_complex = ";".join(filters) + ";" + "".join(labels) + f"amix=inputs={len(clips)}:normalize=0[a]"
    subprocess.run(
        [
            "ffmpeg", "-y", *inputs, "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
            str(out_path),
        ],
        check=True,
        capture_output=True,
    )


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
