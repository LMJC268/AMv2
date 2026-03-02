from __future__ import annotations

import csv
import json
from pathlib import Path

from app.models.card import Card


def export_cards_to_json(cards: list[Card], path: str | Path) -> None:
    payload = [
        {
            "id": c.id,
            "deck_id": c.deck_id,
            "front": c.front,
            "back": c.back,
            "tags": c.tags,
            "created_at": c.created_at,
            "ease_factor": c.ease_factor,
            "interval_days": c.interval_days,
            "repetitions": c.repetitions,
            "due_date": c.due_date,
        }
        for c in cards
    ]
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def import_cards_from_json(path: str | Path, deck_id: int) -> list[Card]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Card(deck_id=deck_id, front=row["front"], back=row["back"], tags=row.get("tags", [])) for row in data]


def export_cards_to_csv(cards: list[Card], path: str | Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["front", "back", "tags"])
        for card in cards:
            writer.writerow([card.front, card.back, ",".join(card.tags)])


def import_cards_from_csv(path: str | Path, deck_id: int) -> list[Card]:
    output: list[Card] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            output.append(
                Card(
                    deck_id=deck_id,
                    front=row.get("front", ""),
                    back=row.get("back", ""),
                    tags=[item.strip() for item in row.get("tags", "").split(",") if item.strip()],
                )
            )
    return output
