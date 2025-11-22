# src/ai_player.py
from __future__ import annotations

from typing import Optional
from .player import Player
from .space import Space


class AIPlayer(Player):
    """
    Un joueur contrôlé par l'IA.

    Il utilise des heuristiques simples basées sur :
    - l'air restant,
    - le nombre de trésors portés,
    - sa position sur le plateau.
    """

    def __init__(self, name: str = "Bot", player_id: Optional[int] = None):
        super().__init__(name=name, player_id=player_id, is_ai=True)

    # ----------------------------
    #  Choix de direction
    # ----------------------------
    def choose_direction(self, air_remaining: int) -> bool:
        """
        Retourne True si l'IA décide de remonter, False si elle continue à descendre.

        Heuristique :
        - Si elle n'a AUCUN trésor => continue à descendre.
        - Si elle a des trésors :
            * si l'air est encore confortable => continue un peu à descendre.
            * si l'air devient bas => commence à remonter.
        """
        # Déjà en mode remontée → continue à remonter
        if self.going_back:
            return True

        # Pas de trésor ? => aucun intérêt à remonter
        if self.carrying_count == 0:
            return False

        # Heuristique simple de "danger" selon l'air
        # Plus tu portes de trésors, plus tu consommes d'air
        # On se donne une marge de sécurité grossière :
        danger_threshold = 5 + 2 * self.carrying_count

        if air_remaining <= danger_threshold:
            # 🛟 On commence à remonter
            return True

        # Sinon on continue à descendre
        return False

    # ----------------------------
    #  Choix d'action sur la case
    # ----------------------------
    def choose_action(self, space: Space, air_remaining: int) -> str:
        """
        Choisit "A" (ne rien faire) ou "B" (ramasser un trésor).

        Heuristique :
        - Si pas de ruine sur la case → "A"
        - Si on remonte et que l'air est vraiment bas → évite de prendre encore du poids.
        - Si on est en descente ou encore avec assez d'air → ramasse ("B").
        """
        # S'il n'y a aucun trésor, aucune action à faire
        if not space.has_ruin:
            return "A"

        # Si on remonte déjà et que l'air devient très faible → ne prend plus
        if self.going_back:
            # seuil plus strict quand on remonte
            if air_remaining <= 3 + self.carrying_count:
                return "A"

        # Heuristique globale : si l'air est encore correct -> on ramasse
        # (tu peux raffiner, mais c'est déjà fun)
        safe_threshold = 3
        if air_remaining <= safe_threshold and self.carrying_count >= 3:
            # Trop chargé, plus assez d'air => on arrête de greed
            return "A"

        # Par défaut, l'IA est gourmande : elle ramasse
        return "B"
