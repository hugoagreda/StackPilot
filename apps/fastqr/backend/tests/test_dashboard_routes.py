from app.routes import dashboard as dashboard_routes


def test_dashboard_overview_ok(client, monkeypatch):
    monkeypatch.setattr(
        dashboard_routes,
        "get_overview",
        lambda _db, _restaurant_slug=None: {
            "total_votes": 12,
            "unique_sessions": 8,
            "avg_rating": 4.5,
            "total_feedback": 5,
        },
    )

    response = client.get("/api/v1/dashboard/overview?restaurant_slug=demo")

    assert response.status_code == 200
    body = response.json()
    assert body["total_votes"] == 12
    assert body["unique_sessions"] == 8
    assert body["avg_rating"] == 4.5
    assert body["total_feedback"] == 5
