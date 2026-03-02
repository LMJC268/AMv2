from __future__ import annotations

from app.models.card import Card


class SRSEngine:
    """Translated from JS scheduling behavior into Python service methods."""

    @staticmethod
    def evaluate_answer(card: Card, answer: str, strict_accents: bool = False) -> tuple[bool, int, float]:
        correct = card.is_correct(answer, strict_accents=strict_accents)
        ratio = card.typo_ratio(answer)
        quality = 5 if correct and ratio > 0.97 else 4 if correct else 2 if ratio > 0.7 else 1
        return correct, quality, ratio

    @staticmethod
    def update_card_progress(card: Card, quality: int) -> Card:
        card.apply_srs_score(quality)
        return card
