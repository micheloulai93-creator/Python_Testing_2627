def test_pages_utilisent_la_feuille_de_style(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    pages = [
        client.get("/"),
        client.get("/showSummary"),
        client.get("/book/Spring Festival/Simply Lift"),
    ]
    for reponse in pages:
        assert b"/static/style.css" in reponse.data


def test_page_reservation_affiche_les_points_du_club(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.get("/book/Spring Festival/Simply Lift")
    assert b"Your points: 13" in reponse.data


def test_message_email_inconnu_est_une_erreur(client):
    reponse = client.post("/showSummary", data={"email": "inconnu@x.com"},
                          follow_redirects=True)
    assert b'alert-danger' in reponse.data


def test_message_achat_reussi_est_un_succes(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.post("/purchasePlaces",
                          data={"club": "Simply Lift", "competition": "Spring Festival",
                                "places": 2},
                          follow_redirects=True)
    assert b'alert-success' in reponse.data


def test_message_achat_refuse_est_une_erreur(client):
    client.post("/showSummary", data={"email": "admin@irontemple.com"})
    reponse = client.post("/purchasePlaces",
                          data={"club": "Iron Temple", "competition": "Spring Festival",
                                "places": 5},
                          follow_redirects=True)
    assert b'alert-danger' in reponse.data


def test_message_competition_passee_est_une_erreur(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    reponse = client.get("/book/Fall Classic/Simply Lift", follow_redirects=True)
    assert b'alert-danger' in reponse.data