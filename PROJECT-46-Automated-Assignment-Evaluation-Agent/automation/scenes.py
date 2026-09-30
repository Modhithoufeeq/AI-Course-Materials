"""Scene model + loader for the automated code-walkthrough pipeline."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .paths import CONFIG_FILE, REPO_ROOT


@dataclass
class SceneAction:
    """An optional on-screen action to perform while a scene is live."""

    type: str = "terminal"  # "terminal" | "browser"
    command: str = ""
    cwd: str = "."
    delay_after: float = 3.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneAction":
        return cls(
            type=data.get("type", "terminal"),
            command=data.get("command", ""),
            cwd=data.get("cwd", "."),
            delay_after=float(data.get("delay_after", 3.0)),
        )


@dataclass
class Scene:
    id: str
    title: str
    narration: str
    file: Optional[str] = None
    secondary_file: Optional[str] = None
    focus_line: Optional[int] = None
    scroll_lines: int = 0
    scroll_speed: float = 0.35
    min_duration: float = 15.0
    hold_seconds: float = 2.0
    show_explorer: bool = False
    action: Optional[SceneAction] = None

    @property
    def word_count(self) -> int:
        return len(self.narration.split())

    @property
    def narration_estimate_seconds(self) -> float:
        """Rough spoken duration at the configurable default pace."""
        return max(4.0, self.word_count / 150.0 * 60.0)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        action = SceneAction.from_dict(data["action"]) if data.get("action") else None
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            narration=str(data["narration"]),
            file=data.get("file"),
            secondary_file=data.get("secondary_file"),
            focus_line=data.get("focus_line"),
            scroll_lines=int(data.get("scroll_lines", 0)),
            scroll_speed=float(data.get("scroll_speed", 0.35)),
            min_duration=float(data.get("min_duration", 15.0)),
            hold_seconds=float(data.get("hold_seconds", 2.0)),
            show_explorer=bool(data.get("show_explorer", False)),
            action=action,
        )


@dataclass
class Walkthrough:
    project_title: str
    tagline: str
    channel_name: str
    tts_voice: str
    tts_rate: str
    default_wpm: float
    inter_scene_gap: float
    open_file_seconds: float
    scroll_speed: float
    fps: int
    crf: int
    preset: str
    resolution: List[int]
    scenes: List[Scene] = field(default_factory=list)

    @property
    def total_narration_seconds(self) -> float:
        return sum(s.narration_estimate_seconds for s in self.scenes)

    def scene(self, scene_id: str) -> Optional[Scene]:
        for s in self.scenes:
            if s.id == scene_id:
                return s
        return None

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Walkthrough":
        cfg_path = Path(path) if path else CONFIG_FILE
        with cfg_path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)

        self = cls(
            project_title=str(raw.get("project_title", "AutoEval AI")),
            tagline=str(raw.get("tagline", "")),
            channel_name=str(raw.get("channel_name", "My Channel")),
            tts_voice=str(raw.get("tts_voice", "en-US-JennyNeural")),
            tts_rate=str(raw.get("tts_rate", "+0%")),
            default_wpm=float(raw.get("default_wpm", 150.0)),
            inter_scene_gap=float(raw.get("inter_scene_gap", 0.8)),
            open_file_seconds=float(raw.get("open_file_seconds", 3.0)),
            scroll_speed=float(raw.get("scroll_speed", 0.35)),
            fps=int(raw.get("fps", 30)),
            crf=int(raw.get("crf", 18)),
            preset=str(raw.get("preset", "veryfast")),
            resolution=list(raw.get("resolution", [1920, 1080])),
            scenes=[Scene.from_dict(s) for s in raw.get("scenes", [])],
        )
        self.narration_estimate_seconds = (
            self.total_narration_seconds  # kept for API symmetry
        )
        self.validate()
        return self

    def validate(self) -> None:
        ids = [s.id for s in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("Scene ids must be unique.")
        if not self.scenes:
            raise ValueError("Walkthrough config contains no scenes.")
        for s in self.scenes:
            if not s.narration.strip():
                raise ValueError(f"Scene '{s.id}' has empty narration.")
            if s.file and not (REPO_ROOT / s.file).exists():
                print(f"[warn] scene '{s.id}' references missing file: {s.file}")
            if s.secondary_file and not (REPO_ROOT / s.secondary_file).exists():
                print(f"[warn] scene '{s.id}' references missing secondary file: {s.secondary_file}")
            if s.action and s.action.type not in ("terminal", "browser"):
                raise ValueError(
                    f"Scene '{s.id}' uses unsupported action type '{s.action.type}'."
                )