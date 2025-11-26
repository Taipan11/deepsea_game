from src.player import Player

def choose_players_cli():
    def ask_int(prompt, mini, maxi):
        while True:
            try:
                n = int(input(prompt))
                if mini <= n <= maxi:
                    return n
            except ValueError:
                pass
            print(f"Veuillez entrer un nombre entre {mini} et {maxi}.")

    n = ask_int("Combien de joueurs ? (2 à 6) : ", 2, 6)

    players = []
    for i in range(n):
        print(f"\nJoueur {i+1} :")
        name = input("Nom : ")

        type_choice = ask_int("1 = Humain, 2 = IA : ", 1, 2)
        is_ai = (type_choice == 2)

        players.append(Player(name, is_ai=is_ai))

    return players
