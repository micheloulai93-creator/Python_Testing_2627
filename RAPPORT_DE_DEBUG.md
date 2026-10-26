# Rapport de Debug et d'Organisation

Ce document explique la méthodologie employée pour identifier, corriger et organiser les bugs du projet Güdlft, ainsi que l'organisation de l'environnement de travail (VS Code) et du dépôt Git.

## 1. Comment j'ai trouvé les bugs (Stratégie de Debug)

Pour identifier les anomalies, j'ai suivi une approche structurée plutôt que de me lancer tête baissée dans le code :

1. **Analyse des rapports QA et des spécifications** : J'ai commencé par lire le fichier `Intro` et les spécifications fonctionnelles pour lister tous les bogues signalés (les 11 bugs de la phase 1).
2. **Reproduction des bugs (Tests Manuels)** : J'ai lancé l'application (`flask run`) et j'ai essayé de reproduire chaque scénario sur mon navigateur :
   - J'ai essayé de réserver plus de 12 places.
   - J'ai essayé de réserver une compétition déjà passée.
   - J'ai testé le bouton "Déconnexion" et actualisé la page.
3. **Analyse des traces d'erreurs (Logs)** : Quand l'application plantait (erreur 500), je regardais directement le terminal qui exécutait Flask. Les messages d'erreur Python (les "Tracebacks") m'indiquaient exactement la ligne du fichier `server.py` qui posait problème (par exemple, une erreur d'index ou un `NoneType`).
4. **Approche TDD (Test-Driven Development)** : Pour chaque bug, j'ai écrit un test dans le dossier `tests/` qui échouait, avant même de corriger le code. Cela m'a permis de m'assurer que le bug était bien reproduit de manière automatisée.

## 2. Comment j'ai corrigé les bugs (Méthodologie)

Pour chaque bug, j'ai suivi une règle stricte : **une branche Git par bug, et on ne touche pas à `main` tant que les tests ne passent pas.**

Voici la démarche type :
1. **Création d'une branche** : Par exemple, `git checkout -b bug/limite-12-places`.
2. **Correction du code** : J'ai centralisé les règles métier dans une fonction dédiée (`validate_booking`). Plutôt que d'avoir des conditions `if` éparpillées partout dans les routes Flask, j'ai fait en sorte que chaque validation (points, stock, date, limite) retourne un message d'erreur clair.
3. **Gestion des erreurs (Sad Paths)** : J'ai utilisé `flash()` pour afficher les messages d'erreur de manière élégante à l'utilisateur, sans faire planter le serveur.
4. **Validation** : Je lançais `python -m pytest -q` pour vérifier que mes 143 tests passaient au vert, et `flake8 --count` pour m'assurer que le code restait propre.

**Exemples de correctifs majeurs :**
- **Le crash de l'application** : La recherche d'un club ou d'une compétition inexistante renvoyait `None`, et le code essayait d'accéder à des propriétés dessus (`None['name']`), causant une Erreur 500. J'ai ajouté des vérifications `if foundClub is None:` pour rediriger proprement l'utilisateur.
- **Le bouton Logout** : Le logout ne faisait rien car il n'y avait pas de gestion de session. J'ai importé `session` de Flask, l'ai initialisé à la connexion, et j'ai ajouté `session.clear()` dans la route `/logout`.
- **L'erreur 405 à l'actualisation** : La route `/showSummary` n'acceptait que la méthode POST. En actualisant, le navigateur fait un GET. J'ai modifié la route pour accepter `methods=['GET', 'POST']` et j'ai géré les deux cas.
- **La non-sauvegarde JSON** : L'application modifiait les données en mémoire vive, mais ne les enregistrait jamais dans `clubs.json` et `competitions.json`. J'ai créé une fonction `saveData()` qui réécrit les fichiers JSON à chaque réservation validée.

## 3. Organisation de GitHub (Git Flow)

Le projet respecte scrupuleusement les conventions de nommage du guide de développement :

- **`main`** : C'est la branche de production. Elle est stable et contient toujours la version finale et testée de l'application.
- **`feature/...`** : Branches dédiées aux nouvelles fonctionnalités (ex: `feature/filtre-et-badges`, `feature/test-performance-locust`).
- **`bug/...`** : Branches dédiées aux corrections de bugs.
- **`style/...`** : Branches pour les améliorations visuelles ou le nettoyage de code (ex: `style/amelioration-visuelle`).
- **`docs/...`** : Branches pour la documentation (ex: `docs/readme-complet`).
- **`qa`** : Branche spéciale, créée à la toute fin. Elle est identique à `main` mais ne doit **jamais** être fusionnée. Elle sert uniquement à l'évaluateur pour faire sa revue de code.

**Workflow typique :**
1. `git checkout -b feature/ma-nouvelle-idee` (depuis `main`).
2. Coder, tester (`pytest`).
3. `git add .` et `git commit -m "feat: description"`.
4. `git push`.
5. `git checkout main`, `git merge feature/ma-nouvelle-idee`, puis `git push`.

## 4. Organisation de VS Code pour ce projet

Pour travailler efficacement et débugger sereinement, j'ai configuré mon espace de travail VS Code de la manière suivante :

1. **Le Terminal Intégré** : Je l'utilise en permanence en bas de l'écran. Il me permet de lancer le serveur (`flask run`), de lancer les tests (`pytest`) et de faire mes commandes Git sans quitter l'éditeur.
2. **L'Explorateur de Fichiers (à gauche)** : J'ai structuré les dossiers pour séparer la logique Flask (`server.py`), les données (`clubs.json`, `competitions.json`), les vues (`templates/`) et les tests (`tests/`). Cela me permet de naviguer rapidement.
3. **Les Fichiers Ouverts (Onglets)** : Lors du débogage, j'avais souvent 3 onglets ouverts en permanence :
   - `server.py` (pour corriger la logique).
   - Le fichier de test correspondant (ex: `test_regles_reservation.py` pour vérifier mes corrections).
   - Le template HTML concerné (pour vérifier l'affichage des erreurs avec `flash()`).
4. **Les Extensions recommandées** :
   - **Python & Pylance** : Pour l'autocomplétion et la détection d'erreurs de syntaxe en temps réel.
   - **Flake8** : Pour souligner en rouge/jaune les problèmes de style (espaces, lignes trop longues) directement dans l'éditeur, ce qui m'évitait de lancer la commande terminal à chaque fois.
   - **GitLens** : Pour voir directement dans l'éditeur qui a modifié quelle ligne de code et quand.
5. **La Palette de Commandes (`Ctrl+Shift+P`)** : Très utile pour formater le document ou lancer des tâches spécifiques.

---
*Ce rapport a été rédigé dans le cadre de la préparation à la revue de code finale.*