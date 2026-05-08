from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os
import uuid

from backend.services.converter_service import ConverterService

router = APIRouter()
BASE = Path(__file__).resolve().parent.parent.parent
UPLOADS = BASE / "backend" / "uploads"
TEMPLATES = BASE / "backend" / "templates"

UPLOADS.mkdir(parents=True, exist_ok=True)
TEMPLATES.mkdir(parents=True, exist_ok=True)


def _save_upload(file: UploadFile) -> Path:
    dest = UPLOADS / f"{uuid.uuid4().hex}_{file.filename}"
    with open(dest, "wb") as f:
        f.write(file.file.read())
    return dest


def _get_template(filename: str = "") -> Path:
    if filename:
        t = TEMPLATES / filename
        if t.exists():
            return t
    return None


@router.post("/convert/products")
async def convert_products(
    sga_file: UploadFile = File(...),
    template_name: str = Form("TEMPLATE MERCADORIAS.xlsx"),
    output_name: str = Form("MERCADORIAS_SGACLOUD.xlsx"),
):
    sga_path = _save_upload(sga_file)
    template_path = _get_template(template_name)
    if not template_path:
        raise HTTPException(400, f"Template {template_name} n\u00e3o encontrado no servidor")

    try:
        svc = ConverterService()
        out_path = svc.convert_products(sga_path, template_path, output_name)
        return FileResponse(
            out_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_name,
        )
    except Exception as e:
        raise HTTPException(500, f"Erro na convers\u00e3o: {str(e)}")
    finally:
        sga_path.unlink(missing_ok=True)


@router.post("/convert/clients")
async def convert_clients(
    client_file: UploadFile = File(...),
    supplier_file: UploadFile = File(...),
    template_name: str = Form("TEMPLATE CLIENTES.xlsx"),
    output_name: str = Form("CLIENTES_SGACLOUD.xlsx"),
    default_cep: str = Form(""),
    handle_missing: str = Form("keep"),
    fill_city: str = Form(""),
    fill_uf: str = Form(""),
):
    client_path = _save_upload(client_file)
    supplier_path = _save_upload(supplier_file)
    template_path = _get_template(template_name)
    if not template_path:
        raise HTTPException(400, f"Template {template_name} n\u00e3o encontrado no servidor")

    try:
        svc = ConverterService()
        out_path = svc.convert_clients(
            client_path, supplier_path, template_path, output_name,
            default_cep, handle_missing, fill_city, fill_uf
        )
        return FileResponse(
            out_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_name,
        )
    except Exception as e:
        raise HTTPException(500, f"Erro na convers\u00e3o: {str(e)}")
    finally:
        client_path.unlink(missing_ok=True)
        supplier_path.unlink(missing_ok=True)


@router.post("/convert/both")
async def convert_both(
    product_file: UploadFile = File(...),
    product_template: str = Form("TEMPLATE MERCADORIAS.xlsx"),
    client_file: UploadFile = File(...),
    supplier_file: UploadFile = File(...),
    client_template: str = Form("TEMPLATE CLIENTES.xlsx"),
    default_cep: str = Form(""),
    handle_missing: str = Form("keep"),
    fill_city: str = Form(""),
    fill_uf: str = Form(""),
):
    prod_path = _save_upload(product_file)
    cli_path = _save_upload(client_file)
    sup_path = _save_upload(supplier_file)
    prod_tpl = _get_template(product_template)
    cli_tpl = _get_template(client_template)

    if not prod_tpl:
        raise HTTPException(400, f"Template {product_template} n\u00e3o encontrado")
    if not cli_tpl:
        raise HTTPException(400, f"Template {client_template} n\u00e3o encontrado")

    prod_out = f"MERCADORIAS_{uuid.uuid4().hex[:8]}.xlsx"
    cli_out = f"CLIENTES_{uuid.uuid4().hex[:8]}.xlsx"

    try:
        svc = ConverterService()
        prod_result = svc.convert_products(prod_path, prod_tpl, prod_out)
        cli_result = svc.convert_clients(
            cli_path, sup_path, cli_tpl, cli_out,
            default_cep, handle_missing, fill_city, fill_uf
        )

        return {
            "products": {"filename": prod_out, "url": f"/api/download/{prod_out}"},
            "clients": {"filename": cli_out, "url": f"/api/download/{cli_out}"},
        }
    except Exception as e:
        raise HTTPException(500, f"Erro: {str(e)}")
    finally:
        prod_path.unlink(missing_ok=True)
        cli_path.unlink(missing_ok=True)
        sup_path.unlink(missing_ok=True)
