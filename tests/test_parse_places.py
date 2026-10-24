import pytest

import server


@pytest.mark.parametrize("saisie, attendu", [("3", 3), (" 5 ", 5), (7, 7), ("1", 1)])
def test_saisie_valide(saisie, attendu):
    assert server.parse_places(saisie) == attendu


@pytest.mark.parametrize("saisie", ["", "   ", "abc", "1.5", "0", "-4", None, "3 places"])
def test_saisie_invalide_retourne_none(saisie):
    assert server.parse_places(saisie) is None