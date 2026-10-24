import server


def test_get_club_by_email_trouve_le_club():
    assert server.get_club_by_email("john@simplylift.co")["name"] == "Simply Lift"


def test_get_club_by_email_inconnu_retourne_none():
    assert server.get_club_by_email("inconnu@nulle-part.com") is None


def test_get_club_by_email_vide_retourne_none():
    assert server.get_club_by_email("") is None


def test_get_club_by_name():
    assert server.get_club_by_name("Iron Temple")["email"] == "admin@irontemple.com"
    assert server.get_club_by_name("Fantome") is None


def test_get_competition_by_name():
    assert server.get_competition_by_name("Spring Festival")["numberOfPlaces"] == "25"
    assert server.get_competition_by_name("Fantome") is None