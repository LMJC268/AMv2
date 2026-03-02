from __future__ import annotations

from dataclasses import dataclass, field

from app.models.card import Card


@dataclass
class Deck:
    name: str
    folder_id: int | None = None
    cards: list[Card] = field(default_factory=list)
    id: int | None = None

    def progress(self) -> float:
        if not self.cards:
            return 0.0
        learned = sum(1 for c in self.cards if c.repetitions >= 2)
        return learned / len(self.cards)

    def add_card(self, card: Card) -> None:
        self.cards.append(card)
