import uuid
import secrets
from datetime import date, datetime, timezone

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.game_reward_rule import GameRewardRule
from app.models.game_session import GameSession
from app.services.public_service import _get_restaurant_feature_settings, get_table_and_restaurant_by_qr

REWARDS = [
    {"label": "No Prize", "weight": 45, "redeemable": False},
    {"label": "5% OFF", "weight": 30, "redeemable": True},
    {"label": "Free Drink", "weight": 18, "redeemable": True},
    {"label": "Free Dessert", "weight": 7, "redeemable": True},
]


def _normalize_session_token(session_token: str) -> str:
    normalized = session_token.strip()
    if not normalized:
        raise ValueError("Invalid session_token")
    return normalized


def _build_default_rules() -> list[dict]:
    return [dict(item, is_active=True) for item in REWARDS]


def _get_rules_for_today(db: Session, restaurant_id: uuid.UUID) -> list[dict]:
    today = date.today()
    rules_stmt = (
        select(GameRewardRule)
        .where(GameRewardRule.restaurant_id == restaurant_id, GameRewardRule.rule_date == today)
        .order_by(GameRewardRule.weight.desc(), GameRewardRule.label.asc())
    )
    rules = db.execute(rules_stmt).scalars().all()
    if not rules:
        return _build_default_rules()
    return [
        {
            "label": item.label,
            "weight": item.weight,
            "redeemable": item.redeemable,
            "is_active": item.is_active,
        }
        for item in rules
    ]


def _pick_reward(rules: list[dict]) -> dict:
    active_rules = [item for item in rules if item.get("is_active", True) and item.get("weight", 0) > 0]
    if not active_rules:
        active_rules = _build_default_rules()

    total_weight = sum(item["weight"] for item in active_rules)
    roll = secrets.randbelow(total_weight) + 1
    current = 0
    for reward in active_rules:
        current += reward["weight"]
        if roll <= current:
            return reward
    return active_rules[0]


def _parse_uuid(raw_value: str, field_name: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw_value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} format") from exc


def spin_wheel(db: Session, qr_token: str, session_token: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant
    settings = _get_restaurant_feature_settings(db, restaurant.id)
    if not settings["allow_games"]:
        return {"error": "feature_disabled", "feature": "games"}

    normalized_session_token = _normalize_session_token(session_token)
    today = date.today()

    existing_stmt = select(GameSession).where(
        GameSession.restaurant_id == restaurant.id,
        GameSession.session_token == normalized_session_token,
        GameSession.game_type == "spin_wheel",
        GameSession.played_date == today,
    )
    existing_session = db.execute(existing_stmt).scalar_one_or_none()
    if existing_session is not None:
        return {
            "status": "ignored",
            "session_token": normalized_session_token,
            "reward_label": existing_session.reward_label,
            "reward_code": existing_session.reward_code,
            "reward_status": existing_session.reward_status,
        }

    reward_rules = _get_rules_for_today(db, restaurant.id)
    reward = _pick_reward(reward_rules)
    reward_code = secrets.token_urlsafe(8).upper() if reward["redeemable"] else None
    reward_status = "issued" if reward["redeemable"] else "not_redeemable"

    game_session = GameSession(
        restaurant_id=restaurant.id,
        table_id=table.id,
        session_token=normalized_session_token,
        game_type="spin_wheel",
        played_date=today,
        reward_code=reward_code,
        reward_label=reward["label"],
        reward_status=reward_status,
    )
    db.add(game_session)
    db.commit()

    return {
        "status": "recorded",
        "session_token": normalized_session_token,
        "reward_label": reward["label"],
        "reward_code": reward_code,
        "reward_status": reward_status,
    }


def get_today_game_settings(db: Session, restaurant_id: str) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    rules = _get_rules_for_today(db, restaurant_uuid)
    return {
        "date": str(date.today()),
        "rules": rules,
    }


def update_today_game_settings(db: Session, restaurant_id: str, rules: list[dict]) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    today = date.today()

    if not rules:
        raise ValueError("At least one rule is required")

    active_weight = sum(rule["weight"] for rule in rules if rule.get("is_active", True) and rule["weight"] > 0)
    if active_weight <= 0:
        raise ValueError("Active rules must have positive weight")

    delete_stmt = select(GameRewardRule).where(
        GameRewardRule.restaurant_id == restaurant_uuid,
        GameRewardRule.rule_date == today,
    )
    existing_rules = db.execute(delete_stmt).scalars().all()
    for item in existing_rules:
        db.delete(item)

    for rule in rules:
        label = rule["label"].strip()
        if not label:
            raise ValueError("Rule label cannot be empty")
        db.add(
            GameRewardRule(
                restaurant_id=restaurant_uuid,
                rule_date=today,
                label=label,
                weight=rule["weight"],
                redeemable=rule["redeemable"],
                is_active=rule.get("is_active", True),
            )
        )

    db.commit()
    return get_today_game_settings(db, restaurant_id)


def list_rewards_today(db: Session, restaurant_id: str) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    today = date.today()
    stmt = (
        select(GameSession)
        .where(GameSession.restaurant_id == restaurant_uuid, GameSession.played_date == today)
        .order_by(GameSession.created_at.desc())
    )
    rows = db.execute(stmt).scalars().all()
    return {
        "date": str(today),
        "items": [
            {
                "reward_code": row.reward_code,
                "reward_label": row.reward_label,
                "reward_status": row.reward_status,
                "session_token": row.session_token,
                "table_id": str(row.table_id),
                "created_at": row.created_at.isoformat() if row.created_at else "",
            }
            for row in rows
        ],
    }


def get_session_reward(db: Session, qr_token: str, session_token: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    _, restaurant = table_restaurant
    settings = _get_restaurant_feature_settings(db, restaurant.id)
    if not settings["allow_games"]:
        return {"error": "feature_disabled", "feature": "games"}

    normalized_session_token = _normalize_session_token(session_token)

    stmt = (
        select(GameSession)
        .where(
            GameSession.restaurant_id == restaurant.id,
            GameSession.session_token == normalized_session_token,
            GameSession.game_type == "spin_wheel",
        )
        .order_by(GameSession.created_at.desc())
    )
    game_session = db.execute(stmt).scalar_one_or_none()
    if game_session is None:
        return {
            "error": "reward_not_found",
        }

    return {
        "session_token": normalized_session_token,
        "reward_label": game_session.reward_label,
        "reward_code": game_session.reward_code,
        "reward_status": game_session.reward_status,
    }


def get_games_analytics(db: Session, restaurant_id: str) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    total_spins_stmt = select(func.count(GameSession.id)).where(GameSession.restaurant_id == restaurant_uuid)
    unique_sessions_stmt = select(func.count(distinct(GameSession.session_token))).where(
        GameSession.restaurant_id == restaurant_uuid
    )
    issued_rewards_stmt = select(func.count(GameSession.id)).where(
        GameSession.restaurant_id == restaurant_uuid,
        GameSession.reward_status.in_(["issued", "redeemed"]),
    )
    redeemed_rewards_stmt = select(func.count(GameSession.id)).where(
        GameSession.restaurant_id == restaurant_uuid,
        GameSession.reward_status == "redeemed",
    )

    total_spins = int(db.execute(total_spins_stmt).scalar_one() or 0)
    unique_sessions = int(db.execute(unique_sessions_stmt).scalar_one() or 0)
    issued_rewards = int(db.execute(issued_rewards_stmt).scalar_one() or 0)
    redeemed_rewards = int(db.execute(redeemed_rewards_stmt).scalar_one() or 0)

    redemption_rate = 0.0
    if issued_rewards > 0:
        redemption_rate = redeemed_rewards / issued_rewards

    return {
        "total_spins": total_spins,
        "unique_sessions": unique_sessions,
        "issued_rewards": issued_rewards,
        "redeemed_rewards": redeemed_rewards,
        "redemption_rate": float(redemption_rate),
    }


def redeem_reward(db: Session, restaurant_id: str, reward_code: str) -> dict | None:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    normalized_code = reward_code.strip().upper()
    if not normalized_code:
        raise ValueError("Invalid reward_code")

    stmt = select(GameSession).where(
        GameSession.restaurant_id == restaurant_uuid,
        GameSession.reward_code == normalized_code,
    )
    game_session = db.execute(stmt).scalar_one_or_none()
    if game_session is None:
        return None

    if game_session.reward_status == "not_redeemable":
        raise ValueError("Reward is not redeemable")

    if game_session.reward_status == "redeemed":
        return {
            "reward_code": normalized_code,
            "reward_status": "redeemed",
        }

    game_session.reward_status = "redeemed"
    game_session.redeemed_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "reward_code": normalized_code,
        "reward_status": "redeemed",
    }
