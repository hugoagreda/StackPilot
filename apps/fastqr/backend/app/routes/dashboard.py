from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.analytics import OverviewResponse
from app.schemas.dashboard import (
    CategoryCreateRequest,
    CategoryResponse,
    DishCreateRequest,
    DishResponse,
    DishUpdateRequest,
    TableCreateRequest,
    TableResponse,
)
from app.schemas.game import GamesAnalyticsResponse, RewardRedeemResponse
from app.schemas.game import GameSettingsTodayResponse, GameSettingsTodayUpdateRequest, RewardsTodayResponse
from app.schemas.scoring import (
    DishScoreBonusRequest,
    DishScoresTodayResponse,
    ScoringSettingsResponse,
    ScoringSettingsUpdateRequest,
)
from app.services.dashboard_service import (
    create_category,
    create_dish,
    create_table,
    get_overview,
    get_overview_by_restaurant_id,
    get_scoring_settings,
    list_categories,
    list_dishes,
    list_tables,
    set_dish_score_bonus_today,
    update_scoring_settings,
    update_dish,
)
from app.services.game_service import (
    get_games_analytics,
    get_today_game_settings,
    list_rewards_today,
    redeem_reward,
    update_today_game_settings,
)
from app.services.public_service import get_today_ranking_by_restaurant_id
from app.utils.auth import CurrentAuth, get_current_auth

router = APIRouter(prefix="/dashboard")


def _enforce_restaurant_scope(path_restaurant_id: str, current_auth: CurrentAuth) -> None:
    if path_restaurant_id != current_auth.restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden restaurant scope")


def _dish_to_response(dish) -> DishResponse:
    return DishResponse(
        id=str(dish.id),
        restaurant_id=str(dish.restaurant_id),
        category_id=str(dish.category_id),
        name=dish.name,
        description=dish.description,
        price_cents=dish.price_cents,
        image_url=dish.image_url,
        is_available=dish.is_available,
    )


@router.get("/overview")
def get_dashboard_overview(
    restaurant_slug: str | None = None,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> OverviewResponse:
    overview = get_overview(db, restaurant_slug)
    return OverviewResponse(**overview)


@router.get("/restaurants/{restaurant_id}/overview")
def get_restaurant_overview(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> OverviewResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        overview = get_overview_by_restaurant_id(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return OverviewResponse(**overview)


@router.get("/restaurants/{restaurant_id}/categories")
def get_restaurant_categories(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> list[CategoryResponse]:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    categories = list_categories(db, restaurant_id)
    return [CategoryResponse(id=str(c.id), name=c.name) for c in categories]


@router.post("/restaurants/{restaurant_id}/categories")
def post_restaurant_category(
    restaurant_id: str,
    payload: CategoryCreateRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> CategoryResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        category = create_category(db, restaurant_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CategoryResponse(id=str(category.id), name=category.name)


@router.get("/restaurants/{restaurant_id}/tables")
def get_restaurant_tables(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> list[TableResponse]:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        tables = list_tables(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [
        TableResponse(
            id=str(table.id),
            restaurant_id=str(table.restaurant_id),
            code=table.code,
            qr_token=table.qr_token,
            is_enabled=table.is_enabled,
            scan_cooldown_minutes=table.scan_cooldown_minutes,
        )
        for table in tables
    ]


@router.post("/restaurants/{restaurant_id}/tables")
def post_restaurant_table(
    restaurant_id: str,
    payload: TableCreateRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> TableResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        table = create_table(db, restaurant_id, payload.code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TableResponse(
        id=str(table.id),
        restaurant_id=str(table.restaurant_id),
        code=table.code,
        qr_token=table.qr_token,
        is_enabled=table.is_enabled,
        scan_cooldown_minutes=table.scan_cooldown_minutes,
    )


@router.get("/restaurants/{restaurant_id}/dishes")
def get_restaurant_dishes(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> list[DishResponse]:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        dishes = list_dishes(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [_dish_to_response(dish) for dish in dishes]


@router.post("/restaurants/{restaurant_id}/dishes")
def post_restaurant_dish(
    restaurant_id: str,
    payload: DishCreateRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> DishResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        dish = create_dish(
            db,
            restaurant_id,
            payload.category_id,
            payload.name,
            payload.description,
            payload.price_cents,
            payload.image_url,
            payload.is_available,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _dish_to_response(dish)


@router.patch("/restaurants/{restaurant_id}/dishes/{dish_id}")
def patch_restaurant_dish(
    restaurant_id: str,
    dish_id: str,
    payload: DishUpdateRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> DishResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        dish = update_dish(
            db,
            restaurant_id,
            dish_id,
            payload.category_id,
            payload.name,
            payload.description,
            payload.price_cents,
            payload.image_url,
            payload.is_available,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")

    return _dish_to_response(dish)


@router.get("/restaurants/{restaurant_id}/games/analytics")
def get_restaurant_games_analytics(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> GamesAnalyticsResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    analytics = get_games_analytics(db, restaurant_id)
    return GamesAnalyticsResponse(**analytics)


@router.patch("/restaurants/{restaurant_id}/rewards/{reward_code}/redeem")
def patch_redeem_reward(
    restaurant_id: str,
    reward_code: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> RewardRedeemResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        reward = redeem_reward(db, restaurant_id, reward_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if reward is None:
        raise HTTPException(status_code=404, detail="Reward not found")

    return RewardRedeemResponse(**reward)


@router.get("/restaurants/{restaurant_id}/games/settings/today")
def get_restaurant_game_settings_today(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> GameSettingsTodayResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        settings = get_today_game_settings(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return GameSettingsTodayResponse(**settings)


@router.put("/restaurants/{restaurant_id}/games/settings/today")
def put_restaurant_game_settings_today(
    restaurant_id: str,
    payload: GameSettingsTodayUpdateRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> GameSettingsTodayResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        settings = update_today_game_settings(
            db,
            restaurant_id,
            [item.model_dump() for item in payload.rules],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return GameSettingsTodayResponse(**settings)


@router.get("/restaurants/{restaurant_id}/rewards/today")
def get_restaurant_rewards_today(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> RewardsTodayResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        rewards = list_rewards_today(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RewardsTodayResponse(**rewards)


@router.get("/restaurants/{restaurant_id}/scoring/settings")
def get_restaurant_scoring_settings(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> ScoringSettingsResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        settings = get_scoring_settings(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ScoringSettingsResponse(**settings)


@router.patch("/restaurants/{restaurant_id}/scoring/settings")
def patch_restaurant_scoring_settings(
    restaurant_id: str,
    payload: ScoringSettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> ScoringSettingsResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        settings = update_scoring_settings(db, restaurant_id, payload.vote_points)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ScoringSettingsResponse(**settings)


@router.patch("/restaurants/{restaurant_id}/dishes/{dish_id}/score/today")
def patch_dish_score_bonus_today(
    restaurant_id: str,
    dish_id: str,
    payload: DishScoreBonusRequest,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> dict:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        result = set_dish_score_bonus_today(db, restaurant_id, dish_id, payload.bonus_points)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return result


@router.get("/restaurants/{restaurant_id}/dishes/scores/today")
def get_dishes_scores_today(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> DishScoresTodayResponse:
    _enforce_restaurant_scope(restaurant_id, current_auth)
    try:
        ranking = get_today_ranking_by_restaurant_id(db, restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DishScoresTodayResponse(**ranking)
