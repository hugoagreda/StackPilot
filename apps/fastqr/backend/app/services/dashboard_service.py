from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.restaurant import Restaurant
from app.models.vote import Vote


def get_overview(db: Session, restaurant_slug: str | None = None) -> dict:
    if restaurant_slug:
        restaurant_stmt = select(Restaurant).where(Restaurant.slug == restaurant_slug)
    else:
        restaurant_stmt = select(Restaurant).order_by(Restaurant.created_at.asc())

    restaurant = db.execute(restaurant_stmt).scalars().first()
    if restaurant is None:
        return {
            "total_votes": 0,
            "unique_sessions": 0,
            "avg_rating": 0.0,
            "total_feedback": 0,
        }

    votes_stmt = select(func.count(Vote.id)).where(Vote.restaurant_id == restaurant.id)
    unique_sessions_stmt = select(func.count(distinct(Vote.session_id))).where(
        Vote.restaurant_id == restaurant.id
    )
    feedback_count_stmt = select(func.count(Feedback.id)).where(Feedback.restaurant_id == restaurant.id)
    avg_rating_stmt = select(func.avg(Feedback.rating)).where(Feedback.restaurant_id == restaurant.id)

    total_votes = db.execute(votes_stmt).scalar_one() or 0
    unique_sessions = db.execute(unique_sessions_stmt).scalar_one() or 0
    total_feedback = db.execute(feedback_count_stmt).scalar_one() or 0
    avg_rating_raw = db.execute(avg_rating_stmt).scalar_one()

    return {
        "total_votes": int(total_votes),
        "unique_sessions": int(unique_sessions),
        "avg_rating": float(avg_rating_raw) if avg_rating_raw is not None else 0.0,
        "total_feedback": int(total_feedback),
    }
