import server


def test_points_des_clubs_sont_valides():
    for club in server.loadClubs():
        assert int(club["points"]) >= 0


def test_au_moins_3_clubs():
    assert len(server.loadClubs()) >= 3


def test_places_des_competitions_sont_valides():
    for comp in server.loadCompetitions():
        assert int(comp["numberOfPlaces"]) >= 0


def test_au_moins_2_competitions_a_venir():
    a_venir = [c for c in server.loadCompetitions()
               if not server.is_competition_over(c)]
    assert len(a_venir) >= 2