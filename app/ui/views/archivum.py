from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QListWidget, QPushButton, QVBoxLayout, QWidget

from app.models.deck import Deck


class ArchivumView(QWidget):
    deck_selected = pyqtSignal(int)
    create_deck_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.deck_list = QListWidget()
        self.add_deck_btn = QPushButton("+ Deck")
        layout.addWidget(self.deck_list)
        layout.addWidget(self.add_deck_btn)

        self.deck_list.itemClicked.connect(lambda item: self.deck_selected.emit(item.data(1)))
        self.add_deck_btn.clicked.connect(self.create_deck_clicked.emit)

    def set_decks(self, decks: list[Deck]) -> None:
        self.deck_list.clear()
        for deck in decks:
            self.deck_list.addItem(deck.name)
            self.deck_list.item(self.deck_list.count() - 1).setData(1, deck.id)
