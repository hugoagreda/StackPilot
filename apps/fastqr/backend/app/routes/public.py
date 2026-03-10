from fastapi import APIRouter

router = APIRouter(prefix="/public")


@router.get("/{qr_token}/menu")
def get_public_menu(qr_token: str) -> dict:
    return {
        "qr_token": qr_token,
        "restaurant": "Demo Restaurant",
        "table": "T1",
        "categories": [],
    }


@router.post("/{qr_token}/votes")
def vote_dish(qr_token: str, payload: dict) -> dict:
    return {"qr_token": qr_token, "status": "recorded", "payload": payload}


@router.post("/{qr_token}/feedback")
def create_feedback(qr_token: str, payload: dict) -> dict:
    return {"qr_token": qr_token, "status": "received", "payload": payload}


@router.get("/{qr_token}/ranking/today")
def get_today_ranking(qr_token: str) -> dict:
    return {"qr_token": qr_token, "date": "today", "ranking": []}
