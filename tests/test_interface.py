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


def test_messages_affiches_avec_une_classe_flash(client):
    reponse = client.post("/showSummary", data={"email": "inconnu@x.com"},
                          follow_redirects=True)
    assert b'class="flash"' in reponse.data


def test_page_reservation_affiche_les_points_du_club(client):
    reponse = client.get("/book/Spring Festival/Simply Lift")
    assert b"Your points: 13" in reponse.data