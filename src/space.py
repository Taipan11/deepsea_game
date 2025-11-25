from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from .ruin_tile import RuinTile


@dataclass
class Space:
    """
    Représente une case du chemin sous-marin.

    Attributs
    ---------
    is_submarine : bool
        Indique si cette case est le sous-marin (case 0).
        Le sous-marin ne doit contenir aucun jeton de ruines.
    ruins : List[RuinTile]
        Liste des jetons de ruines présents sur cette case.
        On considère cela comme une pile : le dernier ajouté est le premier ramassé.
    max_stack_size : Optional[int]
        Nombre maximum de ruines autorisées sur cette case.
        Si None, aucune limite n'est imposée (utile pour simplifier au début,
        puis pour activer la règle des piles de 3 plus tard).
    """

    is_submarine: bool = False
    ruins: List[RuinTile] = field(default_factory=list)
    max_stack_size: Optional[int] = None

    def __post_init__(self) -> None:
        """
        Valide la cohérence initiale de la case.
        """
        if self.is_submarine and self.ruins:
            raise ValueError("Une case sous-marin ne peut pas contenir de ruines.")

        if self.max_stack_size is not None and len(self.ruins) > self.max_stack_size:
            raise ValueError(
                f"La case contient déjà {len(self.ruins)} ruines, "
                f"ce qui dépasse la limite {self.max_stack_size}."
            )

    # --------- Propriétés utiles ---------

    @property
    def has_ruin(self) -> bool:
        """
        Indique si la case contient au moins un jeton de ruines.
        """
        return len(self.ruins) > 0

    @property
    def ruin_count(self) -> int:
        """
        Nombre de ruines présentes sur cette case.
        """
        return len(self.ruins)

    @property
    def is_empty(self) -> bool:
        """
        Indique si la case ne contient aucune ruine (et n'est pas le sous-marin).
        """
        return not self.ruins

    @property
    def top_ruin(self) -> Optional[RuinTile]:
        """
        Renvoie le jeton au sommet de la pile (sans le retirer),
        ou None si la case est vide.
        """
        if not self.ruins:
            return None
        return self.ruins[-1]

    # --------- Gestion des ruines ---------

    def add_ruin(self, tile: RuinTile) -> None:
        """
        Ajoute un jeton de ruines sur la case.

        Lève une erreur si :
        - la case est le sous-marin,
        - la taille maximale de pile est atteinte (si max_stack_size est défini).
        """
        if self.is_submarine:
            raise ValueError("Impossible d'ajouter un jeton sur le sous-marin.")

        if self.max_stack_size is not None and len(self.ruins) >= self.max_stack_size:
            raise ValueError(
                f"Impossible d'ajouter un jeton : pile pleine ({self.max_stack_size})."
            )

        self.ruins.append(tile)

    def push_ruin(self, tile: RuinTile) -> None:
        """
        Pose un trésor sur cette case.
        Dans DSA, on le pose face cachée, mais côté moteur on s’en fiche.
        """
        self.ruins.append(tile)

    def pop_ruin(self) -> Optional[RuinTile]:
        """
        Retire et renvoie le jeton de ruines au sommet de la pile.

        Retourne None si la case est vide.
        """
        if not self.ruins:
            return None
        return self.ruins.pop()

    def remove_all_ruins(self) -> List[RuinTile]:
        """
        Retire toutes les ruines de la case et les renvoie dans une liste.

        Utile si un joueur ramasse toute la pile (variante), ou pour des règles
        spéciales de réorganisation du plateau.
        """
        tiles = self.ruins[:]
        self.ruins.clear()
        return tiles

    # --------- Représentation ---------

    def __str__(self) -> str:
        """
        Représentation courte pour l'affichage ASCII du plateau.

        - Sous-marin : 'SUB'
        - Case vide : '.'
        - Case avec 1 ruine : str(ruine)
        - Case avec plusieurs ruines : 'nR', où n est le nombre de ruines.
          (à affiner si tu veux afficher la valeur du dessus)
        """
        if self.is_submarine:
            return "SUB"

        if not self.ruins:
            return "."

        if len(self.ruins) == 1:
            # Repose sur le __str__ de RuinTile, ex: [L2:7]
            return str(self.ruins[0])

        # Plusieurs ruines : on peut choisir l'affichage comme "3R" pour 3 ruines
        return f"{len(self.ruins)}R"

    def __repr__(self) -> str:
        """
        Représentation détaillée pour le debug.
        """
        return (
            f"Space(is_submarine={self.is_submarine}, "
            f"ruins={self.ruins!r}, "
            f"max_stack_size={self.max_stack_size})"
        )

    # --------- Sérialisation ---------

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise la case sous forme de dict simple (JSON-friendly).

        Exemple de structure :
        {
            "is_submarine": false,
            "max_stack_size": 3,
            "ruins": [
                {"level": 1, "value": 0},
                {"level": 1, "value": 1}
            ]
        }
        """
        return {
            "is_submarine": self.is_submarine,
            "max_stack_size": self.max_stack_size,
            "ruins": [tile.to_dict() for tile in self.ruins],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Space":
        """
        Recrée une case à partir d'un dict sérialisé.

        Paramètres
        ----------
        data : dict
            Dictionnaire contenant 'is_submarine', 'max_stack_size' (optionnel),
            et une liste 'ruins' de dicts représentant des RuinTile.

        Retour
        ------
        Space
            Nouvelle instance de Space.
        """
        ruins_data = data.get("ruins", [])
        ruins = [RuinTile.from_dict(t) for t in ruins_data]

        return cls(
            is_submarine=bool(data.get("is_submarine", False)),
            max_stack_size=data.get("max_stack_size"),
            ruins=ruins,
        )
