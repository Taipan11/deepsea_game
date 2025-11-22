# dice.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import random


@dataclass
class Dice:
    """
    Représente un ensemble de dés.

    Par défaut, ce modèle reproduit les dés de Deep Sea Adventure :
    - 2 dés, chacun avec des valeurs de 1 à 3.

    Attributs
    ---------
    num_dice : int
        Nombre de dés lancés à chaque tirage.
    faces : int
        Nombre de faces par dé. Les valeurs vont de 1 à `faces` inclus.
    rng : Optional[random.Random]
        Générateur pseudo-aléatoire utilisé pour les tirages.
        Si None, on utilise le module `random` global.
    """

    num_dice: int = 2
    faces: int = 3
    rng: Optional[random.Random] = None

    def __post_init__(self) -> None:
        """
        Valide les paramètres du set de dés.
        """
        if self.num_dice <= 0:
            raise ValueError(f"num_dice doit être >= 1, reçu : {self.num_dice}")
        if self.faces <= 0:
            raise ValueError(f"faces doit être >= 1, reçu : {self.faces}")

        # Si aucun RNG fourni, on prend le module global
        if self.rng is None:
            self.rng = random.Random()

    # --------- Méthodes de tirage ---------

    def roll_individual(self) -> List[int]:
        """
        Lance chaque dé et renvoie la liste des résultats individuels.

        Retour
        ------
        List[int]
            Liste de longueur `num_dice`, avec une valeur entre 1 et `faces` pour chaque dé.
        """
        assert self.rng is not None  # pour aider les analyseurs statiques
        return [self.rng.randint(1, self.faces) for _ in range(self.num_dice)]

    def roll(self) -> int:
        """
        Lance les dés et renvoie la somme des résultats.

        C'est cette méthode que tu utiliseras dans le moteur de jeu.
        """
        results = self.roll_individual()
        return sum(results)

    # --------- Représentation ---------

    def __str__(self) -> str:
        """
        Représentation courte du set de dés.
        """
        return f"{self.num_dice}d{self.faces}"

    def __repr__(self) -> str:
        return f"Dice(num_dice={self.num_dice}, faces={self.faces})"
