"""Tests unitaires des fonctions de recherche de clubs et de competitions."""
import pytest

import server


@pytest.mark.parametrize("email, nom", [
    ("john@simplylift.co", "Simply Lift"),
    ("admin@irontemple.com", "Iron Temple"),
    ("kate@shelifts.co.uk", "She Lifts"),
])
def test_recherche_de_club_par_email(email, nom):
    assert server.get_club_by_email(email)["name"] == nom


@pytest.mark.parametrize("nom", ["Simply Lift", "Iron Temple", "She Lifts"])
def test_recherche_de_club_par_nom(nom):
    assert server.get_club_by_name(nom)["name"] == nom


@pytest.mark.parametrize("nom", ["Fantome", "", " "])
def test_recherche_de_club_inconnu(nom):
    assert server.get_club_by_name(nom) is None


@pytest.mark.parametrize("nom", ["Spring Festival", "Fall Classic",
                                 "Sold Out Cup"])
def test_recherche_de_competition_par_nom(nom):
    assert server.get_competition_by_name(nom)["name"] == nom


@pytest.mark.parametrize("nom", ["", "Fantome"])
def test_recherche_de_competition_inconnue(nom):
    assert server.get_competition_by_name(nom) is None
