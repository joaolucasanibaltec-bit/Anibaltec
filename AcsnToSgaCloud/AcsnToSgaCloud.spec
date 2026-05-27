# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

src_dir = os.getcwd()

a = Analysis(
    ["run.py"],
    pathex=[src_dir],
    binaries=[],
    datas=[
        (os.path.join(src_dir, "backend", "templates", "TEMPLATE MERCADORIAS.xlsx"), "backend/templates"),
        (os.path.join(src_dir, "backend", "templates", "TEMPLATE CLIENTES.xlsx"), "backend/templates"),
        (os.path.join(src_dir, "backend", "ibge_municipios.csv"), "backend"),
        (os.path.join(src_dir, "frontend", "dist", "index.html"), "frontend/dist"),
        (os.path.join(src_dir, "frontend", "dist", "favicon.svg"), "frontend/dist"),
        (os.path.join(src_dir, "frontend", "dist", "assets", "index-BKaThIzc.css"), "frontend/dist/assets"),
        (os.path.join(src_dir, "frontend", "dist", "assets", "index-BYSpKxo_.js"), "frontend/dist/assets"),
    ],
    hiddenimports=[
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.middleware",
        "uvicorn.middleware.proxy_headers",
        "uvicorn.middleware.asgi2",
        "uvicorn.middleware.wsgi",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "fastapi",
        "pydantic",
        "pandas",
        "openpyxl",
        "xlrd",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AcsnToSgaCloud",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
