# game.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum, auto

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

class GamePhase(Enum):
    SETUP = auto()
    PLAYING = auto()
    ROUND_END = auto()
    GAME_END = auto()


@dataclass
class PlayerState:
    index: int
    name: str
    is_ai: bool
    position: int
    is_on_submarine: bool
    going_back: bool
    has_returned: bool
    carrying_count: int
    carrying_value: int
    total_score: int

@dataclass
class SpaceState:
    index: int
    depth: int           # ou niveau, si tu as cette info
    has_ruin: bool       # True si au moins 1 tuile (initiale ou reposée)
    ruin_count: int
    is_submarine: bool
    is_removed: bool     # si plus tard tu “retires” des cases

@dataclass
class GameState:
    phase: GamePhase
    round_number: int
    num_rounds: int
    air: int
    air_per_round: int
    current_player_index: int
    is_last_round: bool
    is_round_over: bool
    is_game_over: bool
    board: Dict[str, Any]
    spaces: List[SpaceState] # NEW
    players: List[PlayerState]
    last_turn: Optional[TurnResult] = None


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
        self.players = players
        self.num_rounds = num_rounds
        self.air_per_round = air_per_round
        self.board = board if board is not None else Board.create_default()
        self.dice = dice if dice is not None else Dice()

        self.round_number: int = 1
        self.air: int = air_per_round
        self.current_player_index: int = 0

        # Nouveau : phase + dernier tour pour le state
        self._phase: GamePhase = GamePhase.SETUP
        self._last_turn: Optional[TurnResult] = None

        self._reset_all_players_for_new_game()
        # Après init, on est prêt à jouer
        self._phase = GamePhase.PLAYING
        # Suivre quelles cases ont été vidées pendant la manche
        self._emptied_spaces_this_round: set[int] = set()
        # Suivre l'ordre dans lequel les joueurs reviennent au sous-marin
        self._return_log: list[int] = []          # indices de joueurs dans l'ordre de retour
        self._next_round_start_index: int = 0     # qui commencera la prochaine manche




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
        Prépare une nouvelle manche :

        - On NE recrée PAS le board (il a été compressé en fin de manche).
        - On remet juste l'air et les joueurs à zéro pour la nouvelle plongée.
        - Le joueur qui commence est déterminé par la règle de fin de manche.
        """
        self.air = self.air_per_round
        self._emptied_spaces_this_round.clear()
        self._return_log.clear()          # on réinitialise l'historique de retour

        for p in self.players:
            p.reset_for_new_round()

        # 👉 Qui commence la nouvelle manche ?
        self.current_player_index = self._next_round_start_index

        self._phase = GamePhase.PLAYING


     
    def _register_player_return(self, player: Player) -> None:
        """
        Enregistre qu'un joueur vient de revenir au sous-marin
        (pour déterminer qui commencera la prochaine manche).
        """
        idx = self.players.index(player)
        if idx not in self._return_log:
            self._return_log.append(idx)

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
        Déplace le joueur en appliquant les règles Deep Sea Adventure :

        - moves = résultat des dés - nombre de trésors portés (déjà calculé dans begin_turn)
        - si le joueur avance vers un jeton de ruine sur lequel se trouve déjà
        un autre explorateur, on passe sur ce jeton sans le compter dans moves.
        - en descente, on ne dépasse pas le dernier jeton du plateau.
        - en remontée, si on atteint ou dépasse le sous-marin, le joueur revient.
        """
        if moves <= 0:
            return False

        direction = -1 if player.going_back else 1
        steps_left = moves
        reached_submarine = False

        while steps_left > 0:
            next_pos = player.position + direction

            # --- Descente : ne pas dépasser le plateau ---
            if not player.going_back and next_pos > self.board.last_index:
                # On s'arrête simplement au dernier jeton
                player.move_to(self.board.last_index)
                break

            # --- Remontée : retour au sous-marin ---
            if player.going_back and next_pos <= self.board.submarine_index:
                player.mark_as_returned()
                self._register_player_return(player)   # NEW
                reached_submarine = True
                break


            # Regarder la case vers laquelle on va
            space = self.board.get_space(next_pos)

            # On se déplace physiquement sur la case
            player.move_to(next_pos)

            # On regarde si cette case doit être "sautée" ou pas
            if not self._should_skip_space(player, next_pos, space):
                steps_left -= 1


        # Cas particulier : si on termine exactement au sous-marin en remontée
        if player.going_back and player.is_on_submarine and not reached_submarine:
            player.mark_as_returned()
            self._register_player_return(player)   # NEW
            reached_submarine = True


        return reached_submarine

    def perform_action(self, player: Player, action_code: str) -> Optional[RuinTile]:
        if player.is_on_submarine:
            return None

        space: Space = self.board.get_space(player.position)
        code = action_code.upper().strip()

        if code == "A":
            return None

        if code == "B":
            if not space.has_ruin:
                return None

            #  nouvelle méthode : récupère un seul RuinTile combiné
            tile = space.pop_all_ruins_as_single()
            if tile is not None:
                player.take_ruin(tile)

                # Si la case n'a plus de ruine, on la marque comme "vidée" pour fin de manche
                if not space.has_ruin:
                    self._emptied_spaces_this_round.add(player.position)

            return tile
        
        if code == "C":
        # Poser un trésor pour alléger sa charge

            # 1. Impossible si la case contient déjà des ruines
            if space.has_ruin:
                return None

            # 2. Impossible si le joueur ne porte rien
            tile = player.drop_one_ruin()
            if tile is None:
                return None

            # 3. On pose la tuile sur cette case
            space.push_ruin(tile)

            # 4. Cette case n'est plus "vidée" pour la fin de manche
            self._emptied_spaces_this_round.discard(player.position)
            return tile

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

        - Si la manche se termine par manque d'air (air <= 0) :
            * les joueurs au sous-marin sécurisent leurs trésors,
            * les autres jettent tous leurs trésors au fond,
            empilés par lots de 3, en commençant par le joueur
            le plus éloigné du sous-marin.
        - Sinon (tout le monde est revenu avec encore de l'air) :
            * les joueurs au sous-marin sécurisent leurs trésors,
            * les autres perdent leurs trésors (version simplifiée).
        - Dans tous les cas, on compresse ensuite le chemin.
        """
        exhausted_by_air = self.air <= 0

        # Liste des tuiles qui tombent au fond (si air épuisé)
        dropped_to_bottom: list[RuinTile] = []

        if exhausted_by_air:
            # On traite les joueurs du plus éloigné au plus proche du sous-marin
            players_ordered = sorted(
                self.players,
                key=lambda p: p.position,
                reverse=True
            )

            for p in players_ordered:
                if p.is_on_submarine:
                    # Il a réussi à rentrer malgré l'air à 0 → il sécurise
                    p.secure_carried_treasures()
                    continue

                # Joueur resté en mer : il jette tous ses trésors au fond
                while p.carrying:
                    tile = p.drop_one_ruin()
                    if tile is not None:
                        dropped_to_bottom.append(tile)
        else:
            # Fin de manche "normale" : comportement précédent
            for p in self.players:
                if p.is_on_submarine:
                    p.secure_carried_treasures()
                else:
                    p.drop_all_carrying()

        # Si l'air a été épuisé et qu'il y a des trésors à jeter,
        # on les ajoute au fond par piles de 3.
        if exhausted_by_air and dropped_to_bottom:
            self.board.drop_tiles_to_bottom(dropped_to_bottom, stack_size=3)

        # ⚠️ AVANT de reset pour la nouvelle manche, on décide qui commencera
        self._next_round_start_index = self._compute_next_round_start_index()
        
        # Compression du chemin : on retire les cases vides
        self.board.compress_path()
        self._phase = GamePhase.ROUND_END


    def next_round(self) -> None:
        self.round_number += 1
        if self.is_game_over():
            self._phase = GamePhase.GAME_END
        else:
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
    #  State global lisible par l’UI
    # =========================

    def get_state(self) -> GameState:
        players_state: List[PlayerState] = []
        for idx, p in enumerate(self.players):
            carrying_value = sum(tile.value for tile in p.carrying)
            players_state.append(
                PlayerState(
                    index=idx,
                    name=p.name,
                    is_ai=p.is_ai,
                    position=p.position,
                    is_on_submarine=p.is_on_submarine,
                    going_back=p.going_back,
                    has_returned=p.has_returned,
                    carrying_count=len(p.carrying),
                    carrying_value=carrying_value,
                    total_score=p.total_score,
                )
            )

        # Vue des cases
        spaces_state: List[SpaceState] = []
        for idx, space in enumerate(self.board.spaces):
            spaces_state.append(
                SpaceState(
                    index=idx,
                    depth=getattr(space, "depth", 0),
                    has_ruin=space.has_ruin,
                    ruin_count=space.ruin_count if hasattr(space, "ruin_count") else (1 if space.has_ruin else 0),
                    is_submarine=(idx == self.board.submarine_index),
                    is_removed=getattr(space, "is_removed", False),
                )
            )

        return GameState(
            phase=self._phase,
            round_number=self.round_number,
            num_rounds=self.num_rounds,
            air=self.air,
            air_per_round=self.air_per_round,
            current_player_index=self.current_player_index,
            is_last_round=self.is_last_round,
            is_round_over=self.is_round_over(),
            is_game_over=self.is_game_over(),
            board=self.board.to_dict(),
            # spaces=spaces_state,          # 👈 NEW
            players=players_state,
            last_turn=self._last_turn,
        )

    def _compute_next_round_start_index(self) -> int:
        """
        Détermine quel joueur commencera la prochaine manche selon la règle :

        - Si tous les joueurs sont au sous-marin :
            -> dernier à être rentré (via _return_log).
        - Si aucun n'est au sous-marin :
            -> joueur le plus éloigné du sous-marin (position max).
        - Si certains sont au sous-marin et d'autres non :
            -> parmi ceux qui ne sont pas revenus, celui le plus loin.
        """
        on_sub = [(i, p) for i, p in enumerate(self.players) if p.is_on_submarine]
        not_on_sub = [(i, p) for i, p in enumerate(self.players) if not p.is_on_submarine]

        if on_sub and not not_on_sub:
            # Cas 1 : tout le monde est revenu -> dernier à être rentré
            for idx in reversed(self._return_log):
                if 0 <= idx < len(self.players):
                    return idx
            # fallback (au cas où) :
            return 0

        if not on_sub and not_on_sub:
            # Cas 2 : personne n'est revenu -> plus loin du sous-marin
            farthest_i, _ = max(not_on_sub, key=lambda t: t[1].position)
            return farthest_i

        if on_sub and not_on_sub:
            # Cas 3 : certains revenus, d'autres non -> parmi ceux non revenus, le plus loin
            farthest_i, _ = max(not_on_sub, key=lambda t: t[1].position)
            return farthest_i

        # Cas bizarre / fallback
        return 0

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
    
    
    def _is_space_occupied_by_other(self, player: Player, position: int) -> bool:
        return any(
            (other is not player) and (other.position == position)
            for other in self.players
        )

    def _should_skip_space(self, player: Player, position: int, space: Space) -> bool:
        """
        Décide si cette case doit être "sautée" sans consommer de pas.

        Idée : c’est ici qu’on branche les règles évolutives :
        - case occupée par un autre joueur
        - case marquée comme retirée
        - future règle spéciale (piège, courant marin, etc.)
        """
        occupied_by_other = self._is_space_occupied_by_other(player, position)

        # Règle 1 : sauter toute case occupée par un autre joueur
        if occupied_by_other:
            return True

        # Règle 2 (exemple futur) : si on marque certaines cases comme "retirées"
        # if getattr(space, "is_removed", False):
        #     return True

        # Règle 3 : on pourrait garder un comportement spécial sur les ruines
        # (par exemple : sauter seulement si c’est une ruine occupée, comme la règle originale)
        # if occupied_by_other and space.has_ruin:
        #     return True

        return False


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