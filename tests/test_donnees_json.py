"""Verifie la qualite des vrais fichiers clubs.json et competitions.json."""
from datetime import datetime

import server


# --- clubs.json ---

def test_clubs_ont_les_champs_attendus():
    for club in server.loadClubs():
        assert set(club) == {"name", "email", "points"}


def test_points_des_clubs_sont_des_entiers_positifs():
    for club in server.loadClubs():
        assert isinstance(club["points"], int) and club["points"] >= 0


def test_emails_des_clubs_sont_uniques():
    emails = [club["email"] for club in server.loadClubs()]
    assert len(emails) == len(set(emails))


def test_noms_des_clubs_sont_uniques():
    noms = [club["name"] for club in server.loadClubs()]
    assert len(noms) == len(set(noms))


def test_au_moins_5_clubs():
    assert len(server.loadClubs()) >= 5


# --- competitions.json ---

def test_competitions_ont_les_champs_attendus():
    for comp in server.loadCompetitions():
        assert set(comp) == {"name", "date", "numberOfPlaces"}


def test_places_des_competitions_sont_des_entiers_positifs():
    for comp in server.loadCompetitions():
        assert isinstance(comp["numberOfPlaces"], int) and comp["numberOfPlaces"] >= 0


def test_dates_des_competitions_sont_valides():
    for comp in server.loadCompetitions():
        datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")


def test_noms_des_competitions_sont_uniques():
    noms = [comp["name"] for comp in server.loadCompetitions()]
    assert len(noms) == len(set(noms))


def test_au_moins_3_competitions_a_venir():
    a_venir = [c for c in server.loadCompetitions() if not server.is_competition_over(c)]
    assert len(a_venir) >= 3
