# Guide Complet du Projet : Debug, Corrections et Organisation

Ce document a pour but de documenter l'intégralité de la démarche de développement, de débogage et d'organisation du projet Güdlft. Il est conçu pour servir de support lors de la revue de code et de la soutenance.

---

## 1. L'Organisation des Dossiers dans VS Code

Pour travailler efficacement, l'espace de travail a été structuré de manière logique et modulaire. Voici l'arborescence du projet et le rôle de chaque dossier :

- **`server.py`** : C'est le cœur de l'application. Il contient toutes les routes Flask, la logique métier (validation des réservations) et la gestion des sessions.
- **`clubs.json` et `competitions.json`** : Ce sont nos "bases de données" locales. Ils contiennent les données brutes et sont mis à jour (sauvegardés) à chaque réservation.
- **`requirements.txt`** : Liste des dépendances Python (Flask, Pytest, Flake8, Locust).
- **`README.md`** : Le guide d'installation et de lancement du projet.
- **`RAPPORT_DE_DEBUG.md`** : Le document expliquant la méthodologie de résolution des bugs.
- **`GUIDE_COMPLET_DU_PROJET.md`** : Ce fichier (explication globale et organisation).
- **`templates/`** : Ce dossier contient toutes les vues HTML de l'application. Nous utilisons `base.html` comme modèle parent (avec Bootstrap et le menu de navigation), et les autres fichiers (`index.html`, `welcome.html`, `booking.html`, `points.html`) héritent de ce modèle.
- **`static/`** : Contient la feuille de style personnalisée (`style.css`). Cela permet de garder le HTML propre et de séparer le design de la structure.
- **`tests/`** : Le dossier de test est rigoureusement organisé pour faciliter la maintenance :
  - **`unit/`** : Tests des fonctions isolées (règles de validation, formatage des dates, recherches).
  - **`integration/`** : Tests vérifiant que les routes Flask fonctionnent correctement de bout en bout (ex: achat de places).
  - **`functional/`** : Tests simulant un parcours utilisateur complet (ex: cliquer sur un bouton, vérifier l'affichage).
  - **`performance/`** : Contient le script `locustfile.py` pour les tests de charge.
  - **`conftest.py`** : Fichier de configuration de Pytest qui fournit un "client" Flask à tous les tests pour simuler des requêtes web.
- **`rapports/`** : Dossier de sortie pour les rapports de tests de performance (fichiers CSV et HTML générés par Locust).

---

## 2. Comment nous avons trouvé et corrigé les Bugs (Stratégie de Debug)

La méthodologie de débogage a suivi une approche rigoureuse : **Reproduction -> Test -> Correction**.

### A. Les plantages (Erreurs 500)
- **Le crash lors de la recherche (Club/Compétition)** :
  - *Comment on l'a trouvé* : En modifiant l'URL manuellement avec un nom qui n'existe pas.
  - *Cause* : La fonction de recherche renvoyait `None`, et le code essayait d'accéder à ses propriétés (`club['name']`), causant une erreur fatale.
  - *Correction* : Ajout de conditions `if result is None:` dans `server.py` pour rediriger proprement l'utilisateur avec un message d'erreur au lieu de planter.

### B. Les bugs de la Page de Connexion (UX et Sécurité)
- **L'erreur 405 (Method Not Allowed)** :
  - *Comment on l'a trouvé* : En appuyant sur `F5` après s'être connecté.
  - *Cause* : La route `/showSummary` n'acceptait que la méthode `POST`. L'actualisation envoie un `GET`.
  - *Correction* : Modification de la route avec `methods=['GET', 'POST']`. Si `POST`, on connecte ; si `GET`, on recharge la page depuis la session active.
- **Le Logout sans effet et le manque de sécurité** :
  - *Cause* : Aucune session n'était utilisée. N'importe qui pouvait accéder à `/showSummary` sans être connecté.
  - *Correction* : Importation de `session` de Flask. On stocke l'email de l'utilisateur à la connexion, et on utilise `session.clear()` dans la route `/logout`. On vérifie aussi la session dans les autres routes pour bloquer les intrus.

### C. Le contournement des Règles Métier
- **Réservation > 12 places ou surcompétition passée** :
  - *Cause* : Le code initial vérifiait mal les cumuls et ignorait les dates.
  - *Correction* : Création d'une fonction centralisée `validate_booking()`. On y vérifie d'abord la date (`is_competition_over`), puis le cumul avec un dictionnaire `bookings`, puis le stock, puis les points.
- **Saisie invalide (ex: "1,5", "abc")** :
  - *Cause* : L'application plantait ou acceptait des données incohérentes.
  - *Correction* : Création de la fonction `parse_places()` avec un `try/except ValueError` pour n'accepter que des entiers stricts positifs.

### D. La persistance des Données
- **Les points revenaient à zéro après redémarrage** :
  - *Cause* : L'application modifiait les dictionnaires en mémoire vive, mais ne réécrivait pas les fichiers JSON.
  - *Correction* : Création de la fonction `saveData()` qui utilise `json.dump()` pour écrire les nouvelles valeurs dans `clubs.json` et `competitions.json` à chaque achat réussi.

---

## 3. Approche TDD (Test-Driven Development)

Pour garantir que les corrections n'introduisaient pas de nouveaux bugs (régressions), le projet a été développé en suivant les principes du TDD :
- Pour chaque bug, un test a été écrit **avant** de modifier le code.
- Par exemple, avant de coder la limite des 12 places, un test `test_limite_de_12_places_cumulees` a été créé. Il échouait (phase rouge), puis nous avons codé la validation (phase verte).
- Le projet totalise **143 tests** qui couvrent les "Happy Paths" (chemins heureux) et les "Sad Paths" (cas d'erreur : points insuffisants, dates invalides, etc.).

---

## 4. Organisation Git (Workflow)

Le projet respecte les conventions de nommage exigées par le guide de développement :
- **`main`** : Branche de production, toujours stable et testée.
- **`feature/nom`** : Nouvelles fonctionnalités (ex: `feature/filtre-et-badges`).
- **`bug/nom`** : Corrections de bugs.
- **`style/nom`** : Améliorations visuelles (ex: `style/amelioration-visuelle`).
- **`docs/nom`** : Documentation (ex: `docs/rapport-de-debug`).
- **`qa`** : Branche spécifique à la revue de code (ne doit jamais être fusionnée dans `main`).

---

## 5. Les Améliorations Dynamiques (Bonus)

Au-delà du cahier des charges, deux fonctionnalités ont été ajoutées pour rendre l'interface plus vivante :
1. **La barre de recherche en JavaScript** (sur `welcome.html`) : Filtre les cartes de compétitions en temps réel sans recharger la page.
2. **Les badges "Dernières places"** : Un indicateur visuel rouge (géré via Jinja2 dans `welcome.html`) qui s'affiche dès qu'il reste 3 places ou moins dans une compétition.

---

## 6. Synthèse pour la Soutenance

Lors de la démonstration, il sera important de mettre en avant :
- La propreté du code (Flake8 à 0).
- La robustesse de l'application face aux erreurs utilisateur.
- Le passage du modèle "TOUT dans un seul fichier" à une architecture MVC (Modèle-Vue-Contrôleur) avec des templates hérités (Bootstrap).
- La sécurisation des routes via les sessions Flask.