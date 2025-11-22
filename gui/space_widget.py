# gui/space_widget.py

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


class SpaceWidget(QLabel):
    def __init__(self, space, index: int, players_here=None, parent=None):
        super().__init__(parent)
        self.space = space
        self.index = index
        self.players_here = players_here or []
        self._setup()

    def _setup(self):
        # Cas sous-marin
        if self.space.is_submarine:
            text = "SUB"
            bg = "#2E86C1"

        # Cas avec au moins une ruine
        elif self.space.has_ruin:
            # 👉 On utilise top_ruin, pas space.ruin
            tile = self.space.top_ruin
            level = tile.level
            value = tile.value

            colors = {
                1: "#ABEBC6",  # vert clair
                2: "#F7DC6F",  # jaune
                3: "#F5B041",  # orange
                4: "#EC7063",  # rouge
            }
            bg = colors.get(level, "#D5D8DC")
            text = f"{value}"

            # Si plusieurs ruines empilées, tu peux l’indiquer :
            if self.space.ruin_count > 1:
                text += f"\n({self.space.ruin_count}x)"

        # Case vide
        else:
            text = "-"
            bg = "#D5D8DC"

        # Ajouter les joueurs présents sur la case
        if self.players_here:
            players_text = ",".join(self.players_here)
            text += f"\n{players_text}"

        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(50, 50)
        self.setStyleSheet(f"""
            background-color: {bg};
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
        """)
