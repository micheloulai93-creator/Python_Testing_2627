import server


def test_tableau_affiche_tous_les_clubs(client):
    reponse = client.get("/points")
    assert reponse.status_code == 200
    for club in server.clubs:
        assert club["name"].encode() in reponse.data


def test_tableau_est_trie_par_points_decroissants(client):
    reponse = client.get("/points")
    html = reponse.data.decode()
    # Simply Lift (13) doit apparaitre avant Iron Temple (4)
    index_simply = html.find("Simply Lift")
    index_iron = html.find("Iron Temple")
    assert index_simply < index_iron


def test_tableau_est_public_sans_connexion(client):
    reponse = client.get("/points")
    assert reponse.status_code == 200


def test_tableau_se_met_a_jour_apres_une_reservation(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    client.post("/purchasePlaces",
                data={"club": "Simply Lift", "competition": "Spring Festival", "places": 3})
    html = client.get("/points").data.decode()
    assert "Simply Lift" in html
    assert ">10<" in html
