from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SettingsManager:
    DEFAULTS = {
        "sfx": True,
        "timers": True,
        "theme": "sepia",
        "strict_accents": False,
        "study_countdown": 0,
    }

    def __init__(self, path: str | Path = "settings.json"):
        self.path = Path(path)
        self._settings = dict(self.DEFAULTS)
        self.load()

    def load(self) -> dict[str, Any]:
        if self.path.exists():
            self._settings.update(json.loads(self.path.read_text(encoding="utf-8")))
        return self._settings

    def save(self) -> None:
        self.path.write_text(json.dumps(self._settings, indent=2), encoding="utf-8")

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value
        self.save()

    @property
    def data(self) -> dict[str, Any]:
        return self._settings
