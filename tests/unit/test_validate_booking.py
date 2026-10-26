from datetime import datetime

import server


def club(points):
    return {"name": "X", "email": "x@x.com", "points": str(points)}


def competition(places):
    return {"name": "C", "date": "2099-01-01 10:00:00",
            "numberOfPlaces": str(places)}


def test_points_suffisants_autorise():
    assert server.validate_booking(club(5), competition(20), 5) is None


def test_points_insuffisants_refuse():
    erreur = server.validate_booking(club(4), competition(20), 5)
    assert "Not enough points" in erreur


def test_13_places_refuse_meme_avec_assez_de_points():
    erreur = server.validate_booking(club(20), competition(30), 13)
    assert "more than 12" in erreur


def test_12_places_autorise():
    assert server.validate_booking(club(20), competition(30), 12) is None


def test_plus_de_places_que_disponible_refuse():
    erreur = server.validate_booking(club(12), competition(3), 5)
    assert "Not enough places" in erreur


def test_competition_complete_refusee():
    assert "full" in server.validate_booking(club(12), competition(0), 1)


def test_exactement_les_places_restantes_autorise():
    assert server.validate_booking(club(12), competition(3), 3) is None


# --- Bug 9 : la limite de 12 s'applique au cumul des reservations ---

def test_cumul_avec_reservations_precedentes_depasse_12():
    erreur = server.validate_booking(club(20), competition(30), 5,
                                     already_booked=8)
    assert "more than 12" in erreur


def test_cumul_exactement_12_autorise():
    resultat = server.validate_booking(club(20), competition(30), 4,
                                       already_booked=8)
    assert resultat is None


# --- Bug 10 : competitions passees ---

def test_competition_passee_detectee():
    assert server.is_competition_over({"date": "2020-01-01 10:00:00"}) is True


def test_competition_future_detectee():
    assert server.is_competition_over({"date": "2099-01-01 10:00:00"}) is False


def test_is_competition_over_avec_horloge_injectee():
    comp = {"date": "2030-05-05 12:00:00"}
    avant = datetime(2030, 5, 5, 11, 59)
    apres = datetime(2030, 5, 5, 12, 1)
    assert server.is_competition_over(comp, now=avant) is False
    assert server.is_competition_over(comp, now=apres) is True


def test_date_illisible_consideree_passee():
    assert server.is_competition_over({"date": "pas une date"}) is True
    assert server.is_competition_over({}) is True


def test_reservation_refusee_pour_competition_passee():
    comp = {"name": "Old", "date": "2020-01-01 10:00:00",
            "numberOfPlaces": "10"}
    assert "already over" in server.validate_booking(club(5), comp, 1)
