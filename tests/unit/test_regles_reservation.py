"""Tests unitaires des regles de validate_booking, une regle a la fois."""
import copy

import pytest

import server


def club(points):
    return {"name": "X", "email": "x@x.com", "points": points}


def competition(places, date="2099-01-01 10:00:00"):
    return {"name": "C", "date": date, "numberOfPlaces": places}


# --- Limite de 12 places par club et par competition ---

@pytest.mark.parametrize("deja, demande, autorise", [
    (0, 1, True),
    (0, 12, True),
    (0, 13, False),
    (5, 7, True),
    (5, 8, False),
    (11, 1, True),
    (11, 2, False),
    (12, 1, False),
])
def test_limite_de_12_places_cumulees(deja, demande, autorise):
    erreur = server.validate_booking(club(30), competition(30), demande,
                                     already_booked=deja)
    if autorise:
        assert erreur is None
    else:
        assert "more than 12" in erreur


# --- Stock de places de la competition ---

@pytest.mark.parametrize("stock, demande, message", [
    (10, 10, None),
    (10, 11, "Not enough places"),
    (1, 1, None),
    (1, 2, "Not enough places"),
    (0, 1, "full"),
    (0, 5, "full"),
])
def test_stock_de_places(stock, demande, message):
    erreur = server.validate_booking(club(12), competition(stock), demande)
    if message is None:
        assert erreur is None
    else:
        assert message in erreur


# --- Points du club ---

@pytest.mark.parametrize("points, demande, message", [
    (5, 5, None),
    (5, 6, "Not enough points"),
    (0, 1, "Not enough points"),
    (12, 12, None),
    (11, 12, "Not enough points"),
    (1, 1, None),
])
def test_points_du_club(points, demande, message):
    erreur = server.validate_booking(club(points), competition(30), demande)
    if message is None:
        assert erreur is None
    else:
        assert message in erreur


# --- Ordre de priorite des regles ---

def test_competition_passee_prime_sur_toutes_les_autres_regles():
    passee = competition(30, date="2020-01-01 10:00:00")
    erreur = server.validate_booking(club(30), passee, 1)
    assert "already over" in erreur


def test_competition_passee_prime_meme_si_la_limite_est_depassee():
    passee = competition(30, date="2020-01-01 10:00:00")
    erreur = server.validate_booking(club(30), passee, 13)
    assert "already over" in erreur


def test_limite_de_12_prime_sur_competition_complete():
    erreur = server.validate_booking(club(30), competition(0), 13)
    assert "more than 12" in erreur


def test_stock_insuffisant_prime_sur_points_insuffisants():
    erreur = server.validate_booking(club(1), competition(2), 5)
    assert "Not enough places" in erreur


# --- Robustesse ---

@pytest.mark.parametrize("points", ["5", 5])
@pytest.mark.parametrize("places", ["20", 20])
def test_nombres_acceptes_en_texte_ou_en_entier(points, places):
    assert server.validate_booking(club(points), competition(places), 5) is None


def test_validate_booking_ne_modifie_pas_ses_arguments():
    un_club, une_competition = club(5), competition(20)
    club_avant = copy.deepcopy(un_club)
    competition_avant = copy.deepcopy(une_competition)
    server.validate_booking(un_club, une_competition, 3)
    assert un_club == club_avant
    assert une_competition == competition_avant
