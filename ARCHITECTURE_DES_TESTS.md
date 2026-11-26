# Architecture et Organisation des Tests

Ce document détaille l'organisation de la suite de tests du projet Güdlft. Conformément au guide de développement (Règle n°4), les tests sont rigoureusement séparés en trois catégories (unitaires, intégration, fonctionnels) pour faciliter la maintenance et le débogage.

La suite compte **137 tests** au total, avec un ratio d'environ 2 tests unitaires pour 1 test d'intégration/fonctionnel.

---

## 1. Le dossier `tests/unit/` (Tests Unitaires)

**Objectif :** Tester chaque fonction de manière isolée, sans interface graphique ni base de données. C'est la base de la pyramide des tests (TDD).

- **`test_clubs.py`** :
  - *Ce qu'il teste :* Les fonctions de recherche de clubs (`get_club_by_email`, `get_club_by_name`).
  - *Détails :* Il vérifie que si on cherche un email existant (ex: `john@simplylift.co`), on obtient le bon nom. Il vérifie aussi que si on cherche un email inconnu, la fonction renvoie `None` sans faire planter l'application.

- **`test_donnees_json.py`** :
  - *Ce qu'il teste :* L'intégrité des données de base dans les fichiers JSON.
  - *Détails :* Il s'assure qu'il y a au moins 3 clubs dans `clubs.json`, que les points sont convertibles en nombres, et qu'il y a au moins 2 compétitions à venir. C'est un test de "sécurité" pour vérifier que le fichier de données n'a pas été corrompu.

- **`test_parse_places.py`** :
  - *Ce qu'il teste :* La fonction `parse_places()`.
  - *Détails :* C'est le test de la saisie utilisateur. Il vérifie que si on tape "2" (en texte), ça devient bien le nombre 2. Mais si on tape "abc", "-5" ou "1,5", la fonction renvoie `None` (ce qui déclenchera une erreur propre dans l'application). C'est la gestion des "Sad Paths".

- **`test_recherches.py`** :
  - *Ce qu'il teste :* Les fonctions de recherche globales (`get_competition_by_name`).
  - *Détails :* Il teste la robustesse. Que se passe-t-il si on cherche une compétition qui n'existe pas (ex: "Fantome") ? Le test s'assure que ça ne fait pas planter l'application (pas d'erreur 500).

- **`test_regles_reservation.py`** :
  - *Ce qu'il teste :* Le cœur de la logique métier (`validate_booking`).
  - *Détails :* C'est le plus gros fichier de tests. Il vérifie toutes les règles :
    - La limite de 12 places cumulées.
    - Le stock de places disponibles.
    - Les points du club.
    - L'ordre de priorité des règles (ex: si la compétition est passée, on affiche l'erreur "passée" avant l'erreur "pas assez de points").

- **`test_saisie_et_dates.py`** :
  - *Ce qu'il teste :* La conversion des dates (`is_competition_over`).
  - *Détails :* Il vérifie que le code comprend bien le format "AAAA-MM-JJ HH:MM:SS". Il teste aussi les limites (ex: une compétition à 11h59 est considérée comme passée à midi). Et il vérifie qu'une date mal formatée (ex: "05/05/2030") est considérée comme passée par sécurité.

- **`test_validate_booking.py`** :
  - *Ce qu'il teste :* Des scénarios spécifiques de réservation.
  - *Détails :* Il complète `test_regles_reservation.py` en testant des cas plus complexes, comme la robustesse quand on passe des types de données inattendus (texte au lieu d'entier).

---

## 2. Le dossier `tests/integration/` (Tests d'Intégration)

**Objectif :** Tester les routes Flask (les URL) en simulant un client web pour vérifier que les différentes couches de l'application communiquent bien entre elles.

- **`test_achat_places.py`** :
  - *Ce qu'il teste :* La route `/purchasePlaces`.
  - *Détails :* Il simule un achat complet : on se connecte, on envoie le formulaire avec un nombre de places, et on vérifie que la page de réponse affiche le bon message (succès ou erreur). Il vérifie aussi que les points sont bien déduits en mémoire.

- **`test_connexion.py`** :
  - *Ce qu'il teste :* La route `/showSummary` (le login).
  - *Détails :* Il simule une connexion avec un email valide. Il vérifie que l'utilisateur est redirigé vers le tableau de bord, et que la session est bien créée.

- **`test_nouvelles_fonctionnalites.py`** :
  - *Ce qu'il teste :* Les fonctionnalités bonus.
  - *Détails :* Par exemple, il vérifie que le badge "Dernières places" s'affiche bien dans le code HTML quand il ne reste que 2 places.

- **`test_page_reservation.py`** :
  - *Ce qu'il teste :* La route `/book/<competition>/<club>`.
  - *Détails :* Il s'assure que la page s'affiche correctement. Il vérifie aussi que si on essaie d'accéder à une compétition passée via l'URL, on est redirigé avec un message d'erreur.

- **`test_tableau_points.py`** :
  - *Ce qu'il teste :* La route `/points`.
  - *Détails :* Il vérifie que le tableau est accessible même sans être connecté (exigence de transparence), et qu'il est trié par ordre décroissant de points.

---

## 3. Le dossier `tests/functional/` (Tests Fonctionnels)

**Objectif :** Tester l'interface HTML générée, comme le ferait un utilisateur devant son écran.

- **`test_html_formulaires.py`** :
  - *Ce qu'il teste :* La structure du code HTML.
  - *Détails :* Il vérifie que le champ de saisie du nombre de places a bien les attributs `min="1"` et `max="12"`. Cela empêche l'utilisateur de taper 0 ou 15 au clavier.

- **`test_interface.py`** :
  - *Ce qu'il teste :* L'apparence visuelle des messages et la feuille de style.
  - *Détails :* Il vérifie que la feuille de style `/static/style.css` est bien chargée. Il vérifie aussi que quand il y a une erreur, le message HTML contient bien la classe Bootstrap `alert-danger` (pour avoir le fond rouge).

---

## 4. Le dossier `tests/performance/`

**Objectif :** Vérifier les temps de réponse (Règle n°5).

- **`locustfile.py`** :
  - *Ce qu'il teste :* La vitesse de l'application sous charge.
  - *Détails :* Ce n'est pas un test Pytest classique, c'est un script pour Locust. Il simule 6 utilisateurs qui se connectent et réservent des places en même temps pour vérifier que les temps de réponse sont inférieurs à 5s (liste) et 2s (réservation).

---

## 5. Le fichier `tests/conftest.py`

- **Ce qu'il fait :** C'est le chef d'orchestre des tests.
- **Détails :** Il contient les fixtures (`client` et `donnees_de_test`). Il s'assure que chaque test démarre avec un faux navigateur et des données propres (via `monkeypatch`), sans jamais toucher aux vrais fichiers JSON. Cela garantit l'isolation des tests.

---

## 💡 Résumé pour la Soutenance

Si le jury vous demande : *"Pourquoi avoir séparé les tests en trois dossiers ?"*

**Réponse :** *"J'ai suivi la règle n°4 du guide de développement. J'ai séparé les tests unitaires (qui testent les fonctions isolées), les tests d'intégration (qui testent les routes Flask avec un faux client), et les tests fonctionnels (qui vérifient le rendu HTML). Cela me permet de savoir immédiatement si un bug vient de la logique pure (unitaire) ou de l'interface (fonctionnel)."*