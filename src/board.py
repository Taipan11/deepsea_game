# board.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .ruin_tile import RuinTile
from .space import Space
import random


@dataclass
class Board:
    """
    Représente le plateau de Deep Sea Adventure.

    Attributs
    ---------
    spaces : List[Space]
        Liste ordonnée des cases du chemin :
        - spaces[0] est toujours le sous-marin.
        - spaces[1..N] sont les cases de ruines/vides.
    """

    spaces: List[Space] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Valide la cohérence du plateau.
        - Au moins une case (le sous-marin).
        - spaces[0] doit être le sous-marin.
        """
        if not self.spaces:
            raise ValueError("Un Board doit contenir au moins une case (le sous-marin).")

        if not self.spaces[0].is_submarine:
            raise ValueError("La case d'index 0 doit être le sous-marin.")

    # ========================
    #  Méthodes de construction
    # ========================

    @classmethod
    def create_default(
        cls,
        *,
        max_stack_size: Optional[int] = None,
        shuffle_tiles: bool = True,
        rng: Optional[random.Random] = None,
    ) -> "Board":
        """
        Crée un plateau par défaut avec la distribution standard des jetons.

        - Si shuffle_tiles=True, on mélange l’ordre des tuiles
        *à l’intérieur de chaque niveau* (profondeur),
        mais on garde l’ordre 1 → 2 → 3 → 4.
        """
        if rng is None:
            rng = random

        tiles = cls._create_default_tiles()  # déjà triées par niveau

        if shuffle_tiles:
            # Mélange à l'intérieur de chaque niveau, sans mélanger les niveaux entre eux
            from collections import defaultdict

            buckets: dict[int, List[RuinTile]] = defaultdict(list)
            for tile in tiles:
                buckets[tile.level].append(tile)

            shuffled_tiles: List[RuinTile] = []
            for level in (1, 2, 3, 4):
                level_tiles = buckets[level]
                rng.shuffle(level_tiles)   # mélange dans la zone de profondeur
                shuffled_tiles.extend(level_tiles)

            tiles = shuffled_tiles

        # Case 0 : sous-marin
        spaces: List[Space] = [Space(is_submarine=True)]

        # Une case par tuile (version simple)
        for tile in tiles:
            space = Space(is_submarine=False, max_stack_size=max_stack_size)
            space.add_ruin(tile)
            spaces.append(space)

        return cls(spaces=spaces)


    @staticmethod
    def _create_default_tiles() -> List[RuinTile]:
        """
        Crée la liste complète des RuinTile selon la distribution officielle
        de Deep Sea Adventure, en respectant la profondeur :

        - Les tuiles de niveau 1 (0–3) sont au début de la liste.
        - Puis niveau 2 (4–7).
        - Puis niveau 3 (8–11).
        - Puis niveau 4 (12–15).

        À l'intérieur d'un même niveau, l'ordre est mélangé, mais
        on ne mélange jamais les niveaux entre eux.
        """
        tiles: List[RuinTile] = []

        # Distribution officielle (36 tuiles au total)
        level_values = {
            1: [0,0, 1,1, 2,2, 3,3],        # 12 tuiles
            2: [4,4, 5,5, 6,6, 7,7 ],        # 12 tuiles
            3: [8,8, 9,9, 10,10, 11,11],            # 8 tuiles
            4: [12, 12, 13, 13, 14, 14, 15, 15],                    # 4 tuiles
        }

        # On mélange l'ordre à l'intérieur de chaque niveau,
        # mais on conserve strictement l'ordre des niveaux.
        for level in (1, 2, 3, 4):
            values = level_values[level][:]
            random.shuffle(values)  # mélange *dans* la zone de profondeur

            for value in values:
                tiles.append(RuinTile(level=level, value=value))

        return tiles



    # ========================
    #  Propriétés utilitaires
    # ========================

    @property
    def size(self) -> int:
        """
        Nombre total de cases (y compris le sous-marin).
        """
        return len(self.spaces)

    @property
    def last_index(self) -> int:
        """
        Index de la dernière case du chemin.
        """
        return len(self.spaces) - 1

    @property
    def submarine_index(self) -> int:
        """
        Index du sous-marin (toujours 0 dans notre implémentation).

        On garde une propriété au cas où un jour tu veux rendre
        la position du sous-marin configurable.
        """
        return 0

    # ========================
    #  Accès aux cases
    # ========================

    def get_space(self, index: int) -> Space:
        """
        Renvoie la case à l'index donné.

        Lève IndexError si l'index est hors bornes.
        """
        return self.spaces[index]

    def __getitem__(self, index: int) -> Space:
        """
        Permet de faire board[index] pour accéder à une case.
        """
        return self.get_space(index)

    def __iter__(self):
        """
        Permet de boucler sur les cases du plateau :
        for space in board: ...
        """
        return iter(self.spaces)

    # ========================
    #  Représentations
    # ========================

    def __str__(self) -> str:
        """
        Représentation ASCII simplifiée du plateau sur une ligne.

        Exemple :
        SUB - [L1:0] - [L1:0] - [L1:1] - . - 3R - ...
        """
        return " - ".join(str(space) for space in self.spaces)

    def __repr__(self) -> str:
        return f"Board(spaces={self.spaces!r})"

    # ========================
    #  Sérialisation
    # ========================

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise le plateau sous forme de dict (JSON-friendly).

        Structure :
        {
            "spaces": [
                { ... },  # dict de Space.to_dict()
                ...
            ]
        }
        """
        return {
            "spaces": [space.to_dict() for space in self.spaces],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Board":
        """
        Recrée un plateau à partir d'un dict sérialisé.

        Paramètres
        ----------
        data : dict
            Dictionnaire contenant une clé 'spaces' avec une liste de dicts.

        Retour
        ------
        Board
            Nouvelle instance de Board.
        """
        spaces_data = data.get("spaces", [])
        spaces = [Space.from_dict(s) for s in spaces_data]
        return cls(spaces=spaces)

    # ========================
    #  Hooks d’extension
    # ========================

    def compress_path(self) -> None:
        """
        Compresse le chemin en fin de manche en retirant toutes les cases vides.

        Règle :
        - On conserve toujours la case du sous-marin (index 0).
        - On retire toutes les autres cases qui ne contiennent aucune ruine.
        - On conserve l'ordre des cases restantes.

        Les joueurs seront replacés au sous-marin en début de manche suivante.
        """
        # On suppose que le sous-marin est toujours la case 0
        submarine_space = self.spaces[0]

        new_spaces: list[Space] = [submarine_space]

        # On garde uniquement les cases non vides (hors sous-marin)
        for idx, space in enumerate(self.spaces):
            if idx == 0:
                continue
            if space.has_ruin:
                new_spaces.append(space)

        # Remplacement du chemin compressé
        self.spaces = new_spaces

        # Aucun besoin de toucher à submarine_index car il est déjà constant (0)
        # Aucun setter → on n'y touche pas !

    def drop_tiles_to_bottom(self, tiles: list[RuinTile], stack_size: int = 3) -> None:
        """
        Ajoute des tuiles au FOND du plateau, en créant de nouvelles cases
        et en empilant les trésors par piles de `stack_size` (par défaut 3).

        Les nouvelles cases sont ajoutées après la dernière case existante.
        """
        if not tiles:
            return

        # On crée des nouvelles cases en partant du chemin actuel
        current_stack: list[RuinTile] = []

        for tile in tiles:
            current_stack.append(tile)
            if len(current_stack) == stack_size:
                space = Space(is_submarine=False, max_stack_size=stack_size)
                for t in current_stack:
                    space.add_ruin(t)
                self.spaces.append(space)
                current_stack = []

        # S'il reste 1 ou 2 tuiles non empilées dans un lot complet
        if current_stack:
            space = Space(is_submarine=False, max_stack_size=stack_size)
            for t in current_stack:
                space.add_ruin(t)
            self.spaces.append(space)
