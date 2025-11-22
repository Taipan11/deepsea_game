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
)
from PySide6.QtCore import Qt

# Rendre src importable (comme dans cli_game.py)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.game import Game
from src.player import Player
from src.ai_player import AIPlayer
from .board_widget import BoardWidget


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deep Sea Adventure 🐙")
        self.setMinimumSize(1000, 600)

        # --- Moteur de jeu ---
        players = [
            Player(name="Mehdi"),
            AIPlayer(name="Bot"),
        ]
        self.game = Game(players, num_rounds=3, air_per_round=25)
        # Widget graphique du plateau
        self.board_widget = BoardWidget(self.game.board, self.game.players)

        # --- UI ---
        self._build_ui()
        self._refresh_ui()

    # =========================
    #  Construction UI
    # =========================

    def _build_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # --- Bandeau d'infos partie (manche, air) ---
        info_layout = QHBoxLayout()
        self.label_round = QLabel()
        self.label_air = QLabel()
        info_layout.addWidget(self.label_round)
        info_layout.addWidget(self.label_air)
        info_layout.addStretch()
        main_layout.addLayout(info_layout)

        # --- Plateau ---
        main_layout.addWidget(self.board_widget)

        # --- Zone joueurs + actions ---
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)

        # Zone états joueurs
        self.players_text = QTextEdit()
        self.players_text.setReadOnly(True)
        bottom_layout.addWidget(self.players_text, stretch=1)

        # Zone actions joueur courant
        actions_layout = QVBoxLayout()
        bottom_layout.addLayout(actions_layout, stretch=1)

        # Joueur actuel
        self.label_current_player = QLabel()
        actions_layout.addWidget(self.label_current_player)

        # Choix direction
        actions_layout.addWidget(QLabel("Direction :"))

        self.radio_descend = QRadioButton("Descendre")
        self.radio_go_back = QRadioButton("Remonter")

        self.direction_group = QButtonGroup()
        self.direction_group.addButton(self.radio_descend)
        self.direction_group.addButton(self.radio_go_back)

        actions_layout.addWidget(self.radio_descend)
        actions_layout.addWidget(self.radio_go_back)

        # Choix action
        actions_layout.addWidget(QLabel("Action sur la case :"))

        self.radio_action_none = QRadioButton("Ne rien faire (A)")
        self.radio_action_pick = QRadioButton("Ramasser un trésor (B)")

        self.action_group = QButtonGroup()
        self.action_group.addButton(self.radio_action_none)
        self.action_group.addButton(self.radio_action_pick)

        actions_layout.addWidget(self.radio_action_none)
        actions_layout.addWidget(self.radio_action_pick)

        # Bouton pour jouer le tour
        self.button_play_turn = QPushButton("Jouer le tour du joueur actuel")
        self.button_play_turn.clicked.connect(self.on_play_turn_clicked)
        actions_layout.addWidget(self.button_play_turn)

        actions_layout.addStretch()

    # =========================
    #  Mise à jour UI
    # =========================

    def _refresh_ui(self):
        # Infos de manche
        self.label_round.setText(f"Manche : {self.game.round_number}/{self.game.num_rounds}")
        self.label_air.setText(f"Air restant : {self.game.air}")

        # Plateau
        self.board_widget.refresh(self.game.board, self.game.players)


        # État des joueurs
        status_lines = self.game.get_players_status_ascii()
        self.players_text.setPlainText("\n".join(status_lines))

        # Joueur actuel
        p = self.game.current_player
        role = "IA" if p.is_ai else "Humain"
        self.label_current_player.setText(f"Joueur actuel : {p.name} ({role})")

        # Pré-sélection des boutons :
        if p.is_on_submarine:
            # Premier coup : obligation de descendre
            self.radio_descend.setChecked(True)
            self.radio_go_back.setChecked(False)
            self.radio_go_back.setEnabled(False)
        else:
            self.radio_go_back.setEnabled(True)
            if p.going_back:
                self.radio_go_back.setChecked(True)
            else:
                self.radio_descend.setChecked(True)

        # Action par défaut : ne rien faire
        self.radio_action_none.setChecked(True)

        # Désactiver le bouton si la manche ou la partie est finie
        self.button_play_turn.setEnabled(
            not self.game.is_round_over() and not self.game.is_game_over()
        )

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
        if player.is_ai:
            assert isinstance(player, AIPlayer)
            go_back = player.choose_direction(self.game.air)
        else:
            if player.is_on_submarine:
                go_back = False  # obligé de descendre au départ
            else:
                go_back = self.radio_go_back.isChecked()

        # --- Phase de déplacement ---
        result = self.game.begin_turn(player, going_back=go_back)

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

            if self.game.is_game_over():
                winners = self.game.get_winners()
                if len(winners) == 1:
                    win_msg = f"Le vainqueur est {winners[0].name} !"
                else:
                    win_msg = "Égalité entre : " + ", ".join(w.name for w in winners)
                QMessageBox.information(self, "Fin de partie", win_msg)
        else:
            # Joueur suivant
            self.game.advance_to_next_player()

        # Refresh après toutes les modifications
        self._refresh_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())
