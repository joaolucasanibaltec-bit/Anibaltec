from pathlib import Path
import sys
import shutil

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "src"))

from reader import SGAReader
from converter import Converter
from xlsx_writer import XLSXWriter
from ibge_lookup import IBGELookup


class ConverterService:
    def __init__(self):
        self.reader = SGAReader()
        self.converter = Converter()
        self.writer = XLSXWriter()
        self.ibge = IBGELookup()

    def convert_products(self, sga_path: Path, template_path: Path, output_name: str) -> Path:
        df = self.reader.read(str(sga_path))
        df_conv = self.converter.convert_products(df)
        out_path = template_path.parent.parent / "uploads" / output_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.writer.write_products(df_conv, str(template_path), str(out_path))
        return out_path

    def convert_clients(
        self, client_path: Path, supplier_path: Path, template_path: Path,
        output_name: str, default_cep: str = "",
        handle_missing: str = "keep", fill_city: str = "", fill_uf: str = ""
    ) -> Path:
        df_cli = self.reader.read(str(client_path))
        df_sup = self.reader.read(str(supplier_path))
        df_conv = self.converter.convert_clients_suppliers_no_ibge(
            df_cli, df_sup, self.ibge, default_cep=default_cep,
            handle_missing=handle_missing, fill_city=fill_city, fill_uf=fill_uf
        )
        out_path = template_path.parent.parent / "uploads" / output_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.writer.write_clients(df_conv, str(template_path), str(out_path))
        return out_path
