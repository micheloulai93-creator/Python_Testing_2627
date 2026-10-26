def test_connexion_email_inconnu_ne_plante_pas(client):
    reponse = client.post("/showSummary", data={"email": "inconnu@x.com"},
                          follow_redirects=True)
    assert reponse.status_code == 200
    assert b"email was not found" in reponse.data


def test_logout_redirige_vers_l_accueil(client):
    reponse = client.get("/logout")
    assert reponse.status_code == 302
    assert reponse.headers["Location"].endswith("/")