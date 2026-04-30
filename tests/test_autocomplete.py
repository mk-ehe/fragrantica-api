def test_autocomplete_valid_q(client):
    params = {"q": "Va"}
    response = client.get("/autocomplete", params=params)
    
    assert response.status_code == 200
    assert response.json()["results"] != []

def test_autocomplete_invalid_q(client):
    params = {"q": "*@!"}
    response = client.get("/autocomplete", params=params)
    
    assert response.status_code == 200
    assert response.json()["results"] == []

def test_autocomplete_empty_q(client):
    params = {"q": ""}
    response = client.get("/autocomplete", params=params)
    
    assert response.status_code == 200
    assert response.json()["results"] == []

def test_autocomplete_one_q(client):
    params = {"q": "S"}
    response = client.get("/autocomplete", params=params)
    
    assert response.status_code == 200
    assert response.json()["results"] == []

def test_autocomplete_case_sensitivity(client):
    res_lower = client.get("/autocomplete", params={"q":"dior"})
    res_title = client.get("/autocomplete", params={"q":"Dior"})
    res_upper = client.get("/autocomplete", params={"q":"DIOR"})

    assert res_lower.status_code == 200
    assert res_title.status_code == 200
    assert res_upper.status_code == 200
    assert res_upper.json() == res_lower.json() == res_title.json()

def test_autocomplete_limit_exceeded(client):
    params = {"q": "dior"}

    for _ in range(60):
        response = client.get("/autocomplete", params=params)
        assert response.status_code == 200

    limit_exceeded = client.get("/autocomplete", params=params)
    assert limit_exceeded.status_code == 429
    assert "rate limit exceeded" in limit_exceeded.json()["error"].lower()
