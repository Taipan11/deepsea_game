# src/ai_player.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from .player import Player
from .space import Space


class AIPlayer(Player, ABC):
    """
    Classe de base pour toutes les IA.
    Permet d'utiliser isinstance(player, AIPlayer) partout.
    """

    def __init__(self, name: str = "Bot", player_id: Optional[int] = None):
        super().__init__(name=name, player_id=player_id, is_ai=True)

    @abstractmethod
    def choose_direction(self, air_remaining: int) -> bool:
        """
        Retourne True si l'IA décide de remonter, False si elle continue à descendre.
        """
        raise NotImplementedError

    @abstractmethod
    def choose_action(self, space: Space, air_remaining: int) -> str:
        """
        Retourne "A", "B" ou "C" selon l'action choisie.
        """
        raise NotImplementedError


class AIPlayerNormal(AIPlayer):
    """
    IA "équilibrée" (ton IA actuelle).
    """

    def choose_direction(self, air_remaining: int) -> bool:
        # Déjà en mode remontée → continue à remonter
        if self.going_back:
            return True

        # Pas de trésor ? => aucun intérêt à remonter
        if self.carrying_count == 0:
            return False

        # Heuristique simple de "danger" selon l'air
        danger_threshold = 5 + 2 * self.carrying_count

        if air_remaining <= danger_threshold:
            return True

        return False

    def choose_action(self, space: Space, air_remaining: int) -> str:
        if not space.has_ruin:
            return "A"

        if self.going_back:
            if air_remaining <= 3 + self.carrying_count:
                return "A"

        safe_threshold = 3
        if air_remaining <= safe_threshold and self.carrying_count >= 3:
            return "A"

        return "B"


class AIPlayerCautious(AIPlayer):
    """
    IA prudente.
    Remonte plus tôt, prend moins de risques.
    """

    def choose_direction(self, air_remaining: int) -> bool:
        # Si elle remonte déjà : on continue
        if self.going_back:
            return True

        # 🧠 Idée : elle raisonne avec une grosse marge de sécurité
        # - sans trésor : elle n'ira PAS trop loin
        # - avec trésors : elle remonte très tôt

        if self.carrying_count == 0:
            # Si l'air descend en dessous de 16–18, elle commence à remonter
            # (tu peux ajuster 16/18 selon ton ressenti)
            return air_remaining <= 16

        # Avec des trésors, elle devient très frileuse
        # Plus elle est chargée, plus elle remonte tôt
        danger_threshold = 14 + 2 * self.carrying_count
        return air_remaining <= danger_threshold

    def choose_action(self, space: Space, air_remaining: int) -> str:
        # Pas de ruine -> rien à faire
        if not space.has_ruin:
            return "A"

        # Si elle remonte déjà : elle NE ramasse plus rien
        if self.going_back:
            return "A"

        # Si elle porte déjà 2 trésors, elle s'arrête là
        if self.carrying_count >= 2:
            return "A"

        # Si l'air commence à être un peu bas, elle ne prend plus
        if air_remaining <= 12:
            return "A"

        # Elle préfère les petits/moyens trésors (niveau <= 2)
        top = space.top_ruin
        if top and top.level <= 2:
            return "B"

        # Gros trésors trop profonds -> elle les laisse
        return "A"


class AIPlayerAdventurous(AIPlayer):
    """
    IA aventureuse.
    Descend longtemps, ramasse beaucoup.
    """

    def choose_direction(self, air_remaining: int) -> bool:
        if self.going_back:
            return True

        # Elle prend plus de risques : remonte très tard
        danger_threshold = 2 + 1 * self.carrying_count
        return air_remaining <= danger_threshold

    def choose_action(self, space: Space, air_remaining: int) -> str:
        if not space.has_ruin:
            return "A"

        if self.going_back:
            # Même en remontant elle peut encore ramasser si un peu d'air
            if air_remaining > 5:
                return "B"
            return "A"

        # En descente : très gourmande
        return "B"
