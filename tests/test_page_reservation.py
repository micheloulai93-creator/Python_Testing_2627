def test_page_reservation_valide(client):
    reponse = client.get("/book/Spring Festival/Simply Lift")
    assert reponse.status_code == 200
    assert b"Spring Festival" in reponse.data


def test_page_reservation_club_inconnu_ne_plante_pas(client):
    reponse = client.get("/book/Spring Festival/Fantome", follow_redirects=True)
    assert reponse.status_code == 200
    assert b"Something went wrong" in reponse.data


def test_page_reservation_competition_inconnue_ne_plante_pas(client):
    reponse = client.get("/book/Fantome/Simply Lift")
    assert reponse.status_code == 200
    assert b"Something went wrong" in reponse.data