from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from app.database.sqlite_manager import SQLiteManager
from app.models.card import Card
from app.models.deck import Deck
from app.models.tabula import Tabula


class FolderRepository:
    def __init__(self, db: SQLiteManager):
        self.db = db

    def insert(self, name: str, parent_id: int | None = None) -> int:
        return self.db.execute("INSERT INTO folders(name, parent_id) VALUES (?, ?)", (name, parent_id))

    def update(self, folder_id: int, name: str) -> None:
        self.db.execute("UPDATE folders SET name=? WHERE id=?", (name, folder_id))

    def delete(self, folder_id: int) -> None:
        self.db.execute("DELETE FROM folders WHERE id=?", (folder_id,))

    def fetch_all(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.fetch_all("SELECT * FROM folders ORDER BY name")]


class DeckRepository:
    def __init__(self, db: SQLiteManager):
        self.db = db

    def insert(self, deck: Deck) -> int:
        return self.db.execute("INSERT INTO decks(folder_id, name) VALUES (?, ?)", (deck.folder_id, deck.name))

    def update(self, deck_id: int, name: str, folder_id: int | None) -> None:
        self.db.execute("UPDATE decks SET name=?, folder_id=? WHERE id=?", (name, folder_id, deck_id))

    def delete(self, deck_id: int) -> None:
        self.db.execute("DELETE FROM decks WHERE id=?", (deck_id,))

    def fetch_all(self) -> list[Deck]:
        rows = self.db.fetch_all("SELECT * FROM decks ORDER BY created_at DESC")
        return [Deck(id=r["id"], folder_id=r["folder_id"], name=r["name"]) for r in rows]


class CardRepository:
    def __init__(self, db: SQLiteManager):
        self.db = db

    def insert(self, card: Card) -> int:
        return self.db.execute(
            """INSERT INTO cards(deck_id, front, back, tags, ease_factor, interval_days, repetitions, due_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                card.deck_id,
                card.front,
                card.back,
                ",".join(card.tags),
                card.ease_factor,
                card.interval_days,
                card.repetitions,
                card.due_date,
            ),
        )

    def update(self, card: Card) -> None:
        self.db.execute(
            """UPDATE cards SET front=?, back=?, tags=?, ease_factor=?, interval_days=?, repetitions=?, due_date=?
               WHERE id=?""",
            (
                card.front,
                card.back,
                ",".join(card.tags),
                card.ease_factor,
                card.interval_days,
                card.repetitions,
                card.due_date,
                card.id,
            ),
        )

    def delete(self, card_id: int) -> None:
        self.db.execute("DELETE FROM cards WHERE id=?", (card_id,))

    def fetch_by_deck(self, deck_id: int) -> list[Card]:
        rows = self.db.fetch_all("SELECT * FROM cards WHERE deck_id=? ORDER BY id", (deck_id,))
        cards = []
        for r in rows:
            cards.append(
                Card(
                    id=r["id"],
                    deck_id=r["deck_id"],
                    front=r["front"],
                    back=r["back"],
                    tags=r["tags"].split(",") if r["tags"] else [],
                    created_at=r["created_at"],
                    ease_factor=r["ease_factor"],
                    interval_days=r["interval_days"],
                    repetitions=r["repetitions"],
                    due_date=r["due_date"],
                )
            )
        return cards


class ProgressRepository:
    def __init__(self, db: SQLiteManager):
        self.db = db

    def insert(self, card_id: int, score: int, streak: int, typo_count: int) -> int:
        return self.db.execute(
            "INSERT INTO progress(card_id, last_score, streak, typo_count) VALUES (?, ?, ?, ?)",
            (card_id, score, streak, typo_count),
        )

    def update(self, card_id: int, score: int, streak: int, typo_count: int) -> None:
        self.db.execute(
            "UPDATE progress SET last_score=?, streak=?, typo_count=?, updated_at=CURRENT_TIMESTAMP WHERE card_id=?",
            (score, streak, typo_count, card_id),
        )

    def delete(self, card_id: int) -> None:
        self.db.execute("DELETE FROM progress WHERE card_id=?", (card_id,))

    def fetch(self, card_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one("SELECT * FROM progress WHERE card_id=?", (card_id,))
        return dict(row) if row else None


class TabulaRepository:
    def __init__(self, db: SQLiteManager):
        self.db = db

    def insert(self, tabula: Tabula) -> int:
        return self.db.execute(
            "INSERT INTO tabulas(name, rows, columns, grid_json, progress_json) VALUES (?, ?, ?, ?, ?)",
            (tabula.name, tabula.rows, tabula.columns, json.dumps(tabula.grid), json.dumps(tabula.progress)),
        )

    def update(self, tabula: Tabula) -> None:
        self.db.execute(
            "UPDATE tabulas SET name=?, rows=?, columns=?, grid_json=?, progress_json=? WHERE id=?",
            (
                tabula.name,
                tabula.rows,
                tabula.columns,
                json.dumps(tabula.grid),
                json.dumps(tabula.progress),
                tabula.id,
            ),
        )

    def delete(self, tabula_id: int) -> None:
        self.db.execute("DELETE FROM tabulas WHERE id=?", (tabula_id,))

    def fetch_all(self) -> list[Tabula]:
        rows = self.db.fetch_all("SELECT * FROM tabulas ORDER BY created_at DESC")
        result = []
        for r in rows:
            result.append(
                Tabula(
                    id=r["id"],
                    name=r["name"],
                    rows=r["rows"],
                    columns=r["columns"],
                    grid=json.loads(r["grid_json"] or "[]"),
                    progress=json.loads(r["progress_json"] or "{}"),
                )
            )
        return result
