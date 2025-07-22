# FlightFollow - Autopilot & Monitoring System

Ce projet gère un pilote automatique d'avion ainsi qu'une interface web interactive pour le suivi en temps réel.

---

## Description générale

- **main.py**  
  C'est le programme principal qui pilote l'autopilote.  
  Il réalise les calculs PID nécessaires pour stabiliser le cap, la vitesse, l'altitude, et d'autres paramètres du vol.

- **map.py**  
  Fournit une carte interactive (Leaflet.js) qui affiche la position actuelle de l'avion, les points dynamiques, ainsi que les lignes et trajectoires.

- **stats.py**  
  Contient les fonctions pour collecter et afficher les statistiques de vol sur la page web avec la carte.

- **oscillo.py**  
  Un oscilloscope logiciel permettant de visualiser en temps réel les actions des PID (Proportionnel, Intégral, Dérivé).

- **pid.py**  
  Implémente les contrôleurs PID utilisés pour ajuster automatiquement le vol selon les objectifs définis.

- **variables.py**  
  Fichier centralisant toutes les variables partagées entre les modules et l'interface web.

- **autopilot.py**  
  Gère la logique spécifique du pilote automatique, s’appuyant sur les calculs PID pour les ajustements.

- **templates/**  
  Contient les fichiers HTML, CSS et les ressources nécessaires pour l'interface web.

---

## Fonctionnement

1. `main.py` orchestre le système, réalise les calculs de pilotage via les PID, et met à jour la position et les données de l’avion.  
2. La carte interactive (via `map.py`) permet de visualiser en temps réel la position, la trajectoire et les points dynamiques.  
3. Les statistiques et oscilloscopes (`stats.py` et `oscillo.py`) fournissent une visualisation claire des paramètres de vol et des actions du PID.  
4. L’interface web est mise à jour périodiquement grâce à une communication AJAX qui interroge le serveur pour récupérer les dernières données.

---

## Technologies utilisées

- Python 3.x  
- Flask / HTTPServer pour le serveur web (selon implémentation)  
- Leaflet.js pour la carte interactive  
- JavaScript pour la mise à jour dynamique de la carte et des données  
- PID Control Theory pour la stabilisation automatique  

---

## Installation & utilisation

1. Cloner le projet  
2. Installer les dépendances (si virtualenv : `pip install -r requirements.txt`)  
3. Lancer `main.py`  
4. Ouvrir `http://localhost:5001` dans un navigateur pour voir la carte et les stats en temps réel  

---

Si tu as des questions ou besoin d’aide pour démarrer, n’hésite pas à me demander !
