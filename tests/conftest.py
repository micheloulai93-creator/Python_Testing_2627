"""Fixtures partagées : jeu de données isolé du JSON réel, remis à zéro à chaque test."""
import copy

import pytest

import server

CLUBS = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
    {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"},
]

COMPETITIONS = [
    {"name": "Spring Festival", "date": "2099-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"},
    {"name": "Sold Out Cup", "date": "2099-06-01 09:00:00", "numberOfPlaces": "0"},
]


@pytest.fixture(autouse=True)
def donnees_de_test(monkeypatch):
    """Remplace les données du serveur par une copie propre avant chaque test."""
    monkeypatch.setattr(server, "clubs", copy.deepcopy(CLUBS))
    monkeypatch.setattr(server, "competitions", copy.deepcopy(COMPETITIONS))
    monkeypatch.setattr(server, "bookings", {})


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    with server.app.test_client() as c:
        yield c