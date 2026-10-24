import server


def acheter(client, club, competition, places):
    return client.post("/purchasePlaces",
                       data={"club": club, "competition": competition, "places": places})


def test_achat_valide_affiche_confirmation(client):
    reponse = acheter(client, "Simply Lift", "Spring Festival", 3)
    assert reponse.status_code == 200
    assert b"Great-booking complete!" in reponse.data


def test_achat_deduit_les_points_du_club(client):
    points_avant = int(server.get_club_by_name("Simply Lift")["points"])
    reponse = acheter(client, "Simply Lift", "Spring Festival", 3)
    assert int(server.get_club_by_name("Simply Lift")["points"]) == points_avant - 3
    assert ("Points available: %d" % (points_avant - 3)).encode() in reponse.data