import csv

ARQUIVO_IBGE = r'C:\Users\joaol\OneDrive\Desktop\Conversão de dados\ibge_municipios.csv'
ARQUIVO_CLIENTES = r'C:\Users\joaol\OneDrive\Desktop\Conversão de dados\DadosACSN\CLIENTES.XLS'

def remove_accents(text):
    import unicodedata
    if not text:
        return ''
    text = text.upper().strip()
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

# Carregar IBGE
ibge_data = {}
with open(ARQUIVO_IBGE, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) >= 4:
            codigo = row[0]
            uf_codigo = row[1]
            nome = row[3]
            uf_map = {'11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
                      '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE',
                      '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
                      '41': 'PR', '42': 'SC', '43': 'RS',
                      '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'}
            uf = uf_map.get(uf_codigo, uf_codigo)
            
            # Usar nome sem acentos para matching
            nome_sem_acento = remove_accents(nome)
            ibge_data[(nome_sem_acento, uf)] = codigo

# Carregar clientes
import xlrd
book = xlrd.open_workbook(ARQUIVO_CLIENTES, encoding_override='latin1')
sheet = book.sheet_by_index(0)

print("Verificação de matching IBGE (com normalização):")
print("-" * 60)

for i in range(1, min(15, sheet.nrows)):
    municipio = sheet.cell(i, 5).value.strip()  # fccid
    uf = sheet.cell(i, 6).value.strip()  # fcest
    
    municipio_sem_acento = remove_accents(municipio)
    uf_upper = uf.upper().strip()
    
    key = (municipio_sem_acento, uf_upper)
    cod_ibge = ibge_data.get(key, 'NÃO ENCONTRADO')
    
    print(f"{municipio}/{uf} -> {cod_ibge}")