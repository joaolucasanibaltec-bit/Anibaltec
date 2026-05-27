import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

router = APIRouter()

BASE = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE / "templates"
UPLOADS_DIR = BASE / "uploads"
OUTPUT_DIR = BASE / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

from backend.services.converter_service import ConverterService

def _save_upload(file: UploadFile) -> Path:
    import uuid
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest = UPLOADS_DIR / safe_name
    content = file.file.read()
    dest.write_bytes(content)
    return dest

def _get_template(name: str) -> Path:
    path = TEMPLATES_DIR / name
    if not path.exists():
        templates = [f.name for f in TEMPLATES_DIR.iterdir() if f.suffix in (".xlsx", ".xls")]
        raise HTTPException(404, f"Template '{name}' não encontrado. Disponíveis: {', '.join(templates)}")
    return path

@router.post("/convert/products")
async def convert_products(
    acsn_file: UploadFile = File(...),
    template_name: str = Form("TEMPLATE MERCADORIAS.xlsx"),
    output_name: str = Form("MERCADORIAS_SGACLOUD.xlsx"),
):
    acsn_path = None
    try:
        acsn_path = _save_upload(acsn_file)
        template_path = _get_template(template_name)
        svc = ConverterService()
        out_path = svc.convert_products(acsn_path, template_path, output_name)
        return FileResponse(
            out_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro na conversão de produtos: {str(e)}")
    finally:
        if acsn_path:
            acsn_path.unlink(missing_ok=True)

@router.post("/validate/clients")
async def validate_clients(
    client_file: UploadFile = File(...),
    supplier_file: UploadFile = File(None),
):
    client_path = None
    supplier_path = None
    try:
        client_path = _save_upload(client_file)
        supplier_path = _save_upload(supplier_file) if supplier_file and supplier_file.filename else None
        svc = ConverterService()
        issues = svc.analyze_clients(client_path, supplier_path)
        return issues
    except Exception as e:
        raise HTTPException(500, f"Erro na validação: {str(e)}")
    finally:
        if client_path:
            client_path.unlink(missing_ok=True)
        if supplier_path:
            supplier_path.unlink(missing_ok=True)

@router.post("/convert/clients")
async def convert_clients(
    client_file: UploadFile = File(...),
    supplier_file: UploadFile = File(None),
    template_name: str = Form("TEMPLATE CLIENTES.xlsx"),
    output_name: str = Form("CLIENTE_FORNECEDOR_SGACLOUD.xlsx"),
    default_cep: str = Form(""),
    default_city: str = Form(""),
    default_state: str = Form(""),
    exclude_missing_city: str = Form("false"),
):
    client_path = None
    supplier_path = None
    try:
        client_path = _save_upload(client_file)
        if supplier_file and supplier_file.filename:
            supplier_path = _save_upload(supplier_file)
        template_path = _get_template(template_name)
        svc = ConverterService()
        fixes = {
            "default_cep": default_cep.strip(),
            "default_city": default_city.strip(),
            "default_state": default_state.strip(),
            "exclude_missing_city": exclude_missing_city.lower() == "true",
        }
        out_path = svc.convert_clients(client_path, template_path, output_name, supplier_path, fixes)
        return FileResponse(
            out_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro na conversão de clientes: {str(e)}")
    finally:
        if client_path:
            client_path.unlink(missing_ok=True)
        if supplier_path:
            supplier_path.unlink(missing_ok=True)

@router.post("/convert/both")
async def convert_both(
    products_file: UploadFile = File(...),
    client_file: UploadFile = File(...),
    supplier_file: UploadFile = File(None),
):
    prod_path = None
    client_path = None
    supplier_path = None
    try:
        prod_path = _save_upload(products_file)
        client_path = _save_upload(client_file)
        if supplier_file and supplier_file.filename:
            supplier_path = _save_upload(supplier_file)

        prod_template = _get_template("TEMPLATE MERCADORIAS.xlsx")
        cli_template = _get_template("TEMPLATE CLIENTES.xlsx")

        svc = ConverterService()
        results = {}

        prod_out = svc.convert_products(prod_path, prod_template, "MERCADORIAS_SGACLOUD.xlsx")
        results["products"] = prod_out.name

        cli_out = svc.convert_clients(client_path, cli_template, "CLIENTE_FORNECEDOR_SGACLOUD.xlsx", supplier_path)
        results["clients"] = cli_out.name

        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro na conversão: {str(e)}")
    finally:
        for p in [prod_path, client_path, supplier_path]:
            if p:
                p.unlink(missing_ok=True)
