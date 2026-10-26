import pytest

import server


def acheter(client, club, competition, places):
    return client.post("/purchasePlaces",
                       data={"club": club, "competition": competition, "places": places})


# --- Bug 3 : les points sont deduits apres une reservation ---

def test_achat_valide_affiche_confirmation(client):
    reponse = acheter(client, "Simply Lift", "Spring Festival", 3)
    assert reponse.status_code == 200
    assert b"Great-booking complete!" in reponse.data


def test_achat_deduit_les_points_du_club(client):
    points_avant = int(server.get_club_by_name("Simply Lift")["points"])
    reponse = acheter(client, "Simply Lift", "Spring Festival", 3)
    assert int(server.get_club_by_name("Simply Lift")["points"]) == points_avant - 3
    assert ("Points available: %d" % (points_avant - 3)).encode() in reponse.data


# --- Bug 4 : points insuffisants ---

def test_achat_refuse_si_points_insuffisants(client):
    reponse = acheter(client, "Iron Temple", "Spring Festival", 5)  # 4 points seulement
    assert b"Not enough points" in reponse.data
    assert server.get_club_by_name("Iron Temple")["points"] == "4"
    assert server.get_competition_by_name("Spring Festival")["numberOfPlaces"] == "25"


def test_achat_accepte_si_points_exactement_suffisants(client):
    reponse = acheter(client, "Iron Temple", "Spring Festival", 4)
    assert b"Great-booking complete!" in reponse.data
    assert server.get_club_by_name("Iron Temple")["points"] == 0


# --- Bug 5 : maximum 12 places ---

def test_achat_refuse_plus_de_12_places(client):
    # Simply Lift a 13 points : assez pour 13 places, mais la limite est de 12
    reponse = acheter(client, "Simply Lift", "Spring Festival", 13)
    assert b"more than 12" in reponse.data
    assert server.get_club_by_name("Simply Lift")["points"] == "13"
    assert server.get_competition_by_name("Spring Festival")["numberOfPlaces"] == "25"


# --- Bug 6 : surreservation ---

def test_achat_refuse_si_depasse_les_places_disponibles(client):
    server.get_competition_by_name("Spring Festival")["numberOfPlaces"] = "3"
    reponse = acheter(client, "Simply Lift", "Spring Festival", 5)
    assert b"Not enough places available" in reponse.data
    assert server.get_competition_by_name("Spring Festival")["numberOfPlaces"] == "3"
    assert server.get_club_by_name("Simply Lift")["points"] == "13"


def test_achat_refuse_si_competition_complete(client):
    reponse = acheter(client, "Simply Lift", "Sold Out Cup", 1)
    assert b"competition is full" in reponse.data
    assert server.get_club_by_name("Simply Lift")["points"] == "13"


# --- Bug 7 : saisie invalide ---

@pytest.mark.parametrize("saisie", ["", "abc", "0", "-5", "2.5"])
def test_achat_saisie_invalide_ne_plante_pas_et_ne_modifie_rien(client, saisie):
    reponse = acheter(client, "Simply Lift", "Spring Festival", saisie)
    assert reponse.status_code == 200
    assert b"valid number of places" in reponse.data
    assert server.get_club_by_name("Simply Lift")["points"] == "13"
    assert server.get_competition_by_name("Spring Festival")["numberOfPlaces"] == "25"


def test_achat_sans_champ_places_ne_plante_pas(client):
    reponse = client.post("/purchasePlaces",
                          data={"club": "Simply Lift", "competition": "Spring Festival"})
    assert reponse.status_code == 200
    assert b"valid number of places" in reponse.data


# --- Bug 8 : club ou competition inconnu dans le formulaire ---

def test_achat_club_inconnu_ne_plante_pas(client):
    reponse = acheter(client, "Fantome", "Spring Festival", 2)
    assert reponse.status_code == 302
    assert server.get_competition_by_name("Spring Festival")["numberOfPlaces"] == "25"


def test_achat_competition_inconnue_ne_plante_pas(client):
    reponse = acheter(client, "Simply Lift", "Fantome", 2)
    assert reponse.status_code == 200
    assert b"Something went wrong" in reponse.data
    assert server.get_club_by_name("Simply Lift")["points"] == "13"


def test_achat_sans_champs_ne_plante_pas(client):
    reponse = client.post("/purchasePlaces", data={})
    assert reponse.status_code == 302


# --- Bug 9 : limite de 12 places cumulee ---

def test_cumul_de_plusieurs_achats_limite_a_12(client):
    server.get_club_by_name("Simply Lift")["points"] = "20"
    acheter(client, "Simply Lift", "Spring Festival", 8)
    reponse = acheter(client, "Simply Lift", "Spring Festival", 5)
    assert b"more than 12" in reponse.data
    assert server.get_club_by_name("Simply Lift")["points"] == 12


def test_limite_de_12_est_par_competition(client):
    server.get_club_by_name("Simply Lift")["points"] = "30"
    server.get_competition_by_name("Sold Out Cup")["numberOfPlaces"] = "20"
    acheter(client, "Simply Lift", "Spring Festival", 12)
    reponse = acheter(client, "Simply Lift", "Sold Out Cup", 5)
    assert b"Great-booking complete!" in reponse.data


def test_limite_de_12_est_par_club(client):
    server.get_club_by_name("Simply Lift")["points"] = "30"
    server.get_club_by_name("She Lifts")["points"] = "20"
    acheter(client, "Simply Lift", "Spring Festival", 12)
    reponse = acheter(client, "She Lifts", "Spring Festival", 12)
    assert b"Great-booking complete!" in reponse.data


# --- Bug 10 : competition passee ---

def test_achat_refuse_pour_competition_passee(client):
    reponse = acheter(client, "Simply Lift", "Fall Classic", 2)
    assert b"already over" in reponse.data
    assert server.get_club_by_name("Simply Lift")["points"] == "13"
    assert server.get_competition_by_name("Fall Classic")["numberOfPlaces"] == "13"
    