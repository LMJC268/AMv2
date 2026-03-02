from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from app.models.card import Card


class StudySessionView(QWidget):
    answer_submitted = pyqtSignal(str)
    reveal_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.prompt = QLabel("Start studying by selecting a deck.")
        self.answer = QLineEdit()
        self.submit = QPushButton("Submit")
        self.reveal = QPushButton("Reveal")
        self.feedback = QLabel("")

        layout.addWidget(self.prompt)
        layout.addWidget(self.answer)
        layout.addWidget(self.submit)
        layout.addWidget(self.reveal)
        layout.addWidget(self.feedback)

        self.submit.clicked.connect(lambda: self.answer_submitted.emit(self.answer.text()))
        self.reveal.clicked.connect(self.reveal_clicked.emit)

    def set_card(self, card: Card) -> None:
        self.prompt.setText(card.front)
        self.answer.clear()
        self.feedback.setText("")

    def set_feedback(self, text: str) -> None:
        self.feedback.setText(text)
