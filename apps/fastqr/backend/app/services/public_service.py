import uuid
from collections import defaultdict
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.dish import Dish
from app.models.feedback import Feedback
from app.models.restaurant import Restaurant
from app.models.table import Table
from app.models.vote import Vote


def get_table_and_restaurant_by_qr(db: Session, qr_token: str) -> tuple[Table, Restaurant] | None:
    stmt = (
        select(Table, Restaurant)
        .join(Restaurant, Restaurant.id == Table.restaurant_id)
        .where(Table.qr_token == qr_token)
    )
    result = db.execute(stmt).first()
    if result is None:
        return None
    return result[0], result[1]


def get_menu_by_qr(db: Session, qr_token: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant

    categories_stmt = (
        select(Category)
        .where(Category.restaurant_id == restaurant.id)
        .order_by(Category.sort_order.asc(), Category.name.asc())
    )
    categories = db.execute(categories_stmt).scalars().all()

    dishes_stmt = (
        select(Dish)
        .where(Dish.restaurant_id == restaurant.id, Dish.is_active.is_(True))
        .order_by(Dish.name.asc())
    )
    dishes = db.execute(dishes_stmt).scalars().all()

    dishes_by_category: dict[uuid.UUID, list[Dish]] = defaultdict(list)
    for dish in dishes:
        dishes_by_category[dish.category_id].append(dish)

    response_categories: list[dict] = []
    for category in categories:
        response_categories.append(
            {
                "id": str(category.id),
                "name": category.name,
                "dishes": [
                    {
                        "id": str(dish.id),
                        "name": dish.name,
                        "description": dish.description,
                        "price_cents": dish.price_cents,
                    }
                    for dish in dishes_by_category.get(category.id, [])
                ],
            }
        )

    return {
        "restaurant": restaurant.name,
        "table": table.code,
        "categories": response_categories,
    }


def create_vote(db: Session, qr_token: str, dish_id: str, session_id: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant

    try:
        dish_uuid = uuid.UUID(dish_id)
    except ValueError:
        raise ValueError("Invalid dish_id format")

    dish_stmt = (
        select(Dish)
        .where(Dish.id == dish_uuid, Dish.restaurant_id == restaurant.id, Dish.is_active.is_(True))
    )
    dish = db.execute(dish_stmt).scalar_one_or_none()
    if dish is None:
        return {"error": "dish_not_found"}

    existing_stmt = select(Vote).where(
        Vote.restaurant_id == restaurant.id,
        Vote.dish_id == dish.id,
        Vote.session_id == session_id,
        Vote.vote_date == date.today(),
    )
    existing_vote = db.execute(existing_stmt).scalar_one_or_none()
    if existing_vote is not None:
        return {"status": "ignored", "reason": "already_voted_today", "dish_id": dish_id}

    vote = Vote(
        restaurant_id=restaurant.id,
        table_id=table.id,
        dish_id=dish.id,
        session_id=session_id,
        vote_date=date.today(),
    )
    db.add(vote)
    db.commit()

    return {"status": "recorded", "dish_id": dish_id, "vote_date": str(vote.vote_date)}


def create_feedback(db: Session, qr_token: str, rating: int, comment: str | None, session_id: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant

    feedback = Feedback(
        restaurant_id=restaurant.id,
        table_id=table.id,
        rating=rating,
        comment=comment,
        session_id=session_id,
    )
    db.add(feedback)
    db.commit()

    return {"status": "received", "rating": rating}


def get_today_ranking(db: Session, qr_token: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    _, restaurant = table_restaurant

    ranking_stmt = (
        select(Dish.id, Dish.name, func.count(Vote.id).label("votes"))
        .join(Vote, Vote.dish_id == Dish.id)
        .where(Vote.restaurant_id == restaurant.id, Vote.vote_date == date.today())
        .group_by(Dish.id, Dish.name)
        .order_by(func.count(Vote.id).desc(), Dish.name.asc())
        .limit(10)
    )

    ranking_rows = db.execute(ranking_stmt).all()

    return {
        "date": str(date.today()),
        "ranking": [
            {"dish_id": str(row.id), "dish_name": row.name, "votes": row.votes}
            for row in ranking_rows
        ],
    }
