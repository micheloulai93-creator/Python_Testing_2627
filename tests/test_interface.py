def test_feuille_de_style_servie(client):
    reponse = client.get("/static/style.css")
    assert reponse.status_code == 200
    assert b"font-family" in reponse.data


def test_pages_utilisent_la_feuille_de_style(client):
    pages = [
        client.get("/"),
        client.post("/showSummary", data={"email": "john@simplylift.co"}),
        client.get("/book/Spring Festival/Simply Lift"),
    ]
    for reponse in pages:
        assert b"/static/style.css" in reponse.data


def test_page_reservation_affiche_les_points_du_club(client):
    reponse = client.get("/book/Spring Festival/Simply Lift")
    assert b"Your points: 13" in reponse.data


# --- Messages : succes et erreurs distingues ---

def test_message_email_inconnu_est_une_erreur(client):
    reponse = client.post("/showSummary", data={"email": "inconnu@x.com"},
                          follow_redirects=True)
    assert b'class="flash flash-error"' in reponse.data


def test_message_achat_reussi_est_un_succes(client):
    reponse = client.post("/purchasePlaces",
                          data={"club": "Simply Lift", "competition": "Spring Festival",
                                "places": 2})
    assert b'class="flash flash-success"' in reponse.data
    assert b"flash-error" not in reponse.data


def test_message_achat_refuse_est_une_erreur(client):
    reponse = client.post("/purchasePlaces",
                          data={"club": "Iron Temple", "competition": "Spring Festival",
                                "places": 5})
    assert b'class="flash flash-error"' in reponse.data
    assert b"flash-success" not in reponse.data


def test_message_competition_passee_est_une_erreur(client):
    reponse = client.get("/book/Fall Classic/Simply Lift")
    assert b'class="flash flash-error"' in reponse.data
