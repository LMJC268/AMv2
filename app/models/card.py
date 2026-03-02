from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from difflib import SequenceMatcher


@dataclass
class Card:
    deck_id: int
    front: str
    back: str
    tags: list[str] = field(default_factory=list)
    id: int | None = None
    created_at: str | None = None
    ease_factor: float = 2.5
    interval_days: int = 1
    repetitions: int = 0
    due_date: str | None = None

    def apply_srs_score(self, quality: int) -> None:
        quality = max(0, min(5, quality))
        if quality < 3:
            self.repetitions = 0
            self.interval_days = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval_days = 1
            elif self.repetitions == 2:
                self.interval_days = 6
            else:
                self.interval_days = round(self.interval_days * self.ease_factor)

        self.ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        self.ease_factor = max(1.3, self.ease_factor)
        self.due_date = (datetime.now() + timedelta(days=self.interval_days)).isoformat()

    def typo_ratio(self, answer: str) -> float:
        return SequenceMatcher(None, answer.strip().lower(), self.back.strip().lower()).ratio()

    def is_correct(self, answer: str, strict_accents: bool = False) -> bool:
        candidate = answer.strip()
        target = self.back.strip()
        if not strict_accents:
            candidate = candidate.lower()
            target = target.lower()
        if candidate == target:
            return True
        return self.typo_ratio(answer) >= 0.88
