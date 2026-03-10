from app.routes import public as public_routes


def test_public_menu_ok(client, monkeypatch):
    def _fake_get_menu_by_qr(_db, _qr_token):
        return {
            "restaurant": "Demo",
            "table": "T1",
            "categories": [],
        }

    monkeypatch.setattr(public_routes, "get_menu_by_qr", _fake_get_menu_by_qr)

    response = client.get("/api/v1/public/token123/menu")

    assert response.status_code == 200
    assert response.json()["restaurant"] == "Demo"


def test_public_menu_not_found(client, monkeypatch):
    monkeypatch.setattr(public_routes, "get_menu_by_qr", lambda _db, _qr_token: None)

    response = client.get("/api/v1/public/missing/menu")

    assert response.status_code == 404


def test_vote_invalid_dish_id(client, monkeypatch):
    def _fake_create_vote(_db, _qr_token, _dish_id, _session_id):
        raise ValueError("Invalid dish_id format")

    monkeypatch.setattr(public_routes, "create_vote", _fake_create_vote)

    response = client.post(
        "/api/v1/public/token123/votes",
        json={"dish_id": "bad", "session_id": "session-a"},
    )

    assert response.status_code == 400


def test_vote_payload_validation(client):
    response = client.post(
        "/api/v1/public/token123/votes",
        json={"dish_id": "2a8f8192-c502-4349-8a28-a45bf9cd7462"},
    )

    assert response.status_code == 422


def test_vote_qr_not_found(client, monkeypatch):
    monkeypatch.setattr(public_routes, "create_vote", lambda _db, _qr_token, _dish_id, _session_id: None)

    response = client.post(
        "/api/v1/public/missing/votes",
        json={"dish_id": "2a8f8192-c502-4349-8a28-a45bf9cd7462", "session_id": "session-a"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "QR token not found"


def test_vote_dish_not_found(client, monkeypatch):
    monkeypatch.setattr(
        public_routes,
        "create_vote",
        lambda _db, _qr_token, _dish_id, _session_id: {"error": "dish_not_found"},
    )

    response = client.post(
        "/api/v1/public/token123/votes",
        json={"dish_id": "2a8f8192-c502-4349-8a28-a45bf9cd7462", "session_id": "session-a"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dish not found for this restaurant"


def test_feedback_ok(client, monkeypatch):
    monkeypatch.setattr(
        public_routes,
        "create_feedback",
        lambda _db, _qr_token, _rating, _comment, _session_id: {
            "status": "received",
            "rating": 5,
        },
    )

    response = client.post(
        "/api/v1/public/token123/feedback",
        json={"rating": 5, "comment": "great", "session_id": "session-a"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "received"


def test_feedback_qr_not_found(client, monkeypatch):
    monkeypatch.setattr(
        public_routes,
        "create_feedback",
        lambda _db, _qr_token, _rating, _comment, _session_id: None,
    )

    response = client.post(
        "/api/v1/public/missing/feedback",
        json={"rating": 5, "comment": "ok", "session_id": "session-a"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "QR token not found"


def test_ranking_ok(client, monkeypatch):
    monkeypatch.setattr(
        public_routes,
        "get_today_ranking",
        lambda _db, _qr_token: {"date": "2026-03-10", "ranking": []},
    )

    response = client.get("/api/v1/public/token123/ranking/today")

    assert response.status_code == 200
    assert "ranking" in response.json()
