# Mappings: SGA -> SGAcloud

# Products: planilha_produtos.csv -> TEMPLATE MERCADORIAS.xlsx
# Note: Template col 1 = "COLUNA" (index), data starts at col 2
PRODUCT_MAPPING = {
    'codigo': ('codigo', 2),          # SGA col 2 -> Target col 2 (may be moved to gtin/ean if 8-14 digits)
    'descricao': ('descricao', 3),      # SGA col 3 -> Target col 3
    'codncm': ('ncm', 6),             # SGA col 83 -> Target col 6
    'cest': ('cest', 7),               # SGA col 127 -> Target col 7
    'unitario': ('preco', 8),          # SGA col 6 -> Target col 8
    'cst': ('cst', 9),                 # SGA col 85 -> Target col 9
    'precocusto': ('custo unitario', 12),  # SGA col 9 -> Target col 12
    'estoque': ('estoque', 13),        # SGA col 7 -> Target col 13
    'secao': ('secao', 15),           # SGA col 12 -> Target col 15
    'marca': ('marca', 18),           # SGA col 13 -> Target col 18
    'referencia': ('referencia', 13),  # SGA col 15 -> Target col 13
    'aliquota': ('subgrupo', 17),     # SGA col 5 -> Target col 17 (Subgrupo de Mercadorias)
    'origmerc': ('Origem', 28),        # SGA col 86 -> Target col 28
    # Field 'CNPJ/CPF fornecedor' (col 40) is NOT filled per user request
}

# Clients: planilha_clientes.csv -> TEMPLATE CLIENTES.xlsx
# Note: Template col 1 = "COLUNA" (index), data starts at col 2
CLIENT_MAPPING = {
    'chave': ('codigo', 2),
    'razaosocial': ('razao', 3),
    'nomecliente': ('fantasia', 4),
    'cgc': ('cpf cnpj', 5),
    'tipopessoa': ('tipo', 6),
    'rg': ('rg ie', 7),
    'rua': ('logradouro', 9),
    'numero': ('numero', 10),
    'cep': ('cep', 12),
    'bairro': ('bairro', 13),
    'cidade': ('municipio', 15),
    'uf': ('uf', 16),
    'datacadastro': ('cadastro', 17),
    'dtnasc': ('aniversario', 18),
    'email': ('email', 19),
    'fone': ('fone resid', 20),
    'celular': ('celular', 22),
    'limitecomprafiado': ('limite', 23),
    'HEX(observacao)': ('Observação', 27),
}

# Suppliers: planilha_fornecedor.csv -> TEMPLATE CLIENTES.xlsx
SUPPLIER_MAPPING = {
    'chave': ('codigo', 2),
    'nome': ('fantasia', 4),
    'cgc': ('cpf cnpj', 5),
    'razaosocial': ('razao', 3),
    'rua': ('logradouro', 9),
    'cep': ('cep', 12),
    'bairro': ('bairro', 13),
    'cidade': ('municipio', 15),
    'uf': ('uf', 16),
    'dtcad': ('cadastro', 17),
    'email': ('email', 19),
    'fone': ('fone resid', 20),
    'celular': ('celular', 22),
    'HEX(observacoes)': ('Observação', 27),
}
