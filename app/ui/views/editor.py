from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget


class EditorView(QWidget):
    save_card_clicked = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.front = QTextEdit()
        self.back = QTextEdit()
        self.tags = QLineEdit()
        self.save_btn = QPushButton("Save Card")

        layout.addWidget(QLabel("Front"))
        layout.addWidget(self.front)
        layout.addWidget(QLabel("Back"))
        layout.addWidget(self.back)
        layout.addWidget(QLabel("Tags (comma-separated)"))
        layout.addWidget(self.tags)
        layout.addWidget(self.save_btn)

        self.save_btn.clicked.connect(self._emit_save)

    def _emit_save(self):
        self.save_card_clicked.emit(self.front.toPlainText(), self.back.toPlainText(), self.tags.text())
