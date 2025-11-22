import os
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QMessageBox,
    QGroupBox,
    QSplitter,
    QFrame,
    QSizePolicy,
    QLineEdit
)
from PySide6.QtCore import Qt
from src.player import Player


# Rendre src importable (comme dans cli_game.py)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.game import Game
from src.player import Player
from src.ai_player import AIPlayer
from .board_widget import BoardWidget
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from typing import Optional, List


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


class GameWindow(QMainWindow):
    def __init__(self, players: Optional[List[Player]] = None):
        super().__init__()
        self.setWindowTitle("Deep Sea Adventure 🐙")
        self.setMinimumSize(1100, 650)

        # --- Moteur de jeu ---
        if players is None:
            players = [
                Player(name="Mehdi"),
                AIPlayer(name="Bot"),
            ]

        self.game = Game(players, num_rounds=3, air_per_round=25)
        self.board_widget = BoardWidget(self.game.board, self.game.players)

        # --- UI ---
        self._build_ui()
        self._apply_styles()
        self._init_dice_animation()  # si tu as déjà ajouté l’animation
        self._refresh_ui()

    # =========================
    #  Construction UI
    # =========================

    def _build_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # ---------- HEADER ----------
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_widget.setLayout(header_layout)

        self.label_title = QLabel("Deep Sea Adventure 🐙")
        self.label_title.setObjectName("GameTitle")

        header_layout.addWidget(self.label_title)
        header_layout.addStretch()

        # petits “badges” pour manche + air
        self.label_round = QLabel()
        self.label_round.setObjectName("BadgeRound")
        self.label_air = QLabel()
        self.label_air.setObjectName("BadgeAir")

        header_layout.addWidget(self.label_round)
        header_layout.addWidget(self.label_air)

        main_layout.addWidget(header_widget)

        # petite ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # ---------- CONTENU CENTRAL (Split gauche/droite) ----------
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)

        # --- Colonne gauche : Plateau + joueurs ---
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        # GroupBox plateau
        board_group = QGroupBox("Plateau")
        board_layout = QVBoxLayout()
        board_layout.setContentsMargins(8, 8, 8, 8)
        board_group.setLayout(board_layout)
        board_layout.addWidget(self.board_widget)

        left_layout.addWidget(board_group, stretch=3)

        # GroupBox joueurs
        players_group = QGroupBox("Résumé des plongeurs")
        players_layout = QVBoxLayout()
        players_layout.setContentsMargins(8, 8, 8, 8)
        players_layout.setSpacing(6)
        players_group.setLayout(players_layout)

        # On stocke une petite "carte" par joueur (index -> dict de labels)
        self.player_cards = []  # liste alignée sur self.game.players

        for idx, player in enumerate(self.game.players):
            card = QFrame()
            card.setObjectName("PlayerCard")
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(8, 6, 8, 6)
            card_layout.setSpacing(2)
            card.setLayout(card_layout)

            # Nom + rôle
            name_label = QLabel()
            name_label.setObjectName("PlayerNameLabel")

            role_label = QLabel()
            role_label.setObjectName("PlayerRoleLabel")

            card_layout.addWidget(name_label)
            card_layout.addWidget(role_label)

            # Infos détaillées
            pos_label = QLabel()
            pos_label.setObjectName("PlayerInfoLabel")

            state_label = QLabel()
            state_label.setObjectName("PlayerInfoLabel")

            treasure_label = QLabel()
            treasure_label.setObjectName("PlayerInfoLabel")

            card_layout.addWidget(pos_label)
            card_layout.addWidget(state_label)
            card_layout.addWidget(treasure_label)

            players_layout.addWidget(card)

            self.player_cards.append({
                "card": card,
                "name": name_label,
                "role": role_label,
                "pos": pos_label,
                "state": state_label,
                "treasure": treasure_label,
            })


        players_layout.addStretch()
        left_layout.addWidget(players_group, stretch=2)
        
        # --- Colonne droite : panneau d'actions ---
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_panel.setLayout(right_layout)

        # Carte joueur courant
        current_player_group = QGroupBox("Joueur en cours")
        current_player_layout = QVBoxLayout()
        current_player_layout.setContentsMargins(10, 10, 10, 10)
        current_player_group.setLayout(current_player_layout)

        # 👉 Label du joueur actuel
        self.label_current_player = QLabel()
        self.label_current_player.setObjectName("CurrentPlayerLabel")
        current_player_layout.addWidget(self.label_current_player)

        # 👉 Hint (message explicatif)
        self.hint_label = QLabel(
            "Choisis une direction et une action,\n"
            "puis clique sur « Jouer le tour »."
        )
        self.hint_label.setObjectName("HintLabel")
        current_player_layout.addWidget(self.hint_label)

        right_layout.addWidget(current_player_group)


        # GroupBox direction
        direction_groupbox = QGroupBox("Direction du déplacement")
        direction_layout = QVBoxLayout()
        direction_groupbox.setLayout(direction_layout)

        self.radio_descend = QRadioButton("Descendre (vers les profondeurs)")
        self.radio_go_back = QRadioButton("Remonter (retour vers le sous-marin)")

        self.direction_group = QButtonGroup()
        self.direction_group.addButton(self.radio_descend)
        self.direction_group.addButton(self.radio_go_back)

        direction_layout.addWidget(self.radio_descend)
        direction_layout.addWidget(self.radio_go_back)

        right_layout.addWidget(direction_groupbox)

        # GroupBox action
        action_groupbox = QGroupBox("Action sur la case")
        action_layout = QVBoxLayout()
        action_groupbox.setLayout(action_layout)

        self.radio_action_none = QRadioButton("Ne rien faire (A)")
        self.radio_action_pick = QRadioButton("Ramasser un trésor (B)")

        self.action_group = QButtonGroup()
        self.action_group.addButton(self.radio_action_none)
        self.action_group.addButton(self.radio_action_pick)

        action_layout.addWidget(self.radio_action_none)
        action_layout.addWidget(self.radio_action_pick)

        right_layout.addWidget(action_groupbox)

        # Bouton principal
        self.button_play_turn = QPushButton("🎲 Jouer le tour")
        self.button_play_turn.setObjectName("PlayButton")
        self.button_play_turn.setMinimumHeight(40)
        self.button_play_turn.clicked.connect(self.on_play_turn_clicked)

        right_layout.addStretch()
        right_layout.addWidget(self.button_play_turn)

        # Ajout des panneaux dans le splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter, stretch=1)

        # ---------- FOOTER (petites infos) ----------
        footer = QLabel("Astuce : plus tu descends, plus les trésors sont précieux… "
                        "mais attention à l’air restant ! 💨")
        footer.setObjectName("FooterLabel")
        footer.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(footer)

    # =========================
    #  Style moderne (QSS)
    # =========================

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a; /* bleu nuit */
            }

            QLabel#GameTitle {
                font-size: 22px;
                font-weight: 700;
                color: #e5e7eb;
            }

            QLabel#BadgeRound,
            QLabel#BadgeAir {
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 600;
                color: #0f172a;
                background-color: #38bdf8;
            }

            QLabel#BadgeAir {
                background-color: #22c55e;
            }

            QGroupBox {
                border: 1px solid #1f2937;
                border-radius: 10px;
                margin-top: 8px;
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

            QTextEdit#PlayersText {
                background-color: #020617;
                border-radius: 8px;
                border: 1px solid #111827;
                color: #e5e7eb;
                font-family: "JetBrains Mono", "Consolas", monospace;
                font-size: 12px;
            }

            QLabel#CurrentPlayerLabel {
                font-size: 14px;
                font-weight: 600;
                color: #e5e7eb;
            }

            QLabel#HintLabel {
                font-size: 11px;
                color: #9ca3af;
            }

            QLabel#FooterLabel {
                font-size: 11px;
                color: #6b7280;
            }

            QPushButton#PlayButton {
                background-color: #38bdf8;
                color: #020617;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                padding: 8px 16px;
                border: none;
            }
            QPushButton#PlayButton:hover {
                background-color: #0ea5e9;
            }
            QPushButton#PlayButton:disabled {
                background-color: #1e293b;
                color: #4b5563;
            }

            QRadioButton {
                color: #e5e7eb;
                font-size: 12px;
            }

            QSplitter::handle {
                background-color: #020617;
            }
            QFrame#PlayerCard {
                background-color: #020617;
                border-radius: 8px;
                border: 1px solid #111827;
            }

            QLabel#PlayerNameLabel {
                font-size: 13px;
                font-weight: 700;
                color: #e5e7eb;
            }

            QLabel#PlayerRoleLabel {
                font-size: 11px;
                color: #9ca3af;
            }

            QLabel#PlayerInfoLabel {
                font-size: 11px;
                color: #d1d5db;
            }
            QLabel#DiceLabel {
                background-color: rgba(15, 23, 42, 220); /* fond bleu nuit semi-transparent */
                border-radius: 14px;
                border: 1px solid #38bdf8;
                padding: 12px 20px;
                color: #f9fafb;
                font-size: 26px;
                font-weight: 800;
            }
        """)

    # =========================
    #  Mise à jour UI
    # =========================

    def _refresh_ui(self):
        # Infos de manche
        self.label_round.setText(f"Manche : {self.game.round_number}/{self.game.num_rounds}")
        self.label_air.setText(f"Air : {self.game.air}")

        # Plateau
        self.board_widget.refresh(self.game.board, self.game.players)

        # État des joueurs (cartes)
        for idx, player in enumerate(self.game.players):
            widgets = self.player_cards[idx]
            name_label = widgets["name"]
            role_label = widgets["role"]
            pos_label = widgets["pos"]
            state_label = widgets["state"]
            treasure_label = widgets["treasure"]

            role = "IA" if player.is_ai else "Humain"
            name_label.setText(f"{player.name}")
            role_label.setText(f"Rôle : {role}")

            # Position
            pos_text = f"Position : {player.position if not player.is_on_submarine else 'Sous-marin'}"
            pos_label.setText(pos_text)

            # État
            state_parts = []
            if player.is_on_submarine:
                state_parts.append("Sur le sous-marin")
            else:
                if player.going_back:
                    state_parts.append("Remonte vers la surface")
                else:
                    state_parts.append("Descend vers les profondeurs")
            if player.has_returned:
                state_parts.append("✔️ Revenu")
            state_label.setText("État : " + ", ".join(state_parts))

            # Trésors portés & score sécurisé
            carrying_tiles = player.carrying
            carrying_count = len(carrying_tiles)
            carrying_value = sum(tile.value for tile in carrying_tiles)
            total_score = player.total_score

            if carrying_count > 0:
                treasure_label.setText(
                    f"Trésors : {carrying_count} portés "
                    f"(valeur totale : {carrying_value}) | "
                    f"Score sécurisé : {total_score}"
                )
            else:
                treasure_label.setText(
                    f"Trésors : aucun porté | Score sécurisé : {total_score}"
                )

        # Joueur actuel (en dehors de la boucle)
        p = self.game.current_player
        role = "IA" if p.is_ai else "Humain"
        self.label_current_player.setText(f"Joueur actuel : {p.name} ({role})")

        # =========================
        #  Activation / désactivation des contrôles selon IA / humain
        # =========================
        if p.is_ai:
            # Bot : il choisit tout seul, l'UI est juste en lecture
            self.radio_descend.setEnabled(False)
            self.radio_go_back.setEnabled(False)
            self.radio_action_none.setEnabled(False)
            self.radio_action_pick.setEnabled(False)
            self.button_play_turn.setEnabled(True)  # tu cliques juste pour le faire jouer

            self.hint_label.setText(
                "Tour du bot 🤖\n"
                "Il choisit lui-même sa direction et s'il ramasse un trésor."
            )
        else:
            # Joueur humain : il contrôle direction + action
            self.radio_descend.setEnabled(True)
            self.radio_go_back.setEnabled(True)
            self.radio_action_none.setEnabled(True)
            self.radio_action_pick.setEnabled(True)

            self.hint_label.setText(
                "Choisis une direction et une action,\n"
                "puis clique sur « Jouer le tour »."
            )

        # =========================
        #  Direction (UI)
        # =========================
        if p.is_on_submarine and not p.has_returned:
            # Début de manche : obligé de descendre
            self.radio_descend.setEnabled(True)
            self.radio_go_back.setEnabled(False)

            self.radio_descend.setChecked(True)
            self.radio_go_back.setChecked(False)

        elif p.going_back:
            # Il a déjà décidé de remonter : on affiche "Remonter" verrouillé
            self.radio_descend.setEnabled(False)
            self.radio_go_back.setEnabled(False)

            self.radio_descend.setChecked(False)
            self.radio_go_back.setChecked(True)

        else:
            # En pleine descente : libre de choisir descendre / commencer à remonter
            self.radio_descend.setEnabled(True)
            self.radio_go_back.setEnabled(True)

            # Par défaut on met "Descendre"
            # (si le joueur vient de cliquer "Remonter", ce sera pris en compte
            #  dans on_play_turn_clicked avant le prochain refresh)
            if not self.radio_go_back.isChecked():
                self.radio_descend.setChecked(True)

    # =========================
    #  Logique "un tour"
    # =========================

    def on_play_turn_clicked(self):
        if self.game.is_game_over():
            QMessageBox.information(self, "Partie terminée", "La partie est déjà terminée.")
            return

        if self.game.is_round_over():
            QMessageBox.information(self, "Manche terminée", "La manche est déjà terminée.")
            return

        player = self.game.current_player

        # --- Décision de direction ---
                # --- Décision de direction ---
        if player.is_ai:
            assert isinstance(player, AIPlayer)
            go_back = player.choose_direction(self.game.air)
        else:
            if player.going_back:
                # Il est déjà en remontée, il continue.
                go_back = True
            elif player.is_on_submarine and not player.has_returned:
                # Début de manche : sur le sous-marin, obligé de descendre.
                go_back = False
            else:
                # En descente, peut choisir de commencer à remonter.
                go_back = self.radio_go_back.isChecked()

        # --- Phase de déplacement ---
        result = self.game.begin_turn(player, going_back=go_back)
        # Petite animation de dé avec la valeur tirée
        self.show_dice_animation(result.dice_roll)

        # --- Action sur la case ---
        if result.can_act_on_space:
            if player.is_ai:
                assert isinstance(player, AIPlayer)
                space = self.game.board.get_space(player.position)
                action_code = player.choose_action(space, self.game.air)
            else:
                if self.radio_action_pick.isChecked():
                    action_code = "B"
                else:
                    action_code = "A"

            tile = self.game.perform_action(player, action_code)
            if tile and not player.is_ai:
                QMessageBox.information(
                    self,
                    "Trésor ramassé",
                    f"Vous avez ramassé un trésor (valeur cachée : {tile.value}).",
                )

        # --- Fin de manche ? ---
        if self.game.is_round_over():
            self.game.end_round()
            scores = self.game.get_scores()
            msg = "\n".join(f"{name}: {score}" for name, score in scores.items())
            QMessageBox.information(self, "Fin de manche", msg)
            self.game.next_round()

            
        else:
            # Joueur suivant
            self.game.advance_to_next_player()

        # Refresh après toutes les modifications
        self._refresh_ui()

    def _init_dice_animation(self):
        # Label centré qui affichera le résultat du dé (ex : "🎲 4")
        self.dice_label = QLabel(self)
        self.dice_label.setObjectName("DiceLabel")
        self.dice_label.setAlignment(Qt.AlignCenter)
        self.dice_label.hide()

        # Effet de transparence
        self.dice_opacity_effect = QGraphicsOpacityEffect(self.dice_label)
        self.dice_label.setGraphicsEffect(self.dice_opacity_effect)

        # Animation d'opacité (fade in/out)
        self.dice_opacity_anim = QPropertyAnimation(self.dice_opacity_effect, b"opacity", self)
        self.dice_opacity_anim.setDuration(800)  # 0.8s
        self.dice_opacity_anim.setStartValue(0.0)
        self.dice_opacity_anim.setKeyValueAt(0.2, 1.0)  # monte vite à 1
        self.dice_opacity_anim.setEndValue(0.0)
        self.dice_opacity_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.dice_opacity_anim.finished.connect(self.dice_label.hide)

    def show_dice_animation(self, dice_value: int):
        # Texte du dé
        self.dice_label.setText(f"🎲 {dice_value}")
        self.dice_label.adjustSize()

        # Centre le label dans la fenêtre
        rect = self.rect()
        x = rect.center().x() - self.dice_label.width() // 2
        y = rect.center().y() - self.dice_label.height() // 2
        self.dice_label.move(x, y)

        self.dice_label.show()

        # Relance proprement l’animation
        self.dice_opacity_anim.stop()
        self.dice_opacity_anim.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup = SetupWindow()
    setup.show()
    sys.exit(app.exec())

