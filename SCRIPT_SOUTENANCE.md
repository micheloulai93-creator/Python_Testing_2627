# Dossier de Soutenance et Documentation Technique

Bienvenue dans le dossier de référence du projet Güdlft. Ce document centralise l'explication de notre méthodologie de debug, l'organisation de notre espace de travail et les scripts pour la démonstration finale.

---

## 1. Organisation du Projet et de VS Code

Pour travailler efficacement, l'espace de travail a été structuré de manière logique et modulaire :

- **`server.py`** : Le cœur de l'application (routes Flask, logique métier, sessions).
- **`clubs.json` et `competitions.json`** : La "base de données" locale, mise à jour à chaque réservation.
- **`requirements.txt`** : Dépendances (Flask, Pytest, Flake8, Locust).
- **`README.md`** : Guide d'installation.
- **`templates/`** : Vues HTML héritant de `base.html` (intégration de Bootstrap).
- **`static/`** : Feuille de style personnalisée (`style.css`).
- **`tests/`** : Organisation stricte des tests :
  - `unit/` : Tests des fonctions isolées (règles, dates).
  - `integration/` : Tests des routes Flask.
  - `functional/` : Tests du parcours utilisateur complet.
  - `performance/` : Script Locust.
  - `conftest.py` : Configuration des "faux navigateurs" pour Pytest.
- **`rapports/`** : Sortie des rapports Locust.

---

## 2. Démarche de Debug (Comment on a trouvé et corrigé les bugs)

Nous avons suivi une approche **TDD (Test-Driven Development)** et méthodique : Reproduction -> Test -> Correction.

### A. Plantages (Erreurs 500)
- **Crash sur recherche inexistante** :
  - *Cause* : La fonction de recherche renvoyait `None`, et le code accédait à ses propriétés.
  - *Correction* : Ajout de conditions `if club is None:` pour rediriger proprement l'utilisateur.

### B. Bugs de la Page de Connexion
- **Erreur 405 à l'actualisation** :
  - *Cause* : La route `/showSummary` n'acceptait que `POST`.
  - *Correction* : Modification avec `methods=['GET', 'POST']`.
- **Logout sans effet et faille de sécurité** :
  - *Cause* : Aucune session utilisée.
  - *Correction* : Utilisation de `session` de Flask (`session['email']` à la connexion, `session.clear()` pour le logout).

### C. Règles Métier
- **Réservation > 12 places ou compétition passée** :
  - *Correction* : Création de la fonction `validate_booking()` qui vérifie l'ordre de priorité (date, cumul, stock, points).
- **Saisies invalides** :
  - *Correction* : Fonction `parse_places()` avec `try/except` pour n'accepter que des entiers positifs.

### D. Persistance des Données
- **Points revenant à zéro au redémarrage** :
  - *Correction* : Création de `saveData()` qui réécrit dans `clubs.json` et `competitions.json` via `json.dump()`.

---

## 3. Rôle des Outils (Flask et Pytest)

- **Flask** : C'est le chef d'orchestre. Il gère les routes (URL), fait le lien avec le HTML (Jinja2), gère les sessions (connexion) et les messages flash (erreurs/succès).
- **Pytest** : C'est le garde-fou. Il simule un navigateur (`client` dans `conftest.py`) pour envoyer de fausses requêtes à Flask. Il permet de vérifier automatiquement que les règles métier fonctionnent et qu'on n'a rien cassé (non-régression).

---

## 4. Guide de Test Manuel (Checklist QA)

*À exécuter après avoir lancé `flask run`.*

### Connexion et Navigation
- [ ] **Connexion réussie** : `john@simplylift.co` -> Accès au tableau de bord.
- [ ] **Connexion échouée** : `inconnu@test.com` -> Message d'erreur et retour à l'accueil.
- [ ] **Actualisation (F5)** : Connecté, actualiser la page -> Pas d'erreur 405.
- [ ] **Déconnexion** : Cliquer sur "Déconnexion" -> Retour accueil, accès `/showSummary` bloqué.
- [ ] **Tableau public** : Aller sur `/points` sans être connecté -> Le tableau s'affiche.

### Réservation et Règles Métier
- [ ] **Réservation valide** : Acheter 2 places -> Message vert, points déduits.
- [ ] **Limite de 12 places** : Essayer de réserver 13 places -> Message d'erreur.
- [ ] **Points insuffisants** : `admin@irontemple.com` (4 pts) réserve 5 places -> Message d'erreur.
- [ ] **Compétition passée** : Essayer de réserver "Fall Classic" -> Bouton masqué ou erreur.
- [ ] **Compétition complète** : Essayer "Sold Out Cup" -> Bouton masqué ou erreur.
- [ ] **Saisie invalide** : Taper `abc` dans le champ nombre -> Message d'erreur.

### Vérifications Techniques (Terminal)
- [ ] `python -m pytest -q` -> **143 passed**.
- [ ] `flake8 --count` -> **0**.
- [ ] Vérifier que `clubs.json` et `competitions.json` sont modifiés après un achat.

---

## 5. Script de Soutenance (Démonstration en direct)

Voici le déroulé exact à montrer au jury :

### Phase 1 : Démonstration Visuelle
1. Lancer le serveur : `$env:FLASK_APP="server.py"` puis `flask run`.
2. Se connecter et montrer l'actualisation (F5) qui fonctionne.
3. **Fonctionnalités bonus** : Taper "Spring" dans la barre de recherche (filtrage dynamique en JavaScript). Montrer le badge rouge "Dernières places".
4. Faire une réservation et montrer la déduction des points.

### Phase 2 : Qualité et Tests
1. Arrêter le serveur (`Ctrl+C`).
2. Lancer les tests : `python -m pytest -q` (montrer les 143 tests verts).
3. Lancer Flake8 : `flake8 --count` (montrer le 0, preuve de qualité PEP 8).
4. Montrer la couverture : `python -m pytest --cov=server --cov-report=term-missing`.

### Phase 3 : Performance
1. Ouvrir le rapport Locust dans le navigateur (`rapports/locust_rapport.html`).
2. Montrer que les temps de réponse sont en millisecondes (ex: 17ms) et qu'il y a 0 échec, prouvant le respect des limites de 5s et 2s.

### Phase 4 : Organisation Git
1. `git branch -a` pour montrer les branches `feature/`, `bug/`, `docs/`, `style/`.
2. Expliquer que la branche `qa` a été créée pour la revue, sans être fusionnée (point 8 du guide).

---

## 6. Les Phrases Clés pour le Jury

1. **Sur la sécurité :** *"L'application ne plante plus face aux erreurs utilisateur, car j'ai sécurisé toutes les routes avec des sessions et des validations strictes."*
2. **Sur la persistance :** *"Les données sont maintenant sauvegardées dans les fichiers JSON, garantissant que les réservations ne sont pas perdues après un redémarrage."*
3. **Sur le TDD :** *"Grâce aux 143 tests, j'ai pu corriger les bugs et ajouter de nouvelles fonctionnalités sans jamais casser ce qui existait déjà."*
4. **Sur l'approche globale :** *"J'ai abordé ce projet comme une mission professionnelle, en respectant les normes de qualité (Flake8), de performance (Locust) et d'organisation (Git)."*