"""Tests unitaires complementaires : saisie du nombre de places et dates."""
from datetime import datetime

import pytest

import server


# --- parse_places : cas supplementaires ---

@pytest.mark.parametrize("saisie, attendu", [
    ("12", 12),
    ("012", 12),
    ("+3", 3),
    ("1000", 1000),
    ("\n4\n", 4),
])
def test_parse_places_accepte_les_entiers_ecrits_de_plusieurs_facons(saisie,
                                                                     attendu):
    assert server.parse_places(saisie) == attendu


@pytest.mark.parametrize("saisie", ["1e3", "0x10", "1,5", "--1", 3.7, []])
def test_parse_places_refuse_les_formats_non_entiers(saisie):
    assert server.parse_places(saisie) is None


# --- is_competition_over : limites de l'horloge ---

DATE = "2030-05-05 12:00:00"


@pytest.mark.parametrize("maintenant, passee", [
    (datetime(2029, 1, 1), False),
    (datetime(2030, 5, 5, 11, 59, 59), False),
    (datetime(2030, 5, 5, 12, 0, 0), False),
    (datetime(2030, 5, 5, 12, 0, 1), True),
    (datetime(2031, 1, 1), True),
])
def test_competition_passee_selon_l_heure(maintenant, passee):
    resultat = server.is_competition_over({"date": DATE}, now=maintenant)
    assert resultat is passee


@pytest.mark.parametrize("date", [
    "2030-05-05",
    "05/05/2030",
    "2030-05-05T12:00:00",
    "",
])
def test_formats_de_date_invalides_consideres_passes(date):
    assert server.is_competition_over({"date": date}) is True
