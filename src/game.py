# game.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .board import Board
from .dice import Dice
from .player import Player
from .space import Space
from .ruin_tile import RuinTile


@dataclass
class TurnResult:
    """
    Résume ce qui s'est passé pendant la phase de déplacement d'un tour.

    Attributs
    ---------
    player_index : int
        Index du joueur dans la liste Game.players.
    player_name : str
        Nom du joueur.
    round_number : int
        Numéro de la manche en cours (1..N).
    air_before : int
        Air disponible avant de tenir compte des trésors portés.
    air_after : int
        Air après consommation liée aux trésors portés.
    dice_roll : int
        Résultat brut du lancer de dés (avant pénalité lié aux trésors).
    move_distance : int
        Distance réellement parcourue (après pénalité).
    initial_position : int
        Position de départ du joueur (index de case).
    final_position : int
        Position d'arrivée du joueur.
    reached_submarine : bool
        True si le joueur est revenu au sous-marin pendant ce mouvement.
    can_act_on_space : bool
        True si le joueur peut encore effectuer une action sur la case
        (ramasser/poser un trésor). False si c'est impossible
        (par exemple parce qu'il est sur le sous-marin).
    """

    player_index: int
    player_name: str
    round_number: int
    air_before: int
    air_after: int
    dice_roll: int
    move_distance: int
    initial_position: int
    final_position: int
    reached_submarine: bool
    can_act_on_space: bool


class Game:
    """
    Moteur de jeu Deep Sea Adventure (version simplifiée).

    Cette classe ne gère pas d'input/output : elle encapsule uniquement
    la logique du jeu. Une interface (CLI, GUI...) vient s'y brancher.

    Responsabilités :
    - gérer le plateau, l'air, les manches et les tours,
    - déplacer les joueurs,
    - appliquer les actions (ramasser trésors),
    - gérer les scores en fin de manche.

    Elle n'envoie pas de prints, ne lit pas de input.
    """

    def __init__(
        self,
        players: List[Player],
        *,
        num_rounds: int = 3,
        air_per_round: int = 25,
        board: Optional[Board] = None,
        dice: Optional[Dice] = None,
    ) -> None:
        if not 2 <= len(players) <= 6:
            raise ValueError("Deep Sea Adventure se joue de 2 à 6 joueurs.")
        if num_rounds <= 0:
            raise ValueError("num_rounds doit être >= 1.")
        if air_per_round <= 0:
            raise ValueError("air_per_round doit être >= 1.")

        self.players: List[Player] = players
        self.num_rounds: int = num_rounds
        self.air_per_round: int = air_per_round

        self.board: Board = board if board is not None else Board.create_default()
        self.dice: Dice = dice if dice is not None else Dice()

        self.round_number: int = 1
        self.air: int = air_per_round
        self.current_player_index: int = 0

        # On prépare la première manche
        self._reset_all_players_for_new_game()

    # =========================
    #  Initialisation / reset
    # =========================

    def _reset_all_players_for_new_game(self) -> None:
        """
        Réinitialise tous les joueurs pour une nouvelle partie.
        """
        for p in self.players:
            p.reset_for_new_game()

    def start_new_round(self) -> None:
        """
        Prépare et démarre une nouvelle manche :
        - recrée un plateau,
        - réinitialise l'air,
        - remet tous les joueurs au sous-marin.
        """
        self.board = Board.create_default()
        self.air = self.air_per_round
        for p in self.players:
            p.reset_for_new_round()
        self.current_player_index = 0

    # =========================
    #  Propriétés d'état
    # =========================

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def is_last_round(self) -> bool:
        return self.round_number >= self.num_rounds

    def is_round_over(self) -> bool:
        """
        La manche se termine si :
        - l'air est à 0 ou moins, ou
        - tous les joueurs sont revenus au sous-marin.
        """
        if self.air <= 0:
            return True
        if all(p.has_returned for p in self.players):
            return True
        return False

    def is_game_over(self) -> bool:
        """
        La partie est terminée si on a terminé toutes les manches prévues.
        """
        return self.round_number > self.num_rounds

    # =========================
    #  Gestion du tour
    # =========================

    def begin_turn(self, player: Player, going_back: bool) -> TurnResult:
        if player.has_returned:
            raise RuntimeError("begin_turn appelé sur un joueur déjà revenu.")

        # =========================
        #  Règles de direction
        # =========================
        # - Si le joueur est déjà en train de remonter : il CONTINUE à remonter.
        # - Sinon, au sous-marin en début de manche : obligation de descendre.
        # - Sinon : on suit le choix `going_back` donné par l’UI / IA.

        if player.going_back:
            effective_going_back = True
        else:
            if player.is_on_submarine and not player.has_returned:
                # Premier déplacement de la manche -> obligé de descendre
                effective_going_back = False
            else:
                effective_going_back = going_back

        # Applique la direction effective
        if effective_going_back:
            player.start_going_back()
        else:
            player.continue_descending()

        # =========================
        #  Air & déplacement
        # =========================

        air_before = self.air
        penalty = player.carrying_count
        self.air -= penalty
        air_after = self.air

        dice_roll = self.dice.roll()
        move_distance = dice_roll - penalty
        if move_distance < 0:
            move_distance = 0

        initial_position = player.position
        reached_submarine = self._move_player(player, move_distance)
        final_position = player.position

        can_act = (not player.is_on_submarine) and (self.air > 0)

        return TurnResult(
            player_index=self.players.index(player),
            player_name=player.name,
            round_number=self.round_number,
            air_before=air_before,
            air_after=air_after,
            dice_roll=dice_roll,
            move_distance=move_distance,
            initial_position=initial_position,
            final_position=final_position,
            reached_submarine=reached_submarine,
            can_act_on_space=can_act,
        )


    def _move_player(self, player: Player, moves: int) -> bool:
        """
        Déplace le joueur d'un certain nombre de cases dans la direction indiquée
        par player.going_back.

        Respecte :
        - les limites du plateau,
        - le retour au sous-marin en remontée.

        Retour
        ------
        bool
            True si le joueur a atteint le sous-marin pendant ce déplacement.
        """
        if moves <= 0:
            return False

        direction = -1 if player.going_back else 1
        steps_left = moves

        while steps_left > 0:
            next_pos = player.position + direction

            # Descente : ne pas dépasser la dernière case
            if not player.going_back and next_pos > self.board.last_index:
                break

            # Remontée : si on atteint ou dépasse le sous-marin
            if player.going_back and next_pos <= self.board.submarine_index:
                player.mark_as_returned()
                return True

            player.move_to(next_pos)
            steps_left -= 1

        # Si on a fini exactement sur le sous-marin en remontée
        if player.going_back and player.is_on_submarine:
            player.mark_as_returned()
            return True

        return False

    def perform_action(self, player: Player, action_code: str) -> Optional[RuinTile]:
        """
        Applique une action du joueur sur la case courante.

        Paramètres
        ----------
        player : Player
            Joueur dont c'est le tour, déjà déplacé par begin_turn().
        action_code : str
            Code d'action :
            - "A" : ne rien faire
            - "B" : ramasser un jeton de ruines (si disponible)
            (plus tard : "C" pour poser un trésor, etc.)

        Retour
        ------
        Optional[RuinTile]
            Le jeton ramassé si l'action B a réussi, sinon None.
        """
        if player.is_on_submarine:
            # Au sous-marin, il n'y a pas d'action de fouille.
            return None

        space: Space = self.board.get_space(player.position)

        code = action_code.upper().strip()
        if code == "A":
            return None

        if code == "B":
            if not space.has_ruin:
                return None
            tile = space.pop_ruin()
            if tile is not None:
                player.take_ruin(tile)
            return tile

        # Actions futures (C, D, ...) pourront être gérées ici
        return None

    def advance_to_next_player(self) -> None:
        """
        Passe au joueur suivant qui n'est pas encore revenu.
        Si tous les joueurs ont has_returned = True, on s'arrête simplement :
        is_round_over() détectera la fin de manche.
        """
        nb_players = len(self.players)
        for _ in range(nb_players):
            self.current_player_index = (self.current_player_index + 1) % nb_players
            if not self.current_player.has_returned:
                break


    # =========================
    #  Fin de manche / partie
    # =========================

    def end_round(self) -> None:
        """
        Applique la fin de manche :

        - Les joueurs revenus au sous-marin sécurisent leurs trésors portés.
        - Les autres perdent tous leurs trésors portés.
        """
        for p in self.players:
            if p.is_on_submarine:
                p.secure_carried_treasures()
            else:
                p.drop_all_carrying()

        # Hook pour éventuellement compresser le chemin entre les manches
        self.board.compress_path()

    def next_round(self) -> None:
        """
        Passe à la manche suivante, si possible.
        """
        self.round_number += 1
        if not self.is_game_over():
            self.start_new_round()

    # =========================
    #  Scores / infos
    # =========================

    def get_scores(self) -> Dict[str, int]:
        """
        Renvoie un dict {nom_joueur: score_total}.
        """
        return {p.name: p.total_score for p in self.players}

    def get_winners(self) -> List[Player]:
        """
        Renvoie la liste des joueurs ayant le meilleur score.
        (Plusieurs joueurs en cas d'égalité.)
        """
        scores = [p.total_score for p in self.players]
        max_score = max(scores) if scores else 0
        return [p for p in self.players if p.total_score == max_score]

    # =========================
    #  Affichage ASCII (helpers)
    # =========================

    def get_board_ascii(self) -> str:
        """
        Renvoie une représentation ASCII du plateau sur une seule ligne.
        (Ne fait pas de print ; à toi de l'afficher.)
        """
        return str(self.board)

    def get_players_status_ascii(self) -> List[str]:
        """
        Renvoie une liste de chaînes décrivant l'état de chaque joueur,
        utilisable directement pour un affichage texte.
        """
        return [str(p) for p in self.players]

    # =========================
    #  Sérialisation
    # =========================

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise l'état de la partie (pour sauvegarde).
        """
        return {
            "num_rounds": self.num_rounds,
            "air_per_round": self.air_per_round,
            "round_number": self.round_number,
            "air": self.air,
            "current_player_index": self.current_player_index,
            "board": self.board.to_dict(),
            "players": [p.to_dict() for p in self.players],
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        *,
        player_factory=None,
    ) -> "Game":
        """
        Recrée une partie à partir d'un dict sérialisé.

        Paramètres
        ----------
        data : dict
            Dictionnaire produit par Game.to_dict().
        player_factory : Optional[callable]
            Fonction facultative pour recréer les joueurs à partir des dicts
            sérialisés. Si None, on utilisera Player.from_dict et on perdra
            l'info sur les sous-classes (AIPlayer, etc).
            Signature attendue : player_factory(player_data: dict) -> Player

        Retour
        ------
        Game
            Nouvelle instance de Game.
        """
        from src.player import Player  # import local pour éviter les cycles
        from src.board import Board    # idem

        players_data = data.get("players", [])
        players: List[Player] = []

        for p_data in players_data:
            if player_factory is not None:
                p = player_factory(p_data)
            else:
                p = Player.from_dict(p_data)
            players.append(p)

        game = cls(
            players=players,
            num_rounds=int(data.get("num_rounds", 3)),
            air_per_round=int(data.get("air_per_round", 25)),
        )

        game.round_number = int(data.get("round_number", 1))
        game.air = int(data.get("air", game.air_per_round))
        game.current_player_index = int(data.get("current_player_index", 0))
        game.board = Board.from_dict(data.get("board", {}))

        return game
