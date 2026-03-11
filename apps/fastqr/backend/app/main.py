from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.routes.public import router as public_router

app = FastAPI(title="FastQR API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(public_router, prefix="/api/v1", tags=["public"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastQR API running"}
