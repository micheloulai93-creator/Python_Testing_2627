"""Test de charge Locust (guide de developpement, point 5).

Exigences du sujet, avec 6 utilisateurs simultanes :
- recuperer la liste des competitions : 5 secondes maximum ;
- mettre a jour le total de points : 2 secondes maximum.
"""
import random

from locust import HttpUser, between, task

CLUBS = [
    ("john@simplylift.co", "Simply Lift"),
    ("admin@irontemple.com", "Iron Temple"),
    ("kate@shelifts.co.uk", "She Lifts"),
    ("contact@powerhouse.fr", "Power House"),
    ("info@barbellclub.com", "Barbell Club"),
]

COMPETITIONS_A_VENIR = ["Spring Festival", "Summer Showdown", "Winter Open"]

LIMITE_LISTE_SECONDES = 5.0
LIMITE_MISE_A_JOUR_SECONDES = 2.0


def controler(reponse, limite):
    """Marque la requete en echec si elle est en erreur ou trop lente."""
    duree = reponse.elapsed.total_seconds()
    if reponse.status_code != 200:
        reponse.failure("HTTP %s" % reponse.status_code)
    elif duree > limite:
        reponse.failure("trop lent : %.2f s (limite %.0f s)" % (duree, limite))
    else:
        reponse.success()


class Secretaire(HttpUser):
    """Un secretaire de club qui consulte les competitions et reserve."""

    wait_time = between(1, 2)

    def on_start(self):
        self.email, self.club = random.choice(CLUBS)

    @task(3)
    def liste_des_competitions(self):
        with self.client.post("/showSummary", data={"email": self.email},
                              name="Liste des competitions",
                              catch_response=True) as reponse:
            controler(reponse, LIMITE_LISTE_SECONDES)

    @task(2)
    def mise_a_jour_des_points(self):
        donnees = {"club": self.club,
                   "competition": random.choice(COMPETITIONS_A_VENIR),
                   "places": 1}
        with self.client.post("/purchasePlaces", data=donnees,
                              name="Mise a jour des points",
                              catch_response=True) as reponse:
            controler(reponse, LIMITE_MISE_A_JOUR_SECONDES)

    @task(1)
    def tableau_des_points(self):
        with self.client.get("/points", name="Tableau des points",
                             catch_response=True) as reponse:
            controler(reponse, LIMITE_LISTE_SECONDES)
