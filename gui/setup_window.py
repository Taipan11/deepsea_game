import os
import sys
from typing import List, Callable

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
    QLineEdit,
    QSpinBox,
    QComboBox,
)

# Rendre src importable (comme dans cli_game.py)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.player import Player
from src.ai_player import AIPlayerNormal, AIPlayerCautious, AIPlayerAdventurous
from .style_utils import load_styles


class SetupWindow(QMainWindow):
    MAX_PLAYERS = 6

    def __init__(self, on_start_game: Callable[[List[Player]], None], parent=None):
        super().__init__(parent)
        self.on_start_game = on_start_game

        self.setWindowTitle("Deep Sea Adventure – Nouvelle partie")
        self.setMinimumSize(600, 400)

        self.player_rows: List[dict] = []  # une entrée par ligne visuelle

        self._build_ui()
        load_styles(self)

    # =========================
    #  Construction UI
    # =========================

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

        # Sélection du nombre de joueurs (2 à MAX_PLAYERS)
        self.spin_player_count = QSpinBox()
        self.spin_player_count.setRange(2, self.MAX_PLAYERS)
        self.spin_player_count.setValue(2)
        self.spin_player_count.valueChanged.connect(self.on_player_count_changed)

        row_count = QHBoxLayout()
        row_count.addWidget(QLabel("Nombre de joueurs :"))
        row_count.addWidget(self.spin_player_count)
        main_layout.addLayout(row_count)

        # Groupe des joueurs
        players_group = QGroupBox("Joueurs")
        self.players_layout = QVBoxLayout()
        players_group.setLayout(self.players_layout)
        main_layout.addWidget(players_group)

        # ✅ Créer une fois toutes les lignes (max 6), puis on cache/affiche
        self._create_player_rows()

        # Bouton lancer
        self.start_button = QPushButton("🚀 Lancer la partie")
        self.start_button.setObjectName("StartButton")
        self.start_button.clicked.connect(self.on_start_clicked)

        main_layout.addStretch()
        main_layout.addWidget(self.start_button)

        # Mettre à jour la visibilité selon la valeur initiale du spin
        self._update_rows_visibility(self.spin_player_count.value())

    def _create_player_rows(self):
        """
        Crée MAX_PLAYERS lignes de configuration de joueurs,
        puis on gère leur visibilité séparément.
        """
        for i in range(self.MAX_PLAYERS):
            widget = QWidget()
            layout = QHBoxLayout(widget)

            label = QLabel(f"Joueur {i+1} :")
            input_name = QLineEdit()
            input_name.setPlaceholderText(f"Nom du joueur {i+1}")

            role_human = QRadioButton("Humain")
            role_ai = QRadioButton("IA")

            group = QButtonGroup(widget)
            group.addButton(role_human)
            group.addButton(role_ai)

            combo_ai_level = QComboBox()
            combo_ai_level.addItems(["Normal", "Prudent", "Aventureux"])
            combo_ai_level.setEnabled(False)

            # 👉 Par défaut : humain
            role_human.setChecked(True)

            # 🔥 Connexion propre : chaque ligne a son index
            def make_role_ai_slot(index: int):
                def on_role_ai_toggled(checked: bool):
                    row = self.player_rows[index]
                    row["combo_ai_level"].setEnabled(checked)
                return on_role_ai_toggled

            # On connecte le toggled de role_ai uniquement
            # Quand IA = True => combo enabled, IA = False => combo disabled
            # Le slot sera créé après avoir rempli player_rows (voir plus bas)
            layout.addWidget(label)
            layout.addWidget(input_name)
            layout.addWidget(role_human)
            layout.addWidget(role_ai)
            layout.addWidget(combo_ai_level)

            self.players_layout.addWidget(widget)

            self.player_rows.append({
                "widget": widget,
                "label": label,
                "name_input": input_name,
                "role_human": role_human,
                "role_ai": role_ai,
                "combo_ai_level": combo_ai_level,
            })

        # Maintenant qu'on a self.player_rows rempli, on peut connecter les slots proprement
        for index, row in enumerate(self.player_rows):
            role_ai = row["role_ai"]
            combo = row["combo_ai_level"]

            def on_role_ai_toggled(checked: bool, idx=index):
                self.player_rows[idx]["combo_ai_level"].setEnabled(checked)

            role_ai.toggled.connect(on_role_ai_toggled)

    # =========================
    #  Gestion du nombre de joueurs
    # =========================

    def on_player_count_changed(self, value: int):
        self._update_rows_visibility(value)

    def _update_rows_visibility(self, count: int):
        """
        Affiche uniquement les 'count' premières lignes,
        cache les autres, sans perdre leur contenu.
        """
        for index, row in enumerate(self.player_rows):
            visible = index < count
            row["widget"].setVisible(visible)

    # =========================
    #  Création des joueurs pour la partie
    # =========================

    def on_start_clicked(self):
        players: List[Player] = []

        count = self.spin_player_count.value()
        for idx in range(count):
            row = self.player_rows[idx]
            name = row["name_input"].text().strip()
            if not name:
                name = f"Joueur {len(players)+1}"

            if row["role_ai"].isChecked():
                level = row["combo_ai_level"].currentText()

                if level == "Normal":
                    players.append(AIPlayerNormal(name=name))
                elif level == "Prudent":
                    players.append(AIPlayerCautious(name=name))
                elif level == "Aventureux":
                    players.append(AIPlayerAdventurous(name=name))
            else:
                players.append(Player(name=name))

        # On délègue à main.py la création de la GameWindow
        self.on_start_game(players)
        self.close()
