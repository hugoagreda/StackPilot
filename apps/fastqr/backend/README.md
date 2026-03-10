# FastQR Backend (FastAPI)

MVP-oriented modular structure:
- `routes/`: HTTP layer
- `services/`: business rules
- `models/`: SQLAlchemy entities
- `schemas/`: Pydantic DTOs
- `utils/`: helpers (QR, time, security)

## Checkpoint tests

Run from `apps/fastqr/backend`:

```bash
pip install -r requirements.txt
pytest -q
```

Current checkpoint suite validates:
- app root and health endpoints
- public menu, votes, feedback, and ranking route behavior
- dashboard overview route behavior
