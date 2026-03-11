"""
app/utils/common.py — Utilidades y enumeraciones compartidas en todo el backend.

Por qué existe este módulo:
- Centralizar helpers reutilizables evita que cada servicio defina su propia copia
  de la misma lógica (DRY: Don't Repeat Yourself).
- Los Enums con StrEnum garantizan que los valores de estado se escriban igual
  en toda la aplicación; un typo en "reedeemed" vs "redeemed" genera un bug
  silencioso que los strings normales nunca capturarían.
- Al colocar Enums y helpers en un único archivo de utilidades primitivas evitamos
  crear múltiples archivos de 5-10 líneas que dispersan el contexto (principio
  de cohesión: juntar lo que cambia por la misma razón).
"""

import uuid
from enum import StrEnum


# ---------------------------------------------------------------------------
# Enumeraciones de dominio
# ---------------------------------------------------------------------------

class RewardStatus(StrEnum):
    """
    Estados posibles de un premio en una sesión de juego.
    Usar este Enum en lugar de strings literales garantiza consistencia:
    si el valor cambia, el error aparece en tiempo de importación, no en runtime.
    """
    ISSUED = "issued"            # Premio generado, pendiente de canjear
    REDEEMED = "redeemed"        # Premio ya canjeado por el cliente
    NOT_REDEEMABLE = "not_redeemable"  # El resultado no tiene premio


class GameType(StrEnum):
    """
    Tipos de juego disponibles en FastQR.
    Centralizar aquí facilita añadir nuevos juegos sin buscar strings dispersos.
    """
    SPIN_WHEEL = "spin_wheel"


# ---------------------------------------------------------------------------
# Helpers de parsing y normalización
# ---------------------------------------------------------------------------

def parse_uuid(raw_value: str, field_name: str) -> uuid.UUID:
    """
    Convierte un string a UUID con un mensaje de error descriptivo.

    Por qué existe: SQLAlchemy espera uuid.UUID, no strings. Centralizar
    esta conversión evita bloques try/except duplicados en cada servicio.
    """
    try:
        return uuid.UUID(raw_value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} format") from exc


def normalize_session_token(session_token: str) -> str:
    """
    Elimina espacios y rechaza session tokens en blanco.

    Por qué existe: los session tokens vienen del cliente (dispositivo móvil)
    y pueden incluir espacios accidentales. Rechazar blancos aquí previene
    que registros con token vacío contaminen la base de datos.
    """
    normalized = session_token.strip()
    if not normalized:
        raise ValueError("Invalid session_token")
    return normalized
