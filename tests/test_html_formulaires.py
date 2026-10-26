"""Verifie que les formulaires sont correctement relies (label <-> champ) et valides."""


def test_formulaire_connexion_label_lie_au_champ(client):
    html = client.get("/").data.decode()
    assert 'id=""' not in html
    assert 'for="email"' in html and 'id="email"' in html
    assert "required" in html


def test_formulaire_reservation_label_lie_au_champ(client):
    html = client.get("/book/Spring Festival/Simply Lift").data.decode()
    assert 'id=""' not in html
    assert 'for="places"' in html and 'id="places"' in html
    assert 'min="1"' in html and 'max="12"' in html


def test_page_bienvenue_sans_balise_br_invalide(client):
    html = client.post("/showSummary", data={"email": "john@simplylift.co"}).data.decode()
    assert "</br>" not in html
