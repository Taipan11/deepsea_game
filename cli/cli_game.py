# cli/cli_game.py

import os
import sys

# On ajoute le dossier racine du projet au PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.game import Game
from src.player import Player
from src.ai_player import AIPlayer
from src.player_setup import choose_players_cli


def main():
    # # 1 humain + 1 IA par exemple
    # players = [
    #     Player(name="Mehdi"),
    #     AIPlayer(name="Bot"),
    # ]

    players = choose_players_cli()    # <-- voici où le mettre
    game = Game(players, num_rounds=3, air_per_round=25)

    # Boucle de jeu simple ASCII
    while not game.is_game_over():
        print(f"\n=== Manche {game.round_number} - Air: {game.air} ===")
        print("Plateau :", game.get_board_ascii())
        for line in game.get_players_status_ascii():
            print(" ", line)

        while not game.is_round_over():
            player = game.current_player

            # --- choix de direction ---
            if player.is_ai:
                # player est une instance de AIPlayer
                # En fait, cette ligne est inutile et peut causer UnboundLocalError,
                # donc ne l'ajoute pas, garde juste le import tout en haut.
                pass

            if player.is_ai:
                # IA
                assert isinstance(player, AIPlayer)
                go_back = player.choose_direction(game.air)
                print(f"\nTour de {player.name} (IA) - remonte ? {go_back}")
            else:
                # Humain
                print(f"\nTour de {player.name} (humain)")
                choice = input("Voulez-vous remonter ? (o/n) : ").strip().lower()
                go_back = (choice == "o")

            # --- phase de déplacement ---
            result = game.begin_turn(player, going_back=go_back)
            print(f"  Dés: {result.dice_roll}, déplacement: {result.move_distance}")
            print("  Plateau :", game.get_board_ascii())

            # --- action éventuelle ---
            if result.can_act_on_space:
                if player.is_ai:
                    assert isinstance(player, AIPlayer)
                    space = game.board.get_space(player.position)
                    action = player.choose_action(space, game.air)
                    print(f"  IA choisit l'action {action}")
                else:
                    print("  Actions : A = ne rien faire, B = ramasser un trésor")
                    action = input("  Choix d'action (A/B) : ").strip().upper() or "A"

                tile = game.perform_action(player, action)
                if tile:
                    print(f"  {player.name} ramasse un trésor de valeur {tile.value}")

            # Joueur suivant
            game.advance_to_next_player()

        # Fin de manche
        game.end_round()
        print("\nFin de manche. Scores :")
        for name, score in game.get_scores().items():
            print(f"  {name}: {score}")

        game.next_round()

    # print("\n=== Fin de partie ===")
    # for name, score in game.get_scores().items():
    #     print(f"{name}: {score}")
    # winners = game.get_winners()
    # if len(winners) == 1:
    #     print("Vainqueur :", winners[0].name)
    # else:
    #     print("Égalité entre :", ", ".join(p.name for p in winners))

    print("\n=== FIN DE PARTIE ===")

    scores = game.get_final_scores()
    for p, s in scores.items():
        print(f"{p.name}: {s}")

    winners = game.get_winners()
    if len(winners) == 1:
        print(f"\n🏆 VAINQUEUR : {winners[0].name} !!")
    else:
        print("\n🤝 ÉGALITÉ ENTRE :", ", ".join(p.name for p in winners))



if __name__ == "__main__":
    main()
