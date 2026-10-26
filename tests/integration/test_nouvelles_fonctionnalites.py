import server


def test_badge_dernieres_places_affiche(client):
    # On simule une competition avec seulement 2 places
    competition = server.get_competition_by_name("Spring Festival")
    places_originales = competition['numberOfPlaces']
    competition['numberOfPlaces'] = "2"

    reponse = client.post("/showSummary", data={"email": "john@simplylift.co"})

    # On verifie que le badge "Dernieres places" est present
    assert b"Derni\xc3\xa8res places" in reponse.data

    # On remet la valeur d'origine
    competition['numberOfPlaces'] = places_originales