# src/ai_player.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from .player import Player
from .space import Space
from .ruin_tile import RuinTile

@dataclass
class AIPlayer(Player):
    """
    Joueur contrôlé par l'ordinateur.

    Cette IA utilise une stratégie simple basée sur :
    - l'air restant,
    - le nombre de trésors portés,
    - la présence ou non d'un trésor sur la case actuelle.

    Paramètres de stratégie
    -----------------------
    risk_carry_limit : int
        Nombre "raisonnable" de trésors que l'IA accepte de porter avant
        de préférer remonter.
    critical_air_threshold : int
        Niveau d'air sous lequel l'IA considère qu'il est dangereux de continuer
        à descendre.
    min_air_to_pickup : int
        Air minimum requis pour accepter de ramasser un nouveau trésor.
    """

    def __init__(
        self,
        name: str,
        player_id: Optional[int] = None,
        *,
        risk_carry_limit: int = 3,
        critical_air_threshold: int = 5,
        min_air_to_pickup: int = 3,
    ) -> None:
        super().__init__(name=name, player_id=player_id, is_ai=True)

        if risk_carry_limit <= 0:
            raise ValueError("risk_carry_limit doit être >= 1.")
        if critical_air_threshold < 0:
            raise ValueError("critical_air_threshold doit être >= 0.")
        if min_air_to_pickup < 0:
            raise ValueError("min_air_to_pickup doit être >= 0.")

        self.risk_carry_limit = risk_carry_limit
        self.critical_air_threshold = critical_air_threshold
        self.min_air_to_pickup = min_air_to_pickup

    # =========================
    #  Décisions de l'IA
    # =========================

    def choose_direction(self, air_remaining: int) -> bool:
        """
        Décide si l'IA doit remonter ou continuer à descendre.

        Paramètres
        ----------
        air_remaining : int
            Air restant dans le sous-marin au début du tour.

        Retour
        ------
        bool
            True si l'IA choisit de remonter,
            False si elle choisit de descendre.

        Stratégie (simple) :
        - Si elle est au sous-marin (position 0) : elle commence à descendre.
        - Si elle remonte déjà : elle continue à remonter.
        - Sinon :
          * Si l'air est sous critical_air_threshold -> remonte.
          * Si elle porte au moins risk_carry_limit trésors -> remonte.
          * Sinon, continue à descendre.
        """
        # Premier tour : au sous-marin, on doit commencer par descendre.
        if self.is_on_submarine:
            self.continue_descending()
            return False

        # Si elle remonte déjà, on continue la remontée (comportement conservateur).
        if self.going_back:
            return True

        # Décision basée sur l'air et les trésors portés
        if air_remaining <= self.critical_air_threshold:
            self.start_going_back()
            return True

        if self.carrying_count >= self.risk_carry_limit:
            self.start_going_back()
            return True

        # Sinon, elle continue à descendre
        self.continue_descending()
        return False

    def choose_action(self, current_space: Space, air_remaining: int) -> str:
        """
        Décide l'action à effectuer sur la case actuelle.

        Paramètres
        ----------
        current_space : Space
            Case sur laquelle se trouve actuellement l'IA.
        air_remaining : int
            Air restant après la consommation liée aux trésors portés au début du tour.

        Retour
        ------
        str
            Code d'action :
            - "A" : ne rien faire
            - "B" : ramasser un jeton de ruines (si disponible)
            - (plus tard : "C" pour poser un trésor, etc.)

        Stratégie (simple) :
        - Si la case n'a pas de ruines -> "A".
        - Si l'air est trop bas (< min_air_to_pickup) -> "A".
        - Si l'IA porte déjà beaucoup de trésors et que l'air est bas ->
          tendance à "A" pour limiter les risques.
        - Sinon, "B" (ramasser un trésor).
        """
        # Pas de ruine ici -> rien à faire
        if not current_space.has_ruin:
            return "A"

        # Air trop faible pour prendre le risque de ramasser
        if air_remaining <= self.min_air_to_pickup:
            return "A"

        # Déjà chargé et air bas -> rester prudent
        if (
            self.carrying_count >= self.risk_carry_limit
            and air_remaining <= self.critical_air_threshold + 2
        ):
            return "A"

        # Sinon, on ramasse volontiers
        return "B"

    # =========================
    #  Sérialisation (override)
    # =========================

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise l'état de l'IA, en ajoutant les paramètres de stratégie.

        On ajoute :
        - "ai_type": pour pouvoir distinguer différentes IA plus tard,
        - "ai_params": dictionnaire des paramètres de stratégie.
        """
        base = super().to_dict()
        base["ai_type"] = "basic"
        base["ai_params"] = {
            "risk_carry_limit": self.risk_carry_limit,
            "critical_air_threshold": self.critical_air_threshold,
            "min_air_to_pickup": self.min_air_to_pickup,
        }
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIPlayer":
        """
        Recrée une AIPlayer à partir d'un dict sérialisé.

        Note : on ignore `ai_type` pour l'instant (une seule IA).
        """
        params = data.get("ai_params", {}) or {}

        player = cls(
            name=data["name"],
            player_id=data.get("player_id"),
            risk_carry_limit=int(params.get("risk_carry_limit", 3)),
            critical_air_threshold=int(params.get("critical_air_threshold", 5)),
            min_air_to_pickup=int(params.get("min_air_to_pickup", 3)),
        )

        # On réapplique l'état générique depuis Player.to_dict
        player.position = int(data.get("position", 0))
        player.going_back = bool(data.get("going_back", False))
        player.has_returned = bool(data.get("has_returned", False))

        carrying_data = data.get("carrying", [])
        player.carrying = [RuinTile.from_dict(t) for t in carrying_data]

        score_data = data.get("score_tiles", [])
        player.score_tiles = [RuinTile.from_dict(t) for t in score_data]

        return player
