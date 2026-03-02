from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass
class Stopwatch:
    _start: float | None = None
    _elapsed: float = 0.0

    def start(self) -> None:
        if self._start is None:
            self._start = monotonic()

    def stop(self) -> None:
        if self._start is not None:
            self._elapsed += monotonic() - self._start
            self._start = None

    def reset(self) -> None:
        self._start = None
        self._elapsed = 0.0

    def elapsed_seconds(self) -> int:
        running = (monotonic() - self._start) if self._start is not None else 0
        return int(self._elapsed + running)


@dataclass
class CountdownTimer:
    duration: int
    _start: float | None = None

    def start(self) -> None:
        self._start = monotonic()

    def remaining(self) -> int:
        if self._start is None:
            return self.duration
        return max(0, self.duration - int(monotonic() - self._start))

    def complete(self) -> bool:
        return self.remaining() == 0
