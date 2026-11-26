def test_page_reservation_valide(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.get("/book/Spring Festival/Simply Lift")
    assert reponse.status_code == 200


def test_page_reservation_club_inconnu_ne_plante_pas(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.get("/book/Spring Festival/Fantome", follow_redirects=True)
    assert reponse.status_code == 200
    assert b"Something went wrong" in reponse.data


def test_page_reservation_competition_inconnue_ne_plante_pas(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.get("/book/Fantome/Simply Lift", follow_redirects=True)
    assert reponse.status_code == 200


def test_page_reservation_competition_passee_refusee(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.get("/book/Fall Classic/Simply Lift", follow_redirects=True)
    assert b"already over" in reponse.data


def test_lien_reserver_masque_pour_competition_passee_ou_complete(client):
    reponse = client.post("/showSummary", data={"email": "john@simplylift.co"})
    assert b"/book/Spring%20Festival/Simply%20Lift" in reponse.data
    assert b"/book/Fall%20Classic/" not in reponse.data
