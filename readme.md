Deepsea Game — adaptation de Deep Sea Adventure en Python (orienté objet)
🎯 But du jeu
Dans Deep Sea Adventure, chaque joueur incarne un plongeur-explorateur en quête de trésors enfouis sous la mer. Tous les joueurs partagent un même sous-marin et, surtout, une unique réserve d’oxygène.
Plus vous plongez profondément, plus les trésors sont précieux — mais plus votre progression est ralentie, et plus l’air consommé pour remonter augmente. Si l’oxygène vient à manquer avant que vous reveniez au sous-marin, vous perdez tous vos trésors.
Le but est de rapporter le plus de trésors possible après trois plongées. :contentReference[oaicite:2]{index=2}

📦 Contenu / Matériel simulé (dans l’adaptation)
2 dés spéciaux (valeurs : 1, 2 ou 3) — simulent les lancers de dés pour la plongée. :contentReference[oaicite:3]{index=3}
Plusieurs “pions plongeurs” (un par joueur)
Une “piste d’air / oxygène” partagée (réserve d’air du sous-marin)
Une “pile” de jetons trésor / ruines, de différents niveaux (valeurs) — plus on descend, plus les trésors sont “profonds / précieux”. :contentReference[oaicite:4]{index=4}
🧑‍💻 Principe du jeu & déroulement d’une partie
Le jeu se joue de 2 à 6 joueurs, idéalement 3–6. :contentReference[oaicite:5]{index=5}
Une partie dure environ 30 minutes (sur 3 “plongées” / manches). :contentReference[oaicite:6]{index=6}
À chaque plongée :
Tous les plongeurs commencent dans le sous-marin, oxygène au maximum.
À tour de rôle (dans l’ordre), chaque joueur peut décider de descendre — il jette les dés, se déplace d’autant de cases sous l’eau — ou, s’il transporte des trésors, décider de remonter vers le sous-marin.
Avant chaque déplacement, on décrémente la réserve d’air en fonction du nombre de trésors que le joueur porte (donc plus un joueur porte de trésors, plus il consomme d’oxygène pour respirer). Si l’air atteint 0, la plongée se termine, et tous les joueurs encore sous l’eau perdent leurs trésors. :contentReference[oaicite:7]{index=7}
Chaque joueur ne peut remonter qu’une seule fois par plongée, et seulement s’il a au moins un trésor. :contentReference[oaicite:8]{index=8}
La plongée se termine quand tous les joueurs sont remontés ou que l’air vient à manquer.
Après 3 plongées, on compare les trésors rapportés : le joueur ayant la valeur de trésors la plus élevée l’emporte. En cas d’égalité, celui avec le plus de trésors “haut niveau” gagne. :contentReference[oaicite:9]{index=9}
🧩 À propos de cette implémentation
Ce projet constitue une adaptation en Python orienté-objet de Deep Sea Adventure. Le but est de:

Reproduire la mécanique du jeu original (dés, plongée, trésors, oxygène, remontée, scoring),
Proposer une architecture modulaire — logique du jeu, interface en ligne de commande (CLI), interface graphique (GUI), éventuellement des tests.
Permettre d’ajouter facilement de nouvelles fonctionnalités ou variantes via l’extensibilité du code orienté objet.
🚀 Comment lancer le jeu