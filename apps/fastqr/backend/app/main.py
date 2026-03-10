from fastapi import FastAPI

from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.routes.public import router as public_router

app = FastAPI(title="FastQR API", version="0.1.0")

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(public_router, prefix="/api/v1", tags=["public"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastQR API running"}
