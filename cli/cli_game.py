# cli_game.py
from __future__ import annotations


from typing import List, Dict
# Rendre src importable
import os
import sys

# Ajoute le dossier parent au PYTHONPATH
CLI_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CLI_DIR)  # dossier parent (jeu python/)
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from src.game import Game
from src.player import Player
from src.ai_player import AIPlayer, AIPlayerNormal, AIPlayerCautious, AIPlayerAdventurous


# -------------------------------------------------------
#  Utils ASCII
# -------------------------------------------------------

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def render_board_ascii(game: Game) -> None:
    """
    Affiche le plateau en ASCII.

    Ligne 1 : index des cases
    Ligne 2 : contenu des cases (Space.__str__)
    Ligne 3 : joueurs sur chaque case
    """
    board = game.board
    spaces = [board.get_space(i) for i in range(board.last_index + 1)]

    # Ligne des indices
    idx_line = " ".join(f"{i:2d}" for i in range(len(spaces)))

    # Ligne des cases (utilise Space.__str__)
    space_line = " ".join(f"{str(s):>3}" for s in spaces)

    # Ligne des joueurs
    # On concatène les initiales des joueurs présents sur chaque case
    player_by_pos: Dict[int, List[str]] = {}
    for p in game.players:
        if p.is_on_submarine:
            pos = 0
        else:
            pos = p.position
        player_by_pos.setdefault(pos, []).append(p.name[0].upper())

    player_line_elems = []
    for i in range(len(spaces)):
        letters = "".join(player_by_pos.get(i, []))
        player_line_elems.append(f"{letters:>3}")
    player_line = " ".join(player_line_elems)

    print()
    print("Index : ", idx_line)
    print("Cases : ", space_line)
    print("Joueurs:", player_line)
    print()


def render_players_ascii(game: Game) -> None:
    print("=== Joueurs ===")
    for p in game.players:
        role = "IA" if p.is_ai else "Humain"
        pos_text = "Sous-marin" if p.is_on_submarine else f"Case {p.position}"
        state_parts = []
        if p.is_on_submarine:
            state_parts.append("Sur le sous-marin")
        else:
            state_parts.append("Remonte" if p.going_back else "Descend")
        if p.has_returned:
            state_parts.append("Revenu ✔️")

        carrying = p.carrying
        carrying_count = len(carrying)
        carrying_value = sum(t.value for t in carrying)
        total_score = p.total_score

        print(f"- {p.name} ({role})")
        print(f"  Position : {pos_text}")
        print(f"  État     : {', '.join(state_parts)}")
        print(f"  Trésors  : {carrying_count} portés (valeur {carrying_value}), "
              f"score sécurisé = {total_score}")
    print()


def ask_int(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            v = int(input(prompt).strip())
            if min_val <= v <= max_val:
                return v
        except ValueError:
            pass
        print(f"➡️  Merci d'entrer un nombre entre {min_val} et {max_val}.")


# -------------------------------------------------------
#  Setup ASCII
# -------------------------------------------------------

def setup_players_ascii() -> List[Player]:
    clear_screen()
    print("=== Deep Sea Adventure 🐙 (version ASCII) ===\n")

    n = ask_int("Combien de joueurs ? (2–6) : ", 2, 6)

    players: List[Player] = []

    for i in range(n):
        print(f"\n--- Joueur {i+1} ---")
        name = input("Nom du joueur (laisser vide pour un nom par défaut) : ").strip()
        if not name:
            name = f"Joueur {i+1}"

        is_ai_str = input("Ce joueur est-il une IA ? (o/n) [n] : ").strip().lower()
        is_ai = is_ai_str == "o"

        if not is_ai:
            players.append(Player(name=name))
        else:
            # Choix du type d'IA
            print("Type d'IA :")
            print("  1) Normal")
            print("  2) Prudente")
            print("  3) Aventureuse")
            choice = ask_int("Choix [1–3] (défaut 1) : ", 1, 3)

            if choice == 2:
                players.append(AIPlayerCautious(name=name))
            elif choice == 3:
                players.append(AIPlayerAdventurous(name=name))
            else:
                players.append(AIPlayerNormal(name=name))

    return players


# -------------------------------------------------------
#  Un tour en ASCII
# -------------------------------------------------------

def play_turn_ascii(game: Game) -> None:
    player = game.current_player

    clear_screen()
    print(f"=== Manche {game.round_number}/{game.num_rounds} – Air restant : {game.air} ===")
    render_board_ascii(game)
    render_players_ascii(game)
    print(f">>> Au tour de {player.name} "
          f"({'IA' if player.is_ai else 'Humain'})")

    # --- Choix de direction ---
    if isinstance(player, AIPlayer):
        go_back = player.choose_direction(game.air)
        print(f"[IA] {player.name} choisit de "
              f"{'remonter' if go_back else 'descendre'}")
    else:
        # humain
        if player.going_back:
            go_back = True
            print("Tu es déjà en remontée, tu continues à remonter.")
        elif player.is_on_submarine and not player.has_returned:
            go_back = False
            print("Début de manche : tu dois descendre.")
        else:
            # choix libre
            while True:
                direction = input("Choisir la direction (D=descendre, R=remonter) [D] : ")\
                    .strip().lower()
                if direction in ("", "d"):
                    go_back = False
                    break
                if direction in ("r", "remonter"):
                    go_back = True
                    break
                print("Merci de répondre 'D' ou 'R'.")

    # --- Phase de déplacement ---
    result = game.begin_turn(player, going_back=go_back)
    print(f"\n🎲 {player.name} a lancé le dé : {result.dice_roll}")
    print(f"{player.name} se déplace sur la case {player.position}"
          f"{' (sous-marin)' if player.is_on_submarine else ''}")

    # --- Action sur la case ---
    if result.can_act_on_space:
        space = game.board.get_space(player.position)

        if isinstance(player, AIPlayer):
            action_code = player.choose_action(space, game.air)
            print(f"[IA] {player.name} choisit l'action {action_code}")
        else:
            # Joueur humain
            # Actions possibles :
            # A = ne rien faire
            # B = ramasser un trésor (si dispo)
            # C = poser un trésor (si porte quelque chose et case vide)
            while True:
                print("\nActions possibles :")
                print("  A) Ne rien faire")
                print("  B) Ramasser un trésor (si disponible)")
                print("  C) Poser un trésor (si tu en portes et que la case est libre)")
                choice = input("Choix [A/B/C] (défaut A) : ").strip().upper()

                if choice == "":
                    choice = "A"

                if choice not in ("A", "B", "C"):
                    print("Merci de choisir A, B ou C.")
                    continue

                # règles simples côté UI, la vraie validation est dans Game/Space
                if choice == "B" and not space.has_ruin:
                    print("❌ Il n'y a aucun trésor sur cette case.")
                    continue

                if choice == "C":
                    if not player.carrying:
                        print("❌ Tu ne portes aucun trésor.")
                        continue
                    if space.has_ruin:
                        print("❌ Il y a déjà des ruines sur cette case, "
                              "impossible de poser un trésor ici.")
                        continue

                action_code = choice
                break

        tile = game.perform_action(player, action_code)

        if not isinstance(player, AIPlayer) and tile:
            if action_code == "B":
                print(f"✅ Tu as ramassé un trésor (valeur {tile.value}).")
            elif action_code == "C":
                print("✅ Tu as posé un trésor sur cette case.")

    # --- Fin de manche ? ---
    if game.is_round_over():
        print("\n=== Fin de manche ===")
        game.end_round()
        scores = game.get_scores()
        for name, score in scores.items():
            print(f"- {name} : {score} points sécurisés")

        input("\nAppuie sur Entrée pour passer à la manche suivante...")
        game.next_round()
    else:
        game.advance_to_next_player()

    input("\n(Entrée pour continuer...)")


# -------------------------------------------------------
#  Boucle principale
# -------------------------------------------------------

def main():
    players = setup_players_ascii()
    game = Game(players, num_rounds=3, air_per_round=25)

    while not game.is_game_over():
        play_turn_ascii(game)

    # Fin de partie
    clear_screen()
    print("=== Fin de la partie 🏁 ===")
    final_scores = game.get_scores()
    winners = game.get_winners()

    print("\nScores finaux :")
    for p, score in final_scores.items():
        print(f" - {p}: {score}")

    if len(winners) == 1:
        print(f"\n🏆 Vainqueur : {winners[0]} !")
    else:
        names = ", ".join(str(p) for p in winners)
        print(f"\n🤝 Égalité entre : {names}")

    print("\nMerci d'avoir joué à Deep Sea Adventure (version ASCII) 🐙")


if __name__ == "__main__":
    main()
