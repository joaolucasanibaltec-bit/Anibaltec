from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

router = APIRouter()
BASE = Path(__file__).resolve().parent.parent.parent
UPLOADS = BASE / "backend" / "uploads"
TEMPLATES = BASE / "backend" / "templates"
ALLOWED_CSV = {".csv"}
ALLOWED_XLSX = {".xlsx"}
MAX_SIZE = 50 * 1024 * 1024

UPLOADS.mkdir(parents=True, exist_ok=True)


@router.get("/templates")
def list_templates():
    if not TEMPLATES.exists():
        return {"templates": []}
    files = []
    for f in sorted(TEMPLATES.iterdir()):
        if f.suffix in ALLOWED_XLSX:
            files.append({"name": f.name, "size": f.stat().st_size})
    return {"templates": files}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_CSV and ext not in ALLOWED_XLSX:
        raise HTTPException(400, "Formato inv\u00e1lido. Aceitos: .csv, .xlsx")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "Arquivo muito grande. M\u00e1ximo: 50MB")

    dest = UPLOADS / file.filename
    with open(dest, "wb") as f:
        f.write(content)

    return {"filename": file.filename, "type": "csv" if ext == ".csv" else "xlsx", "size": len(content)}
