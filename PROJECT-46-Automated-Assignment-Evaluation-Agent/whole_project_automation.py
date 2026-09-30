"""Record a guided VS Code walkthrough of this repository on Windows.

The recorder captures the primary monitor with mss and writes an MP4 through
OpenCV. It does not require OBS or FFmpeg, but it does require VS Code to be
installed and the Python packages listed in ``VIDEO_REQUIREMENTS``.
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
import time
from pathlib import Path


VIDEO_REQUIREMENTS = ("cv2", "mss", "numpy", "pyautogui")
DEFAULT_OUTPUT = "project_automation.mp4"
DEFAULT_FPS = 12

WALKTHROUGH_FILES = (
    "README.md",
    "project/main.py",
    "project/src/app.py",
    "project/agents/agent.py",
    "backend/app/agents/orchestrator.py",
    "frontend/src/App.jsx",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(DEFAULT_OUTPUT),
        help="MP4 path relative to the repository root (default: project_automation.mp4).",
    )
    parser.add_argument(
        "--seconds-per-file",
        type=float,
        default=12,
        help="How long each file stays visible (default: 12 seconds).",
    )
    parser.add_argument(
        "--startup-delay",
        type=float,
        default=5,
        help="Seconds to move the mouse away and prepare before capture (default: 5).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate files and dependencies without opening VS Code or recording.",
    )
    return parser.parse_args()


def validate(root: Path) -> list[str]:
    missing = [name for name in VIDEO_REQUIREMENTS if not importlib.util.find_spec(name)]
    missing_files = [path for path in WALKTHROUGH_FILES if not (root / path).is_file()]
    if missing_files:
        raise FileNotFoundError(
            "Walkthrough files are missing: " + ", ".join(missing_files)
        )
    return missing


def open_file_in_vscode(relative_path: str) -> None:
    import pyautogui

    pyautogui.hotkey("ctrl", "p")
    time.sleep(0.6)
    pyautogui.write(relative_path, interval=0.01)
    pyautogui.press("enter")
    time.sleep(1.5)


def record(root: Path, output: Path, seconds_per_file: float, startup_delay: float) -> None:
    import cv2
    import numpy as np
    import pyautogui
    from mss import MSS

    code_command = shutil.which("code")
    if not code_command:
        raise RuntimeError("The VS Code CLI ('code') was not found on PATH.")

    output = output if output.is_absolute() else root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.Popen([code_command, "--reuse-window", str(root)], stdout=subprocess.DEVNULL)
    time.sleep(4)

    pyautogui.FAILSAFE = True
    pyautogui.moveTo(10, 10, duration=0.2)
    print(f"Recording starts in {startup_delay:g} seconds. Move the mouse to the top-left to abort.")
    time.sleep(startup_delay)

    with MSS() as screen:
        monitor = screen.monitors[1]
        width = monitor["width"] - monitor["width"] % 2
        height = monitor["height"] - monitor["height"] % 2
        writer = cv2.VideoWriter(
            str(output),
            cv2.VideoWriter_fourcc(*"mp4v"),
            DEFAULT_FPS,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError(f"Could not create video writer for {output}")

        try:
            for relative_path in WALKTHROUGH_FILES:
                print(f"Showing {relative_path}")
                open_file_in_vscode(relative_path)
                frame_count = max(1, round(seconds_per_file * DEFAULT_FPS))
                for _ in range(frame_count):
                    frame = np.asarray(screen.grab(monitor))[:, :, :3]
                    writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    time.sleep(1 / DEFAULT_FPS)
        finally:
            writer.release()

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Capture finished without producing a non-empty MP4.")
    print(f"Video written to {output} ({output.stat().st_size:,} bytes).")


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    missing = validate(root)
    if missing:
        print("Missing Python packages: " + ", ".join(missing))
        print("Install them with: python -m pip install pyautogui mss opencv-python numpy")
        return 1
    if args.seconds_per_file <= 0 or args.startup_delay < 0:
        print("--seconds-per-file must be positive and --startup-delay cannot be negative.")
        return 2
    if args.dry_run:
        print(f"Dry run passed: {len(WALKTHROUGH_FILES)} files are ready under {root}.")
        return 0
    try:
        record(root, args.output, args.seconds_per_file, args.startup_delay)
    except KeyboardInterrupt:
        print("Capture cancelled.")
        return 130
    except Exception as error:
        print(f"Capture failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())