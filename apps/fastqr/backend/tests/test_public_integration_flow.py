import os
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models.category import Category
from app.models.dish import Dish
from app.models.restaurant import Restaurant
from app.models.table import Table

TEST_DATABASE_URL = os.getenv("FASTQR_TEST_DATABASE_URL")


@pytest.fixture(scope="module")
def integration_client() -> Generator[TestClient, None, None]:
    if not TEST_DATABASE_URL:
        pytest.skip("FASTQR_TEST_DATABASE_URL is required for integration tests")

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def seeded_entities() -> dict[str, str]:
    if not TEST_DATABASE_URL:
        pytest.skip("FASTQR_TEST_DATABASE_URL is required for integration tests")

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    restaurant = Restaurant(name="Flow Test", slug="flow-test", timezone="UTC")
    restaurant_id: str
    table_token: str
    dish_id: str

    with SessionLocal() as db:
        db.add(restaurant)
        db.flush()

        category = Category(restaurant_id=restaurant.id, name="Main", sort_order=1)
        db.add(category)
        db.flush()

        dish = Dish(
            restaurant_id=restaurant.id,
            category_id=category.id,
            name="Burger",
            description="Integration burger",
            price_cents=1490,
            is_available=True,
        )
        db.add(dish)

        table = Table(
            restaurant_id=restaurant.id,
            code="T1",
            qr_token=str(uuid.uuid4()),
        )
        db.add(table)

        db.commit()

        restaurant_id = str(restaurant.id)
        table_token = table.qr_token
        dish_id = str(dish.id)

    engine.dispose()

    return {
        "restaurant_id": restaurant_id,
        "qr_token": table_token,
        "dish_id": dish_id,
    }


def test_public_flow_end_to_end(integration_client: TestClient, seeded_entities: dict[str, str]):
    qr_token = seeded_entities["qr_token"]
    dish_id = seeded_entities["dish_id"]

    menu_response = integration_client.get(f"/api/v1/public/{qr_token}/menu")
    assert menu_response.status_code == 200
    menu_body = menu_response.json()
    assert menu_body["restaurant"] == "Flow Test"
    assert len(menu_body["categories"]) == 1
    assert menu_body["categories"][0]["dishes"][0]["id"] == dish_id

    vote_response = integration_client.post(
        f"/api/v1/public/{qr_token}/votes",
        json={"dish_id": dish_id, "session_token": "session-1"},
    )
    assert vote_response.status_code == 200
    assert vote_response.json()["status"] == "recorded"

    repeated_vote_response = integration_client.post(
        f"/api/v1/public/{qr_token}/votes",
        json={"dish_id": dish_id, "session_token": "session-1"},
    )
    assert repeated_vote_response.status_code == 200
    assert repeated_vote_response.json()["status"] == "ignored"

    feedback_response = integration_client.post(
        f"/api/v1/public/{qr_token}/feedback",
        json={"rating": 5, "comment": "Great", "session_token": "session-1"},
    )
    assert feedback_response.status_code == 200
    assert feedback_response.json()["status"] == "received"

    ranking_response = integration_client.get(f"/api/v1/public/{qr_token}/ranking/today")
    assert ranking_response.status_code == 200
    ranking_body = ranking_response.json()
    assert len(ranking_body["ranking"]) == 1
    assert ranking_body["ranking"][0]["dish_id"] == dish_id
    assert ranking_body["ranking"][0]["votes"] == 1
