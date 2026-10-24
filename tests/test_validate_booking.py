import server


def club(points):
    return {"name": "X", "email": "x@x.com", "points": str(points)}


def competition(places):
    return {"name": "C", "date": "2099-01-01 10:00:00", "numberOfPlaces": str(places)}


def test_points_suffisants_autorise():
    assert server.validate_booking(club(5), competition(20), 5) is None


def test_points_insuffisants_refuse():
    assert "Not enough points" in server.validate_booking(club(4), competition(20), 5)