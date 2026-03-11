from app.routes import dashboard as dashboard_routes
from app.main import app
from app.utils.auth import CurrentAuth


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


def test_dashboard_games_analytics_ok(client, monkeypatch):
    app.dependency_overrides[dashboard_routes.get_current_auth] = lambda: CurrentAuth(
        user_id="u1",
        email="manager@example.com",
        role="manager",
        restaurant_id="11111111-1111-1111-1111-111111111111",
    )

    monkeypatch.setattr(
        dashboard_routes,
        "get_games_analytics",
        lambda _db, _restaurant_id: {
            "total_spins": 10,
            "unique_sessions": 8,
            "issued_rewards": 5,
            "redeemed_rewards": 2,
            "redemption_rate": 0.4,
        },
    )

    response = client.get("/api/v1/dashboard/restaurants/11111111-1111-1111-1111-111111111111/games/analytics")
    app.dependency_overrides.pop(dashboard_routes.get_current_auth, None)

    assert response.status_code == 200
    assert response.json()["total_spins"] == 10


def test_dashboard_redeem_reward_ok(client, monkeypatch):
    app.dependency_overrides[dashboard_routes.get_current_auth] = lambda: CurrentAuth(
        user_id="u1",
        email="manager@example.com",
        role="manager",
        restaurant_id="11111111-1111-1111-1111-111111111111",
    )

    monkeypatch.setattr(
        dashboard_routes,
        "redeem_reward",
        lambda _db, _restaurant_id, _reward_code: {
            "reward_code": "FREE123",
            "reward_status": "redeemed",
        },
    )

    response = client.patch(
        "/api/v1/dashboard/restaurants/11111111-1111-1111-1111-111111111111/rewards/FREE123/redeem"
    )
    app.dependency_overrides.pop(dashboard_routes.get_current_auth, None)

    assert response.status_code == 200
    assert response.json()["reward_status"] == "redeemed"


def test_dashboard_game_settings_today_ok(client, monkeypatch):
    app.dependency_overrides[dashboard_routes.get_current_auth] = lambda: CurrentAuth(
        user_id="u1",
        email="manager@example.com",
        role="manager",
        restaurant_id="11111111-1111-1111-1111-111111111111",
    )

    monkeypatch.setattr(
        dashboard_routes,
        "get_today_game_settings",
        lambda _db, _restaurant_id: {
            "date": "2026-03-11",
            "rules": [
                {"label": "No Prize", "weight": 40, "redeemable": False, "is_active": True},
            ],
        },
    )

    response = client.get("/api/v1/dashboard/restaurants/11111111-1111-1111-1111-111111111111/games/settings/today")
    app.dependency_overrides.pop(dashboard_routes.get_current_auth, None)

    assert response.status_code == 200
    assert response.json()["rules"][0]["label"] == "No Prize"


def test_dashboard_scoring_settings_patch_ok(client, monkeypatch):
    app.dependency_overrides[dashboard_routes.get_current_auth] = lambda: CurrentAuth(
        user_id="u1",
        email="manager@example.com",
        role="manager",
        restaurant_id="11111111-1111-1111-1111-111111111111",
    )

    monkeypatch.setattr(
        dashboard_routes,
        "update_scoring_settings",
        lambda _db, _restaurant_id, _vote_points: {"vote_points": 3},
    )

    response = client.patch(
        "/api/v1/dashboard/restaurants/11111111-1111-1111-1111-111111111111/scoring/settings",
        json={"vote_points": 3},
    )
    app.dependency_overrides.pop(dashboard_routes.get_current_auth, None)

    assert response.status_code == 200
    assert response.json()["vote_points"] == 3
