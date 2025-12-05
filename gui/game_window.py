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
    QLineEdit,
    QGraphicsOpacityEffect,
    QSpinBox,
    QDialog,
    QComboBox,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from typing import Optional, List, Callable

# Rendre src importable (comme dans cli_game.py)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.game import Game
from src.player import Player
from src.ai_player import AIPlayer, AIPlayerNormal
from .board_widget import BoardWidget
from .end_game_dialog import EndGameDialog
from .style_utils import load_styles

class GameWindow(QMainWindow):
    def __init__(
            self, 
            players: Optional[List[Player]] = None,
            on_request_new_game: Optional[Callable[[], None]] = None,
            parent=None,
        ):
        """
        on_request_new_game() : callback appelé quand on clique sur "Rejouer" dans la boîte de fin
        """
        super().__init__(parent)
        self.on_request_new_game = on_request_new_game

        self.setWindowTitle("Deep Sea Adventure 🐙")
        self.setMinimumSize(1100, 650)

        # --- Moteur de jeu ---
        if players is None:
            players = [
                Player(name="Mehdi"),
                AIPlayerNormal(name="Bot"),
            ]

        # Le Game est l’unique source de vérité du state
        self.game = Game(players, num_rounds=3, air_per_round=25)
        self.board_widget = BoardWidget(self.game.board, self.game.players)

        # --- UI ---
         # --- UI ---
        self._build_ui()
        load_styles(self)      
        self._init_dice_animation()
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

        for idx, _player in enumerate(self.game.players):
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
        self.radio_action_drop = QRadioButton("Poser un trésor (C)")  # NEW

        self.action_group = QButtonGroup()
        self.action_group.addButton(self.radio_action_none)
        self.action_group.addButton(self.radio_action_pick)
        self.action_group.addButton(self.radio_action_drop)  # NEW

        action_layout.addWidget(self.radio_action_none)
        action_layout.addWidget(self.radio_action_pick)
        action_layout.addWidget(self.radio_action_drop)  # NEW

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
        footer = QLabel(
            "Astuce : plus tu descends, plus les trésors sont précieux… "
            "mais attention à l’air restant ! 💨"
        )
        footer.setObjectName("FooterLabel")
        footer.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(footer)
    
    # =========================
    #  Mise à jour UI
    # =========================

    def _refresh_ui(self):
        """Ne fait que lire l’état du moteur de jeu et mettre l’UI à jour."""
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
            self.radio_action_drop.setEnabled(False)  # NEW
            self.button_play_turn.setEnabled(True)  # on clique juste pour le faire jouer

            self.hint_label.setText(
                "Tour du bot 🤖\n"
                "Il choisit lui-même sa direction et s'il ramasse ou pose un trésor."
            )
        else:
            # Joueur humain : il contrôle direction + action
            self.radio_descend.setEnabled(True)
            self.radio_go_back.setEnabled(True)
            self.radio_action_none.setEnabled(True)
            self.radio_action_pick.setEnabled(True)

            # On n'autorise le bouton “poser” que s’il porte au moins un trésor
            self.radio_action_drop.setEnabled(len(p.carrying) > 0)  # NEW

            self.hint_label.setText(
                "Choisis une direction et une action,\n"
                "puis clique sur « Jouer le tour »."
            )

        # =========================
        #  Direction (UI) – lecture de l’état du moteur
        # =========================
        if not p.is_ai:
            last_index = self.game.board.last_index

            if p.is_on_submarine and not p.has_returned:
                # Début de manche : obligé de descendre (logique métier dans Game.begin_turn,
                # mais on reflète visuellement ici)
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
                # En descente
                if p.position >= last_index:
                    # 👉 Sur la dernière case : impossible de continuer à descendre
                    self.radio_descend.setEnabled(False)
                    self.radio_go_back.setEnabled(True)

                    self.radio_descend.setChecked(False)
                    self.radio_go_back.setChecked(True)
                else:
                    # Cases "normales" : choix libre
                    self.radio_descend.setEnabled(True)
                    self.radio_go_back.setEnabled(True)

                    if not self.radio_go_back.isChecked():
                        self.radio_descend.setChecked(True)
        else:
            # IA : on met juste l'état visuel cohérent
            self.radio_descend.setChecked(not p.going_back)
            self.radio_go_back.setChecked(p.going_back)

        # Action par défaut : ne rien faire
        self.radio_action_none.setChecked(True)
        self.radio_action_pick.setChecked(False)
        self.radio_action_drop.setChecked(False)

        # Désactiver le bouton si la manche ou la partie est finie
        self.button_play_turn.setEnabled(
            not self.game.is_round_over() and not self.game.is_game_over()
        )

    # =========================
    #  Logique "un tour"
    # =========================

    def on_play_turn_clicked(self):
        """Ne fait qu’orchestrer les appels au moteur de jeu + feedback visuel."""
        if self.game.is_game_over():
            QMessageBox.information(self, "Partie terminée", "La partie est déjà terminée.")
            return

        if self.game.is_round_over():
            QMessageBox.information(self, "Manche terminée", "La manche est déjà terminée.")
            return

        player = self.game.current_player

        # --- Décision de direction ---
        if player.is_ai:
            # L’IA décide complètement seule via ses propres méthodes
            assert isinstance(player, AIPlayer)
            go_back = player.choose_direction(self.game.air)
        else:
            # Joueur humain : l’UI traduit seulement ses choix en booléen
            if player.going_back:
                # Déjà en remontée, il continue à remonter (règle métier dans Game.begin_turn)
                go_back = True
            elif player.is_on_submarine and not player.has_returned:
                # Début de manche : obligé de descendre
                go_back = False
            else:
                # En descente, peut choisir de commencer à remonter
                go_back = self.radio_go_back.isChecked()

        # --- Phase de déplacement ---
        result = self.game.begin_turn(player, going_back=go_back)
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
                elif self.radio_action_drop.isChecked():
                    action_code = "C"
                else:
                    action_code = "A"

                # ✅ Vérification spéciale pour C : case déjà occupée
                if action_code == "C":
                    space = self.game.board.get_space(player.position)
                    if space.has_ruin:
                        QMessageBox.warning(
                            self,
                            "Action impossible",
                            "Impossible de poser un trésor sur une case qui contient déjà des ruines."
                        )
                        # On annule l’action (équivalent à "ne rien faire")
                        action_code = "A"

            tile = self.game.perform_action(player, action_code)

            # Feedback uniquement UI, la logique est dans Game / Player / Space
            if not player.is_ai and tile:
                if action_code == "B":
                    QMessageBox.information(
                        self,
                        "Trésor ramassé",
                        f"Vous avez ramassé un trésor (valeur cachée : {tile.value}).",
                    )
                elif action_code == "C":
                    QMessageBox.information(
                        self,
                        "Trésor posé",
                        "Vous avez posé un trésor sur cette case pour vous alléger."
                    )

        # --- Fin de manche ? ---
        if self.game.is_round_over():
            self.game.end_round()
            scores = self.game.get_scores()
            msg = "\n".join(f"{name}: {score}" for name, score in scores.items())
            QMessageBox.information(self, "Fin de manche", msg)

            self.game.next_round()

            if self.game.is_game_over():
                self._show_end_of_game_dialog()
                return
        else:
            self.game.advance_to_next_player()

        self._refresh_ui()


    def _show_end_of_game_dialog(self):

        winners = self.game.get_winners() # List[Player]
        scores = self.game.get_scores() # Dict[str, int]

        dialog = EndGameDialog(scores, winners, parent=self)
        result = dialog.exec()

        # Si l'utilisateur a cliqué sur "Rejouer"
        if result == QDialog.Accepted:
            # On appelle simplement le callback fourni par main.py
            if self.on_request_new_game is not None:
                self.on_request_new_game()

        # Dans tous les cas, on ferme la fenêtre de jeu actuelle
        self.close()

    # ===============
    #  Animation du dé
    # =========================

    def _init_dice_animation(self):
        self.dice_label = QLabel(self)
        self.dice_label.setObjectName("DiceLabel")
        self.dice_label.setAlignment(Qt.AlignCenter)
        self.dice_label.hide()

        self.dice_opacity_effect = QGraphicsOpacityEffect(self.dice_label)
        self.dice_label.setGraphicsEffect(self.dice_opacity_effect)

        self.dice_opacity_anim = QPropertyAnimation(
            self.dice_opacity_effect,
            b"opacity",
            self
        )
        self.dice_opacity_anim.setDuration(1000)  # vitesse augmentée
        self.dice_opacity_anim.setStartValue(0.0)
        self.dice_opacity_anim.setKeyValueAt(0.999, 1.0)
        self.dice_opacity_anim.setEndValue(0.0)
        self.dice_opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
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

