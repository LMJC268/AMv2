from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Tabula:
    name: str
    rows: int
    columns: int
    grid: list[list[str]] = field(default_factory=list)
    progress: dict[str, int] = field(default_factory=dict)
    id: int | None = None

    def completion_ratio(self) -> float:
        total = self.rows * self.columns
        if total <= 0:
            return 0.0
        completed = sum(1 for value in self.progress.values() if value > 0)
        return completed / total
