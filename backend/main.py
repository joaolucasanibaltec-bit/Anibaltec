import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from backend.routes import files, convert

app = FastAPI(title="SGA \u2192 SGAcloud Converter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api")
app.include_router(convert.router, prefix="/api")

app.mount("/api/download", StaticFiles(directory=str(BASE / "backend" / "uploads")), name="download")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


FRONTEND_DIST = BASE / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    from starlette.middleware.base import BaseHTTPMiddleware

    class FrontendMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            path = request.url.path
            if path.startswith("/api/") or path.startswith("/assets/"):
                return await call_next(request)
            file_path = FRONTEND_DIST / path.lstrip("/") if path != "/" else FRONTEND_DIST / "index.html"
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(FRONTEND_DIST / "index.html"))

    app.add_middleware(FrontendMiddleware)
