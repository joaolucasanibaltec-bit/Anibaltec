import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

router = APIRouter()

BASE = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE / "templates"
UPLOADS_DIR = BASE / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

@router.get("/templates")
async def list_templates():
    templates = []
    for f in sorted(TEMPLATES_DIR.iterdir()):
        if f.suffix in (".xlsx", ".xls"):
            templates.append({"name": f.name, "size": f.stat().st_size})
    return {"templates": templates}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".xls", ".xlsx")):
        raise HTTPException(400, "Formato inválido. Envie arquivos .XLS ou .XLSX")

    import uuid
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest = UPLOADS_DIR / safe_name

    content = await file.read()
    dest.write_bytes(content)

    return {"filename": safe_name, "original_name": file.filename, "size": len(content)}

@router.get("/download/{filename:path}")
async def download_file(filename: str):
    filepath = UPLOADS_DIR / filename
    if not filepath.exists():
        filepath = BASE / "output" / filename
    if not filepath.exists():
        raise HTTPException(404, "Arquivo não encontrado")
    return FileResponse(filepath, filename=filepath.name)
