import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.public import router as public_router

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CORS origins
# ---------------------------------------------------------------------------
# Buena práctica: leer las origins desde variable de entorno en lugar de
# hardcodearlas. Así el mismo código sirve en local, staging y producción
# sin modificar archivos. En local funciona con el fallback de desarrollo.
_cors_origins_raw = os.getenv("FASTQR_CORS_ORIGINS", "")
_CORS_ORIGINS: list[str] = (
    [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]
    if _cors_origins_raw
    else [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
)
if _cors_origins_raw:
    logger.info("CORS origins loaded from FASTQR_CORS_ORIGINS: %s", _CORS_ORIGINS)
else:
    logger.debug("CORS origins using development defaults")

app = FastAPI(title="FastQR API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router, prefix="/api/v1", tags=["public"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])


# ---------------------------------------------------------------------------
# Rutas raíz e infraestructura
# ---------------------------------------------------------------------------
# El endpoint /health vive aquí y no en su propio archivo porque es una
# función de una sola línea sin lógica de negocio. Crear un módulo separado
# para 7 líneas añade fricción de navegación sin ningún beneficio.
@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastQR API running"}
