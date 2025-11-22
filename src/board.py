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

        Paramètres
        ----------
        max_stack_size : Optional[int]
            Limite de jetons par case (None = illimité).
            Tu pourras par exemple mettre 3 pour activer la règle des piles de 3 plus tard.
        shuffle_tiles : bool
            Si True, mélange les jetons avant de les placer.
        rng : Optional[random.Random]
            Générateur pseudo-aléatoire à utiliser (pour tests reproductibles).
            Si None, on utilise le module random global.

        Retour
        ------
        Board
            Un nouveau plateau initialisé.
        """
        if rng is None:
            rng = random

        tiles = cls._create_default_tiles()
        if shuffle_tiles:
            rng.shuffle(tiles)

        # Case 0 : sous-marin
        spaces: List[Space] = [Space(is_submarine=True)]

        # Une case par tuile (version simple) :
        # plus tard tu pourras changer la distribution si tu veux regrouper des piles.
        for tile in tiles:
            space = Space(is_submarine=False, max_stack_size=max_stack_size)
            space.add_ruin(tile)
            spaces.append(space)

        return cls(spaces=spaces)

    @staticmethod
    def _create_default_tiles() -> List[RuinTile]:
        """
        Crée la liste complète des RuinTile selon la distribution standard.

        Pour l’instant on prend un modèle simplifié :
        - Niveau 1 : valeurs 0 à 3 (x2 de chaque)
        - Niveau 2 : valeurs 4 à 7 (x2 de chaque)
        - Niveau 3 : valeurs 8 à 11 (x2 de chaque)
        - Niveau 4 : valeurs 12 à 15 (x2 de chaque)

        Si tu veux coller exactement aux règles, tu pourras ajuster cette méthode
        sans toucher au reste du code.
        """
        tiles: List[RuinTile] = []

        distributions = [
            (1, 0, 3),
            (2, 4, 7),
            (3, 8, 11),
            (4, 12, 15),
        ]

        for level, start_val, end_val in distributions:
            for value in range(start_val, end_val + 1):
                tiles.append(RuinTile(level=level, value=value))
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
        (Hook pour plus tard) :
        Implémenter ici la règle de compression du chemin entre les manches.

        Idée possible :
        - retirer les cases vides au-delà de la dernière ruine,
        - ou rapprocher certaines piles, etc.

        Pour l’instant, cette méthode ne fait rien.
        """
        # TODO: implémenter la compression du chemin selon les règles complètes
        pass
