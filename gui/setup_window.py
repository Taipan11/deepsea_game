import os
import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
    QLineEdit
)
from PySide6.QtCore import Qt
from src.player import Player
from gui.game_window import GameWindow

class SetupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deep Sea Adventure – Nouvelle partie")
        self.setMinimumSize(600, 400)

        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Titre
        title = QLabel("Deep Sea Adventure 🐙")
        title.setObjectName("SetupTitle")
        subtitle = QLabel("Configure ta nouvelle partie")
        subtitle.setObjectName("SetupSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # GroupBox mode de jeu
        mode_group = QGroupBox("Mode de jeu")
        mode_layout = QVBoxLayout()
        mode_group.setLayout(mode_layout)

        self.radio_pvp = QRadioButton("Joueur vs Joueur")
        self.radio_pvai = QRadioButton("Joueur vs IA")
        self.radio_pvai.setChecked(True)

        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.addButton(self.radio_pvp)
        self.mode_button_group.addButton(self.radio_pvai)

        mode_layout.addWidget(self.radio_pvp)
        mode_layout.addWidget(self.radio_pvai)

        main_layout.addWidget(mode_group)

        # GroupBox joueurs
        players_group = QGroupBox("Joueurs")
        players_layout = QVBoxLayout()
        players_group.setLayout(players_layout)

        # Joueur 1
        row1 = QHBoxLayout()
        label_p1 = QLabel("Joueur 1 :")
        self.input_player1 = QLineEdit()
        self.input_player1.setPlaceholderText("Nom du joueur 1 (humain)")
        row1.addWidget(label_p1)
        row1.addWidget(self.input_player1)
        players_layout.addLayout(row1)

        # Joueur 2
        row2 = QHBoxLayout()
        self.label_p2 = QLabel("Joueur 2 :")
        self.input_player2 = QLineEdit()
        self.input_player2.setPlaceholderText("Bot")
        row2.addWidget(self.label_p2)
        row2.addWidget(self.input_player2)
        players_layout.addLayout(row2)

        main_layout.addWidget(players_group)

        # Bouton lancer
        self.start_button = QPushButton("🚀 Lancer la partie")
        self.start_button.setObjectName("StartButton")
        self.start_button.clicked.connect(self.on_start_clicked)

        main_layout.addStretch()
        main_layout.addWidget(self.start_button)

        # Réagit au changement de mode
        self.radio_pvp.toggled.connect(self._on_mode_changed)
        self._on_mode_changed()  # initialisation texte joueur 2

    def _on_mode_changed(self):
        if self.radio_pvp.isChecked():
            self.label_p2.setText("Joueur 2 :")
            self.input_player2.setPlaceholderText("Nom du joueur 2 (humain)")
        else:
            self.label_p2.setText("Adversaire IA :")
            self.input_player2.setPlaceholderText("Nom du bot (ex : Kraken)")
            if not self.input_player2.text():
                self.input_player2.setText("Bot")

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #020617;
            }

            QLabel#SetupTitle {
                font-size: 24px;
                font-weight: 800;
                color: #e5e7eb;
            }

            QLabel#SetupSubtitle {
                font-size: 13px;
                color: #9ca3af;
                margin-bottom: 8px;
            }

            QGroupBox {
                border: 1px solid #1f2937;
                border-radius: 10px;
                margin-top: 12px;
                background-color: #020617;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                margin-left: 6px;
                color: #9ca3af;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel {
                color: #e5e7eb;
                font-size: 12px;
            }

            QLineEdit {
                background-color: #020617;
                border-radius: 6px;
                border: 1px solid #111827;
                color: #e5e7eb;
                padding: 6px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
            }

            QRadioButton {
                color: #e5e7eb;
                font-size: 12px;
            }

            QPushButton#StartButton {
                background-color: #22c55e;
                color: #020617;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                padding: 10px 16px;
                border: none;
            }
            QPushButton#StartButton:hover {
                background-color: #16a34a;
            }
        """)

    def on_start_clicked(self):
        name1 = self.input_player1.text().strip() or "Joueur 1"
        name2 = self.input_player2.text().strip()

        if self.radio_pvp.isChecked():
            if not name2:
                name2 = "Joueur 2"
            players: List[Player] = [
                Player(name=name1),
                Player(name=name2),
            ]
        else:
            if not name2:
                name2 = "Bot"
            players = [
                Player(name=name1),
                AIPlayer(name=name2),
            ]

        # Créer et afficher la fenêtre de jeu
        self.game_window = GameWindow(players=players)
        self.game_window.show()
        self.close()
