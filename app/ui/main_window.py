from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.srs_engine import SRSEngine
from app.database.repositories import CardRepository, DeckRepository, FolderRepository, ProgressRepository, TabulaRepository
from app.database.sqlite_manager import SQLiteManager
from app.models.card import Card
from app.models.deck import Deck
from app.state.settings_manager import SettingsManager
from app.ui.views.archivum import ArchivumView
from app.ui.views.editor import EditorView
from app.ui.views.study_session import StudySessionView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ars Memoria - Magister Edition")
        self.resize(1400, 900)

        self.settings = SettingsManager()
        self.db = SQLiteManager()
        self.folder_repo = FolderRepository(self.db)
        self.deck_repo = DeckRepository(self.db)
        self.card_repo = CardRepository(self.db)
        self.progress_repo = ProgressRepository(self.db)
        self.tabula_repo = TabulaRepository(self.db)

        self._active_deck_id: int | None = None
        self._study_cards: list[Card] = []
        self._study_index = 0

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        self.btn_archivum = QPushButton("Archivum")
        self.btn_editor = QPushButton("Editor")
        self.btn_study = QPushButton("Study")
        sidebar_layout.addWidget(self.btn_archivum)
        sidebar_layout.addWidget(self.btn_editor)
        sidebar_layout.addWidget(self.btn_study)
        sidebar_layout.addStretch(1)

        self.stack = QStackedWidget()
        self.archivum = ArchivumView()
        self.editor = EditorView()
        self.study = StudySessionView()
        self.stack.addWidget(self.archivum)
        self.stack.addWidget(self.editor)
        self.stack.addWidget(self.study)

        layout.addWidget(sidebar, 1)
        layout.addWidget(self.stack, 5)
        self._apply_styles()
        self._wire_events()
        self.refresh_decks()

    def _apply_styles(self) -> None:
        # Translated from old CSS palette into Qt stylesheet.
        self.setStyleSheet(
            """
            QMainWindow { background: #e6d8c3; }
            QPushButton { background: #6e4f2b; color: #f8f0e3; border-radius: 6px; padding: 8px; }
            QPushButton:hover { background: #88613a; }
            QTextEdit, QLineEdit, QListWidget { background: #f8f0e3; border: 1px solid #ab8f6a; }
            QLabel { color: #3b2a1a; font-size: 15px; }
            """
        )

    def _wire_events(self) -> None:
        self.btn_archivum.clicked.connect(lambda: self.stack.setCurrentWidget(self.archivum))
        self.btn_editor.clicked.connect(lambda: self.stack.setCurrentWidget(self.editor))
        self.btn_study.clicked.connect(lambda: self.stack.setCurrentWidget(self.study))

        self.archivum.create_deck_clicked.connect(self._create_deck)
        self.archivum.deck_selected.connect(self._select_deck)

        self.editor.save_card_clicked.connect(self._save_card)
        self.study.answer_submitted.connect(self._submit_answer)
        self.study.reveal_clicked.connect(self._reveal_answer)

    def refresh_decks(self) -> None:
        self.archivum.set_decks(self.deck_repo.fetch_all())

    def _create_deck(self) -> None:
        name, ok = QInputDialog.getText(self, "Create Deck", "Deck name")
        if ok and name.strip():
            self.deck_repo.insert(Deck(name=name.strip()))
            self.refresh_decks()

    def _select_deck(self, deck_id: int) -> None:
        self._active_deck_id = deck_id
        self._study_cards = self.card_repo.fetch_by_deck(deck_id)
        self._study_index = 0
        if self._study_cards:
            self.study.set_card(self._study_cards[0])
        else:
            self.study.set_feedback("No cards in this deck yet.")

    def _save_card(self, front: str, back: str, tags: str) -> None:
        if not self._active_deck_id:
            QMessageBox.warning(self, "Deck required", "Select a deck in Archivum before adding cards.")
            return
        if not front.strip() or not back.strip():
            return
        card = Card(deck_id=self._active_deck_id, front=front.strip(), back=back.strip(), tags=[t.strip() for t in tags.split(",") if t.strip()])
        self.card_repo.insert(card)
        self._study_cards = self.card_repo.fetch_by_deck(self._active_deck_id)
        self.study.set_feedback("Card saved.")

    def _submit_answer(self, answer: str) -> None:
        if not self._study_cards:
            return
        card = self._study_cards[self._study_index]
        correct, quality, ratio = SRSEngine.evaluate_answer(card, answer, self.settings.get("strict_accents", False))
        SRSEngine.update_card_progress(card, quality)
        self.card_repo.update(card)
        self.progress_repo.update(card.id, quality, card.repetitions, 0 if correct else 1) if card.id else None

        self.study.set_feedback(f"{'Correct' if correct else 'Try again'} · match {ratio:.0%}")
        if correct:
            self._study_index = (self._study_index + 1) % len(self._study_cards)
            self.study.set_card(self._study_cards[self._study_index])

    def _reveal_answer(self) -> None:
        if self._study_cards:
            self.study.set_feedback(f"Answer: {self._study_cards[self._study_index].back}")
