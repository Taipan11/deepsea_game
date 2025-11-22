# gui/board_widget.py

from PySide6.QtWidgets import QWidget, QGridLayout
from .space_widget import SpaceWidget


class BoardWidget(QWidget):
    def __init__(self, board, players, parent=None, columns: int = 8):
        """
        board : instance de Board
        players : liste de Player
        columns : nombre de cases par ligne (la largeur du "serpent")
        """
        super().__init__(parent)
        self.board = board
        self.players = players
        self.columns = columns

        self.layout = QGridLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.refresh(board, players)

    def refresh(self, board=None, players=None):
        """
        Met à jour l'affichage du plateau en forme de "S".
        """
        if board is not None:
            self.board = board
        if players is not None:
            self.players = players

        # Vider l’ancien layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        spaces = self.board.spaces
        n = len(spaces)

        for idx, space in enumerate(spaces):
            # Calcul de la ligne et de la colonne dans la grille
            row = idx // self.columns
            col_in_row = idx % self.columns

            # Ligne paire : gauche -> droite
            # Ligne impaire : droite -> gauche (effet serpent)
            if row % 2 == 0:
                col = col_in_row
            else:
                col = self.columns - 1 - col_in_row

            # Qui est sur cette case ?
            players_here = [p.name for p in self.players if p.position == idx]

            widget = SpaceWidget(space, idx, players_here)
            self.layout.addWidget(widget, row, col)
