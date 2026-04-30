def test_search_note_piramid(client):
    params = {"url": "https://www.fragrantica.pl/perfumy/Dior/Sauvage-Eau-de-Parfum-48100.html"}
    response = client.get("/search", params=params)
    data = response.json()

    assert response.status_code == 200
    assert "search_count" not in data
    assert "_id" not in data
    assert "time_created" not in data
    assert data["url"] != ""
    assert data["fragrance"]["name"] != ""
    assert data["notes"]["top"] != ""
    assert data["notes"]["heart"] != ""
    assert data["notes"]["base"] != ""

def test_search_linear_notes(client):
    params = {"url": "https://www.fragrantica.pl/perfumy/Viktor-Rolf/Spicebomb-Extreme-30499.html"}
    response = client.get("/search", params=params)
    data = response.json()

    assert response.status_code == 200
    assert "search_count" not in data
    assert "_id" not in data
    assert "time_created" not in data
    assert data["url"] != ""
    assert data["fragrance"]["name"] != ""
    assert data["notes"]["linear"] != ""

def test_search_invalid_domain(client):
    wrong_params = {"url": "https://allegro.pl/dior/sauvage"}
    response = client.get("/search", params=wrong_params)

    assert response.status_code == 400
    assert response.json()["detail"].lower() == "Invalid domain. Only official Fragrantica URLs are allowed.".lower()

def test_search_malformed_url(client):
    wrong_params = {"url": "https://[::1/some-perfumes"}
    response = client.get("/search", params=wrong_params)

    assert response.status_code == 400
    assert response.json()["detail"] == "Malformed URL provided."

def test_search_invalid_path(client):
    wrong_params = {"url": "fragrantica.com/fake/perfume/path"}
    response = client.get("/search", params=wrong_params)

    assert response.status_code == 500
    assert response.json()["detail"].lower() == "An error occured while fetching perfume.".lower()

def test_search_no_url(client):
    wrong_params = {"url": ""}
    response = client.get("/search", params=wrong_params)

    assert response.status_code == 400
    assert response.json()["detail"].lower() == "Invalid domain. Only official Fragrantica URLs are allowed.".lower()

def test_search_limit_exceeded(client):
    params = {"url": "https://www.fragrantica.pl/perfumy/Dior/Sauvage-Eau-de-Parfum-48100.html"}
    response = client.get("/search", params=params)
    assert response.status_code == 200

    limit_exceeded = client.get("/search", params=params)
    assert limit_exceeded.status_code == 429
    assert "rate limit exceeded" in limit_exceeded.json()["error"].lower()
