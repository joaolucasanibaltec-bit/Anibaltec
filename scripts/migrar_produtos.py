import pandas as pd
import xlrd
import os
from pathlib import Path
from datetime import datetime

ACSN_DIR = Path("DadosACSN")
SGACLOUD_DIR = Path("SgaCloud")
OUTPUT_DIR = SGACLOUD_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def ler_dados_acsn():
    """Lê os dados reais dos produtos do ACSN"""
    book = xlrd.open_workbook(ACSN_DIR / "PRODUTOS.XLS", encoding_override='latin1')
    sheet = book.sheet_by_index(0)

    headers = [sheet.cell_value(0, j) for j in range(sheet.ncols)]
    dados = []

    for i in range(1, sheet.nrows):
        row = {}
        for j, header in enumerate(headers):
            cell = sheet.cell(i, j)
            if cell.ctype == xlrd.XL_CELL_EMPTY:
                row[header] = None
            elif cell.ctype == xlrd.XL_CELL_TEXT:
                row[header] = sheet.cell_value(i, j).strip()
            else:
                row[header] = sheet.cell_value(i, j)
        dados.append(row)

    df = pd.DataFrame(dados)
    print(f"Dados ACSN carregados: {len(df)} produtos")
    return df

def normalizar_valor(valor):
    """Normaliza valores"""
    if pd.isna(valor) or valor is None:
        return ''
    if isinstance(valor, float):
        if valor != valor:  # NaN check
            return ''
        if valor == int(valor):
            return int(valor)
        return round(valor, 4)
    return str(valor).strip()

def to_int_str(valor):
    """Converte para string de inteiro"""
    if pd.isna(valor) or valor is None:
        return ''
    if isinstance(valor, float):
        if valor != valor:  # NaN
            return ''
        return str(int(valor))
    return str(valor).strip()

def migrar_para_sgacloud(row):
    """Converte uma linha do ACSN para formato SgaCloud"""
    codigo = row.get('procod', '')
    if isinstance(codigo, float):
        codigo = str(int(codigo))
    else:
        codigo = str(codigo).strip()
    
    return {
        'codigo': codigo,
        'descrição': normalizar_valor(row.get('prodes', '')).upper(),
        'gtin/ean': '',
        'embalagem': normalizar_valor(row.get('prouni', '')).upper(),
        'ncm': to_int_str(row.get('clf_ncm', '')),
        'cest': to_int_str(row.get('procest', '')),
        'preço': normalizar_valor(row.get('propdv', '')),
        'cst': normalizar_valor(row.get('procsosn', '')),
        'Solicitar Balança': '',
        'Exportar p/ Balança': '',
        'custo unitário': normalizar_valor(row.get('propdc', '')),
        'estoque': '',
        'referência': normalizar_valor(row.get('proref', '')),
        'seção': '',
        'grupo': '',
        'subgrupo': '',
        'marca': normalizar_valor(row.get('promar', '')).upper(),
        'peso': normalizar_valor(row.get('propeso', '')),
        'altura': '',
        'largura': '',
        'comprimento': '',
        'dias de validade': '',
        'CST PIS/COFINS': normalizar_valor(row.get('propis', '')) or normalizar_valor(row.get('procofins', '')),
        'CST IPI': normalizar_valor(row.get('prostipi', '')),
        'EnquadramentoIpi': normalizar_valor(row.get('procodipi', '')),
        'Tipo': '',
        'Origem': to_int_str(row.get('proorig', 0)) or '0',
        '% IPI': normalizar_valor(row.get('proipi', '')),
        '% PIS': '',
        '% COFINS': '',
        'Descrição Adicional': '',
        'Benef. Fiscal': '',
        'Observações': '',
        'Estoque Mínimo': normalizar_valor(row.get('proqmi', '')),
        'Estoque Máximo': '',
        '% Redução de ICMS': '',
        '% ICMS': normalizar_valor(row.get('proipe', '')),
        'Nat. Receita PIS/COFINS': '',
        'CNPJ/CPF fornecedor': '',
        'Class Trib (CBS/IBS)': '',
        'Class Trib (IS)': ''
    }

def criar_template_sgacloud():
    """Cria template vazio com instruções do SgaCloud (colunas exatas do template original)"""
    colunas = [
        'codigo', 'descrição', 'gtin/ean', 'embalagem', 'ncm', 'cest',
        'preço', 'cst', 'Solicitar Balança', 'Exportar p/ Balança',
        'custo unitário', 'estoque', 'referência', 'seção', 'grupo',
        'subgrupo', 'marca', 'peso', 'altura', 'largura', 'comprimento',
        'dias de validade', 'CST PIS/COFINS', 'CST IPI', 'EnquadramentoIpi',
        'Tipo', 'Origem', '% IPI', '% PIS', '% COFINS', 'Descrição Adicional',
        'Benef. Fiscal', 'Observações', 'Estoque Mínimo', 'Estoque Máximo',
        '% Redução de ICMS', '% ICMS', 'Nat. Receita PIS/COFINS',
        'CNPJ/CPF fornecedor', 'Class Trib (CBS/IBS)', 'Class Trib (IS)'
    ]
    return pd.DataFrame(columns=colunas)

def processar_migracao():
    """Processa a migração completa"""
    print("=" * 60)
    print("MIGRACAO ACSN -> SgaCloud")
    print("=" * 60)

    df_acsn = ler_dados_acsn()

    template = criar_template_sgacloud()

    produtos_migrados = []
    for _, row in df_acsn.iterrows():
        produto = migrar_para_sgacloud(row)
        produtos_migrados.append(produto)

    df_resultado = pd.DataFrame(produtos_migrados)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_saida = OUTPUT_DIR / f"MERCADORIAS_MIGRADAS_{timestamp}.xlsx"

    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        template.to_excel(writer, sheet_name='Template', index=False)
        df_resultado.to_excel(writer, sheet_name='Dados', index=False)

    print(f"\nMigracao concluida!")
    print(f"Arquivo gerado: {arquivo_saida}")
    print(f"Total de produtos migrados: {len(df_resultado)}")

    print("\nPreview dos 5 primeiros produtos:")
    print(df_resultado[['codigo', 'descrição', 'ncm', 'preço', 'custo unitário', 'marca']].head().to_string())

    return df_resultado, arquivo_saida

if __name__ == "__main__":
    df, arquivo = processar_migracao()
