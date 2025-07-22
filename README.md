# AeroSuite – AeroCore

AeroSuite est une suite modulaire conçue pour gérer le vol d’un aéronef en connectant et contrôlant différents périphériques embarqués.  
AeroCore est le cœur logiciel du pilote automatique, responsable du calcul et de la stabilisation automatique du vol.

---

## Description générale

AeroCore orchestre les fonctions critiques du pilote automatique, en réalisant les calculs PID essentiels pour stabiliser le cap, l’altitude, la vitesse, et la trajectoire.  
Ce composant est connecté à une interface web qui permet de visualiser la position de l’avion, ses statistiques de vol et le comportement des PID en temps réel.

---

## Composants clés

- **main.py**  
  Programme principal qui gère la logique du pilote automatique et exécute les calculs PID pour la stabilisation du vol.

- **map.py**  
  Génère une carte interactive affichant la position de l’avion en temps réel avec Leaflet.

- **stats.py**  
  Affiche les statistiques de vol et de contrôle sur la page web, fournissant un suivi clair des données en cours.

- **oscillo.py**  
  Oscilloscope logiciel qui montre en temps réel l’activité des PID, permettant une analyse fine de leurs réactions.

- **pid.py**  
  Contient les variables PID et la logique de contrôle utilisées par l’interface web connectée à main.py.

---

## Fonctionnalités

- Calcul en temps réel des paramètres de vol pour une stabilisation automatique précise.  
- Visualisation dynamique de la position de l’avion sur une carte interactive et mise à jour continue.  
- Monitoring des PID via un oscilloscope pour un diagnostic en temps réel.  
- Interface web intuitive pour la supervision et le contrôle à distance.

---

## Installation et utilisation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/FranciumDigital/auto_pilot.git

    Installer les dépendances (exemple avec pip) :

pip install -r requirements.txt

Lancer le programme principal :

    python main.py

    Accéder à l’interface web via http://localhost:5001 pour visualiser la carte, les stats, et l’oscilloscope.

Structure du projet

AeroSuite/
├── main.py          # Programme pilote auto principal
├── map.py           # Carte interactive avec Leaflet
├── stats.py         # Statistiques affichées dans l’interface web
├── oscillo.py       # Oscilloscope logiciel pour PID
├── pid.py           # Logique et variables PID
├── templates/       # Fichiers HTML et ressources web
└── ...

Remarques

    Ce composant est l’un des modules de la suite AeroSuite, qui vise à fournir une gestion complète et connectée du vol, incluant la navigation, le pilotage, et l’interfaçage avec divers périphériques embarqués.

    AeroCore est optimisé pour des mises à jour en temps réel et une interface utilisateur claire.

Licence

À définir (exemple MIT, GPL, etc.)
Contact

Pour toute question ou contribution, merci de contacter FranciumDigital via GitHub.
