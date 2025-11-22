# ruin_tile.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass(frozen=True)
class RuinTile:
    """
    Représente un jeton de ruines dans Deep Sea Adventure.

    Attributs
    ---------
    level : int
        Niveau de profondeur (entre 1 et 4 inclus).
        1 = proche du sous-marin, 4 = très profond.
    value : int
        Valeur en points du jeton (en général entre 0 et 15).
    """

    level: int
    value: int

    def __post_init__(self) -> None:
        """
        Valide les données du jeton après initialisation.

        On utilise __post_init__ malgré le dataclass frozen pour
        vérifier la cohérence des données, en levant des erreurs
        explicites si nécessaire.
        """
        if not (1 <= self.level <= 4):
            raise ValueError(f"RuinTile.level doit être entre 1 et 4, reçu: {self.level}")

        if not isinstance(self.value, int):
            raise TypeError(f"RuinTile.value doit être un int, reçu: {type(self.value)}")

        if self.value < 0:
            raise ValueError(f"RuinTile.value doit être >= 0, reçu: {self.value}")

    # --------- Propriétés utiles ---------

    @property
    def is_shallow(self) -> bool:
        """
        Indique si le jeton est dans une zone peu profonde (niveau 1 ou 2).

        Cela peut être utile plus tard si tu veux adapter la stratégie de l'IA
        en fonction de la profondeur.
        """
        return self.level <= 2

    @property
    def is_deep(self) -> bool:
        """
        Indique si le jeton est dans une zone profonde (niveau 3 ou 4).
        """
        return self.level >= 3

    # --------- Représentations ---------

    def __str__(self) -> str:
        """
        Représentation courte, utilisable dans l'affichage ASCII du plateau.

        Exemple : "[L2:7]" pour niveau 2, valeur 7.
        """
        return f"[L{self.level}:{self.value}]"

    def __repr__(self) -> str:
        """
        Représentation détaillée pour le debug / logs.
        """
        return f"RuinTile(level={self.level}, value={self.value})"

    # --------- Sérialisation ---------

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise le jeton sous forme de dict simple (JSON-friendly).

        Exemple de résultat :
        {
            "level": 2,
            "value": 7
        }
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuinTile":
        """
        Recrée un jeton à partir d'un dict sérialisé.

        Paramètres
        ----------
        data : dict
            Dictionnaire contenant au moins 'level' et 'value'.

        Retour
        ------
        RuinTile
            Nouvelle instance de RuinTile.
        """
        return cls(
            level=int(data["level"]),
            value=int(data["value"]),
        )
