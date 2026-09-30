"""Runtime configuration for the project.

The automation transfers `.enc` files verbatim (it never decrypts them). This
module therefore treats `.env.enc` / `settings.enc` as opaque, base64-obfuscated
secrets: it attempts to decode them and falls back to safe defaults whenever the
passphrase/format is unavailable. This keeps the demo runnable in a fresh Colab
runtime with zero setup.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SETTINGS: Dict[str, Any] = {
    "project_name": "Automated Assignment Evaluation Agent",
    "environment": "colab",
    "llm_provider": "deterministic",
    "default_model": "none (offline heuristic analysis)",
    "similarity_threshold_low": 0.20,
    "similarity_threshold_medium": 0.45,
    "similarity_threshold_high": 0.70,
}


def _decode_secret_file(relative_name: str) -> Dict[str, Any] | None:
    """Try to decode a base64-obfuscated secrets file. Returns None on failure
    (missing file, invalid base64, or not JSON) so the caller can fall back."""
    path = BASE_DIR / relative_name
    try:
        raw = path.read_bytes()
        decoded = base64.b64decode(raw).decode("utf-8")
        payload = json.loads(decoded)
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


class Settings:
    def __init__(self) -> None:
        merged: Dict[str, Any] = dict(DEFAULT_SETTINGS)

        # Optional secrets from the transferred, as-is `.enc` files.
        for secret_file in (".env.enc", "config/settings.enc"):
            decoded = _decode_secret_file(secret_file)
            if decoded:
                merged.update(decoded)

        # Real environment variables always win.
        for key, value in os.environ.items():
            if key in merged or key.lower() in {k.replace("_", "").lower() for k in merged}:
                merged[key] = value

        self.project_name = str(merged.get("project_name", DEFAULT_SETTINGS["project_name"]))
        self.environment = str(merged.get("environment", "colab"))
        self.llm_provider = str(merged.get("llm_provider", "deterministic"))
        self.default_model = str(merged.get("default_model", "offline heuristic"))
        self.similarity_low = float(merged.get("similarity_threshold_low", 0.20))
        self.similarity_medium = float(merged.get("similarity_threshold_medium", 0.45))
        self.similarity_high = float(merged.get("similarity_threshold_high", 0.70))
        self.secret_keys_loaded = [
            f for f in (".env.enc", "config/settings.enc")
            if (BASE_DIR / f).exists()
        ]

    def describe(self) -> str:
        return (
            f"project={self.project_name!r} env={self.environment} "
            f"llm={self.llm_provider} model={self.default_model}"
        )


settings = Settings()