"""Central path resolution + tool discovery for the video pipeline."""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOMATION_DIR = Path(__file__).resolve().parent
CONFIG_FILE = AUTOMATION_DIR / "walkthrough.json"

VIDEO_DIR = REPO_ROOT / "output" / "video"
AUDIO_DIR = VIDEO_DIR / "audio"
SCENES_DIR = VIDEO_DIR / "scenes"
DOCS_DIR = REPO_ROOT / "docs" / "video"

MARKERS_FILE = VIDEO_DIR / "markers.json"


def ensure_dirs() -> None:
    for d in (VIDEO_DIR, AUDIO_DIR, SCENES_DIR, DOCS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def find_ffmpeg() -> str | None:
    """Locate a usable ffmpeg binary.

    Priority:
      1. a repo-local copy under tools/ffmpeg (manual install)
      2. the binary bundled by the imageio-ffmpeg pip wheel
      3. any ffmpeg on PATH
    """
    local = REPO_ROOT / "tools" / "ffmpeg"
    if local.exists():
        hits = sorted(local.rglob("ffmpeg.exe"))
        if hits:
            return str(hits[0])

    try:
        import imageio_ffmpeg  # type: ignore

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return str(exe)
    except Exception:
        pass

    return shutil.which("ffmpeg")


def find_code_cli() -> str | None:
    """Locate the VS Code 'code' CLI so the driver can open the project."""
    for candidate in ("code", "code.cmd", "code.exe"):
        where = shutil.which(candidate)
        if where:
            return where
    return None