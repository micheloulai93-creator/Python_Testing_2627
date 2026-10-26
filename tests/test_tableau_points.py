import server


def test_tableau_accessible_sans_connexion(client):
    reponse = client.get("/points")
    assert reponse.status_code == 200


def test_tableau_affiche_tous_les_clubs_et_leurs_points(client):
    html = client.get("/points").data.decode()
    for club in server.clubs:
        assert club["name"] in html
        assert str(club["points"]) in html


def test_tableau_est_en_lecture_seule(client):
    html = client.get("/points").data.decode()
    assert "<form" not in html
    assert "<input" not in html


def test_tableau_se_met_a_jour_apres_une_reservation(client):
    client.post("/purchasePlaces",
                data={"club": "Simply Lift", "competition": "Spring Festival", "places": 3})
    html = client.get("/points").data.decode()
    assert "Simply Lift" in html
    assert ">10<" in html


def test_tableau_trie_du_plus_au_moins_de_points(client):
    html = client.get("/points").data.decode()
    assert html.index("Simply Lift") < html.index("She Lifts") < html.index("Iron Temple")


def test_lien_vers_le_tableau_sur_la_page_d_accueil(client):
    assert b'href="/points"' in client.get("/").data


def test_post_interdit_sur_le_tableau(client):
    assert client.post("/points").status_code == 405
