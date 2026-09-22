import os
import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.database import Database
from backend.import_service import ImportService
from backend.exceptions import ImportValidationError

DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/transactions.db")

app = FastAPI(title="Transaction review")

# PoC-only: wide open CORS so the Vite dev server (port 5173) can call the
# API (port 8000) regardless of how the two are hosted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_db = Database(DATABASE_PATH)
_db.init_db()


class ImportRequest(BaseModel):
    csv: str


def get_database() -> Database:
    return _db


def get_import_service() -> ImportService:
    return ImportService()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/imports", status_code=201)
def import_csv(
    payload: ImportRequest,
    service: ImportService = Depends(get_import_service),
    db: Database = Depends(get_database),
):
    try:
        result = service.evaluate(payload.csv)
    except ImportValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    record = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        **result,
    }
    db.save_import(record)
    return record


@app.get("/api/imports")
def list_imports(db: Database = Depends(get_database)):
    return db.list_imports()


@app.get("/api/imports/{import_id}")
def get_import(import_id: str, db: Database = Depends(get_database)):
    record = db.get_import(import_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Import not found")
    return record
