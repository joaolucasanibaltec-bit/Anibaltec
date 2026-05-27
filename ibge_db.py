import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_IBGE = os.path.join(BASE_DIR, 'ibge_municipios.csv')

_cache_ibge = None

def carregar_ibge():
    global _cache_ibge
    if _cache_ibge is not None:
        return _cache_ibge
    
    _cache_ibge = {}
    try:
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
                    
                    key1 = (nome.upper().strip(), uf)
                    _cache_ibge[key1] = codigo
                    
                    if len(row) >= 15:
                        no_accents = row[14].upper().strip()
                        if no_accents and no_accents != nome.upper().strip():
                            _cache_ibge[(no_accents, uf)] = codigo
    except Exception as e:
        print(f"Erro ao carregar IBGE: {e}")
    
    return _cache_ibge

def get_codigo_ibge(municipio, uf):
    if not municipio or not uf:
        return ''
    
    dados = carregar_ibge()
    
    municipio_upper = municipio.upper().strip()
    uf_upper = uf.upper().strip()
    
    key = (municipio_upper, uf_upper)
    if key in dados:
        return dados[key]
    
    for (nome, estado), codigo in dados.items():
        if municipio_upper in nome or nome in municipio_upper:
            if uf_upper == estado:
                return codigo
    
    return ''

if __name__ == '__main__':
    print("Teste - Códigos IBGE:")
    print(f"Mossoró/RN: {get_codigo_ibge('Mossoró', 'RN')}")
    print(f"Natal/RN: {get_codigo_ibge('Natal', 'RN')}")
    print(f"São Paulo/SP: {get_codigo_ibge('São Paulo', 'SP')}")
    print(f"Rio de Janeiro/RJ: {get_codigo_ibge('Rio de Janeiro', 'RJ')}")
    print(f"Maceió/AL: {get_codigo_ibge('Maceió', 'AL')}")