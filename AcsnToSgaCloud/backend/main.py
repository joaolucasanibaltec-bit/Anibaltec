from pathlib import Path
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

if getattr(sys, "frozen", False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE))

from backend.routes.files import router as files_router
from backend.routes.convert import router as convert_router

app = FastAPI(title="Conversor ACSN \u2192 SgaCloud", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files_router, prefix="/api")
app.include_router(convert_router, prefix="/api")

frontend_dist = BASE / "frontend" / "dist"
if frontend_dist.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(frontend_dist / "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.is_file() and file_path.suffix in (
            ".html", ".js", ".css", ".svg", ".png", ".ico", ".json", ".woff", ".woff2", ".ttf",
        ):
            return FileResponse(str(file_path))
        index = frontend_dist / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"detail": "Not Found"}
