from PySide6.QtWidgets import QDialog

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt

class EndGameDialog(QDialog):
    def __init__(self, scores: dict, winners: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fin de partie")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("🎉 Partie terminée !")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #e5e7eb;")
        layout.addWidget(title)

        # Texte des scores
        text = "Scores finaux :\n"
        for name, s in scores.items():
            text += f" - {name}: {s}\n"


        if len(winners) == 1:
            text += f"\n🏆 Vainqueur : {winners[0].name} a gagné la partie !"
        else:
            text += "\n🤝 Égalité entre : " + ", ".join(p.name for p in winners)

        label_scores = QLabel(text)
        label_scores.setStyleSheet("color: #e5e7eb; font-size: 12px;")
        label_scores.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label_scores.setWordWrap(True)
        layout.addWidget(label_scores)

        # Boutons
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        btn_replay = QPushButton("🔁 Rejouer")
        btn_quit = QPushButton("🚪 Quitter")

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_replay)
        buttons_layout.addWidget(btn_quit)
        buttons_layout.addStretch()

        btn_replay.clicked.connect(self._on_replay_clicked)
        btn_quit.clicked.connect(self.reject)

        # Style simple
        self.setStyleSheet("""
            QDialog {
                background-color: #020617;
            }
            QPushButton {
                background-color: #38bdf8;
                color: #020617;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0ea5e9;
            }
        """)

    def _on_replay_clicked(self):
        self.accept()  # on utilise accept() comme signal "rejouer"
