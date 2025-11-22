# player.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .ruin_tile import RuinTile


@dataclass
class Player:
    """
    Représente un joueur de Deep Sea Adventure (humain ou IA).

    Cette classe gère l'état générique du joueur :
    - position sur le plateau,
    - trésors portés,
    - trésors définitivement gagnés (score),
    - direction (descend / remonte).

    La logique de décision (IA) sera implémentée dans une sous-classe dédiée.
    """

    name: str
    # Optionnel : identifiant unique si tu veux gérer des joueurs
    # dans une sauvegarde ou un réseau.
    player_id: Optional[int] = None
    # Indicateur simple pour savoir si ce joueur est contrôlé par l'IA ou un humain.
    # La vraie logique IA sera dans une classe dérivée (AIPlayer).
    is_ai: bool = False

    # --- Champs d'état initialisés dans reset_for_new_game() / reset_for_new_round() ---

    # Position sur le plateau (index de case dans Board.spaces)
    position: int = field(default=0, init=False)
    # True si le joueur a décidé / est en train de remonter.
    going_back: bool = field(default=False, init=False)
    # True si le joueur est revenu au sous-marin dans la manche courante.
    has_returned: bool = field(default=False, init=False)

    # Trésors portés actuellement (perdus si le joueur ne revient pas).
    carrying: List[RuinTile] = field(default_factory=list, init=False)
    # Trésors définitivement gagnés (score cumulé sur la partie).
    score_tiles: List[RuinTile] = field(default_factory=list, init=False)

    # =========================
    #  Initialisation / reset
    # =========================

    def reset_for_new_game(self) -> None:
        """
        Réinitialise complètement le joueur pour une nouvelle partie.

        - Efface les trésors définitivement gagnés.
        - Réinitialise l'état de manche.
        """
        self.score_tiles.clear()
        self.reset_for_new_round()

    def reset_for_new_round(self) -> None:
        """
        Réinitialise l'état du joueur pour une nouvelle manche.

        - Replace le joueur au sous-marin.
        - Vide les trésors portés.
        - Réinitialise la direction et le statut de retour.
        """
        self.position = 0
        self.going_back = False
        self.has_returned = False
        self.carrying.clear()

    # =========================
    #  Propriétés utiles
    # =========================

    @property
    def carrying_count(self) -> int:
        """
        Nombre de trésors actuellement portés par le joueur.
        """
        return len(self.carrying)

    @property
    def total_score(self) -> int:
        """
        Score total du joueur (somme des valeurs des trésors définitifs).
        """
        return sum(tile.value for tile in self.score_tiles)

    @property
    def is_on_submarine(self) -> bool:
        """
        Indique si le joueur est actuellement sur la case du sous-marin
        (index 0 dans notre modèle actuel).
        """
        return self.position == 0

    # =========================
    #  Gestion de la position
    # =========================

    def move_to(self, new_position: int) -> None:
        """
        Déplace le joueur vers un nouvel index de case.

        Cette méthode ne gère pas la logique de limites du plateau :
        c'est la responsabilité du moteur de jeu (Game / Board).

        Elle se contente de mettre à jour la position.
        """
        if new_position < 0:
            raise ValueError(f"new_position doit être >= 0, reçu : {new_position}")
        self.position = new_position

    def start_going_back(self) -> None:
        """
        Fait passer le joueur en mode remontée.
        """
        self.going_back = True

    def continue_descending(self) -> None:
        """
        Indique que le joueur continue à descendre.
        (On ne force pas going_back à False si déjà True dans certaines règles,
        mais tu peux adapter selon ta logique de choix dans Game.)
        """
        self.going_back = False

    def mark_as_returned(self) -> None:
        """
        Marque le joueur comme revenu au sous-marin.
        """
        self.has_returned = True
        self.position = 0  # on considère qu'il est physiquement sur le sous-marin

    # =========================
    #  Gestion des trésors
    # =========================

    def take_ruin(self, tile: RuinTile) -> None:
        """
        Ajoute un jeton de ruines à la liste des trésors portés.
        """
        self.carrying.append(tile)

    def drop_ruin(self, tile: RuinTile) -> None:
        """
        Retire un jeton spécifique de la liste des trésors portés, s'il est présent.

        Si le jeton n'est pas trouvé, cette méthode ne fait rien.
        """
        try:
            self.carrying.remove(tile)
        except ValueError:
            # Le jeton n'était pas porté, on ignore silencieusement
            pass

    def drop_all_carrying(self) -> List[RuinTile]:
        """
        Retire tous les trésors portés et les renvoie dans une liste.

        Utile quand un joueur se noie ou pour les règles de défausse.
        """
        dropped = self.carrying[:]
        self.carrying.clear()
        return dropped

    def secure_carried_treasures(self) -> None:
        """
        Transfère tous les trésors portés vers les trésors définitivement gagnés.

        À utiliser en fin de manche si le joueur est revenu au sous-marin.
        """
        if not self.carrying:
            return
        self.score_tiles.extend(self.carrying)
        self.carrying.clear()

    # =========================
    #  Représentation
    # =========================

    def __str__(self) -> str:
        """
        Représentation lisible pour l'affichage en ASCII.
        """
        direction = "↑" if self.going_back else "↓"
        pos_str = "Sous-marin" if self.is_on_submarine else f"Case {self.position}"
        role = "IA" if self.is_ai else "Humain"
        return (
            f"{self.name} ({role}) - "
            f"Pos: {pos_str} {direction}, "
            f"Trésors portés: {self.carrying_count}, "
            f"Score: {self.total_score}"
        )

    def __repr__(self) -> str:
        return (
            f"Player(name={self.name!r}, player_id={self.player_id!r}, "
            f"is_ai={self.is_ai}, position={self.position}, "
            f"going_back={self.going_back}, has_returned={self.has_returned}, "
            f"carrying={self.carrying!r}, score_tiles={self.score_tiles!r})"
        )

    # =========================
    #  Sérialisation
    # =========================

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise l'état du joueur sous forme de dict (JSON-friendly).

        Note : on ne sérialise pas la distinction exacte de la classe (Player vs AIPlayer)
        ici. Tu pourras gérer ça en ajoutant une clé "type" dans une sous-classe.
        """
        return {
            "name": self.name,
            "player_id": self.player_id,
            "is_ai": self.is_ai,
            "position": self.position,
            "going_back": self.going_back,
            "has_returned": self.has_returned,
            "carrying": [t.to_dict() for t in self.carrying],
            "score_tiles": [t.to_dict() for t in self.score_tiles],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """
        Recrée un joueur à partir d'un dict sérialisé.

        Attention : cette méthode recrée un Player "de base".
        Si tu as des sous-classes (AIPlayer), tu pourras surcharger cette méthode
        ou utiliser un factory externe pour instancier le bon type.
        """
        player = cls(
            name=data["name"],
            player_id=data.get("player_id"),
            is_ai=bool(data.get("is_ai", False)),
        )

        player.position = int(data.get("position", 0))
        player.going_back = bool(data.get("going_back", False))
        player.has_returned = bool(data.get("has_returned", False))

        # On reconstruit les trésors portés
        carrying_data = data.get("carrying", [])
        player.carrying = [RuinTile.from_dict(t) for t in carrying_data]

        # On reconstruit les trésors de score
        score_data = data.get("score_tiles", [])
        player.score_tiles = [RuinTile.from_dict(t) for t in score_data]

        return player
