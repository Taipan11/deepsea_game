# Deep Sea Adventure – Implémentation en Python (POO)

## 📌 Description

Ce projet consiste en l’implémentation complète du jeu de société **Deep Sea Adventure** en Python, selon une approche en Programmation Orientée Objet (POO).

L’objectif est de concevoir un moteur de jeu modulaire, extensible et testable, respectant les règles officielles du jeu, tout en appliquant de bonnes pratiques d’ingénierie logicielle.

---

## 🎯 Objectifs pédagogiques

- Modéliser un système complexe via la POO
- Concevoir une architecture logicielle modulaire
- Implémenter un moteur de jeu complet
- Développer une intelligence artificielle basique
- Structurer un projet Python proprement
- Produire un code extensible et testable

---

## 🕹️ Fonctionnalités implémentées

- ✅ Moteur de jeu complet (gestion des tours, air, déplacements, scoring)
- ✅ Implémentation fidèle des règles officielles
- ✅ Gestion de 2 à 6 joueurs
- ✅ Affichage textuel (ASCII)
- ✅ Mode joueur vs joueur
- ✅ Mode joueur vs IA
- ✅ Gestion des piles de trésors et logique de pénalité d’oxygène

---

## 🧠 Intelligence Artificielle

Une IA simple a été développée pour simuler un joueur automatique.  
La stratégie repose sur :

- Gestion du risque (niveau d’oxygène restant)
- Décision "stop ou encore"
- Heuristique basée sur la distance au sous-marin
- Priorisation des trésors à forte valeur

---

## 🏗️ Architecture du projet

Le projet est structuré selon une séparation claire des responsabilités :

- `Game` → moteur principal
- `Player` → gestion des joueurs
- `Board` → gestion du plateau
- `Treasure` → gestion des jetons
- `Dice` → logique des dés
- `AIPlayer` → stratégie automatique

Chaque classe est isolée dans son propre module afin d’assurer lisibilité et extensibilité.

---

## 🛠️ Technologies utilisées

- Python 3
- Programmation Orientée Objet
- Gestion d’états
- Logique algorithmique
- Conception modulaire

---

## 🧪 Tests

Des tests unitaires ont été réalisés pour vérifier :

- La validité des déplacements
- La gestion correcte de l’oxygène
- La cohérence du scoring
- Les conditions de fin de manche et de victoire

---

## 🚀 Perspectives d’amélioration

- Interface graphique (Tkinter / Pygame)
- IA plus avancée (Monte Carlo / Minimax)
- Système de sauvegarde / chargement
- Mode multijoueur réseau
- Ajout de logs et visualisation des statistiques

---

## 📚 Règles du jeu

Les règles officielles sont disponibles ici :  
https://regle.escaleajeux.fr/deeps_rg.pdf

---

## 👤 Auteur

Projet réalisé dans le cadre d’un module de Programmation Orientée Objet (Master Data Science).

---

## 💡 Ce que j’ai appris

- Concevoir une architecture orientée objet robuste
- Gérer la complexité d’un système à états multiples
- Structurer un projet Python de manière professionnelle
- Implémenter une logique décisionnelle simple (IA)
