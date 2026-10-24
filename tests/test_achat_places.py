import server

import pytest

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