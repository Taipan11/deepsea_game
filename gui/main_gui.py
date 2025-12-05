# main.py
import os
import sys

from PySide6.QtWidgets import QApplication

from gui.setup_window import SetupWindow
from gui.game_window import GameWindow


def load_global_styles(app: QApplication):
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"[WARN] Fichier de style introuvable : {qss_path}", file=sys.stderr)


def main():
    app = QApplication(sys.argv)
    load_global_styles(app)

    # petite structure pour garder une référence à la fenêtre courante
    current_window = {"win": None}

    def show_setup():
        # ferme l'ancienne fenêtre si elle existe
        if current_window["win"] is not None:
            current_window["win"].close()

        def start_game(players):
            # callback donné à SetupWindow quand on clique sur "Lancer la partie"
            show_game(players)

        win = SetupWindow(on_start_game=start_game)
        current_window["win"] = win
        win.show()

    def show_game(players):
        if current_window["win"] is not None:
            current_window["win"].close()

        # callback pour "Rejouer" depuis la GameWindow
        def request_new_game():
            show_setup()

        win = GameWindow(players=players, on_request_new_game=request_new_game)
        current_window["win"] = win
        win.show()

    # On commence par la fenêtre de configuration
    show_setup()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
