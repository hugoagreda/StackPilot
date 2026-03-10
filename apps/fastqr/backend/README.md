# FastQR Backend (FastAPI)

MVP-oriented modular structure:
- `routes/`: HTTP layer
- `services/`: business rules
- `models/`: SQLAlchemy entities
- `schemas/`: Pydantic DTOs
- `utils/`: helpers (QR, time, security)
