# Migração ACSN → SgaCloud: Guia de Conversão de Produtos

## Visão Geral do Processo

Este documento orienta a migração de dados de produtos do sistema **ACSN** para o **SgaCloud** usando as planilhas de layout fornecidas.

---

## Estrutura do Template SgaCloud

O template `TEMPLATE MERCADORIAS.xlsx` possui **42 colunas** para importação de mercadorias.

### Colunas Obrigatórias

| Coluna | Descrição | Formato | Exemplo |
|--------|-----------|---------|---------|
| codigo | Código de variação da mercadoria | Texto | "PROD001" |
| descrição | Descrição completa | Texto | "Produto Exemplo 500ml" |
| ncm | NCM (8 dígitos) | Texto | "21069090" |
| preço | Preço com 2 casas decimais | Decimal | "29.90" |
| custo unitário | Custo com 2 casas decimais | Decimal | "15.50" |

### Colunas Opcionais Recomendadas

| Coluna | Descrição | Origem ACSN |
|--------|-----------|-------------|
| gtin/ean | Código de barras | - |
| embalagem | Sigla até 6 letras | PROUNI |
| cest | CEST (7 dígitos) | PROCEST |
| estoque | Quantidade | - |
| referência | Código referência | PROREF |
| marca | Marca | PROMAR |
| peso | Peso kg | PROPESO |
| % ICMS | Percentual ICMS | PROICM / PROIPE |
| % IPI | Percentual IPI | PROIPI |
| CST | CST com 2 dígitos | PROCSOSN |

### Colunas Fiscais (Perfil Tributário)

| Coluna | Descrição | Origem ACSN |
|--------|-----------|-------------|
| CST PIS/COFINS | CST 2 dígitos | PROPIS / PROCOFINS |
| CST IPI | CST IPI 2 dígitos | PROSTIPI |
| EnquadramentoIpi | Enquadramento 5 dígitos | PROCODIPI |
| Origem | 0=Nacional, 1=Importado | PROORIG |
| % PIS | Percentual PIS | - |
| % COFINS | Percentual COFINS | - |
| % Redução de ICMS | Redução ICMS | PRODIFIMP |
| Nat. Receita PIS/COFINS | Código natureza receita | - |

### Colunas de Estoque

| Coluna | Descrição | Origem ACSN |
|--------|-----------|-------------|
| estoque | Quantidade atual | - |
| Estoque Mínimo | Qtd mínima | PROQMI |
| Estoque Máximo | Qtd máxima | - |
| dias de validade | Dias até validade | - |

### Colunas de Dimensões

| Coluna | Descrição | Origem ACSN |
|--------|-----------|-------------|
| peso | Peso kg | PROPESO |
| altura | Altura cm | - |
| largura | Largura cm | - |
| comprimento | Comprimento cm | - |

---

## Regras de Conversão de Dados

### 1. Campos Texto

```python
# Remover espaços extras e caracteres especiais
descricao = descricao.strip().upper()

# Limitar tamanho conforme especificação
codigo = codigo[:13]  # Máximo 13 caracteres no ACSN
descricao = descricao[:60]  # Máximo 60 caracteres no ACSN
```

### 2. Campos Numéricos

```python
# Usar ponto como separador decimal (formato brasileiro)
preco = str(valor).replace(',', '.')

# Arredondar conforme decimais permitidos
preco = round(valor, 2)  # 2 casas decimais
peso = round(valor, 3)   # 3 casas decimais
```

### 3. Campos Lógicos (Sim/Não)

```python
# Converter para T (True) ou F (False)
ativo = 'T' if campo == 'S' or campo == True else 'F'
```

### 4. Campos Fiscais - CSOSN/CST

O ACSN usa **CSOSN** para Simples Nacional e **CST** para regime normal:

| Regime | ACSN Campo | SgaCloud Valor |
|--------|------------|----------------|
| Simples | PROCSOSN | CSOSN 3 dígitos |
| Normal | PROSIT | CST 2 dígitos |

```python
def converter_cst_csosn(codtab, csosn, situacao):
    """Converter conforme regime tributário"""
    if codtab == '104':
        # Regime Simples Nacional
        return csosn  # ex: "102", "500"
    else:
        # Regime Normal
        return situacao  # ex: "00", "60", "90"
```

### 5. Campos de Origem ( Nacional/Importado)

```python
# PROORIG no ACSN: 0=Nacional, 1=Importado
# SgaCloud: mesmo padrão
origem = PROORIG  # 0 ou 1
```

---

## Exemplo de Script de Migração

```python
import pandas as pd
from openpyxl import load_workbook

# Carregar dados ACSN
df_acsn = pd.read_excel('ACSN/LayoutProdutos.XLS', engine='xlrd')

# Carregar template SgaCloud
df_template = pd.read_excel('SgaCloud/TEMPLATE MERCADORIAS.xlsx')

# Mapeamento de campos
mapeamento = {
    'PROCOD': 'codigo',
    'PRODES': 'descrição',
    'PROREF': 'referência',
    'PROMAR': 'marca',
    'PROUNI': 'embalagem',
    'PROPESO': 'peso',
    'PROCEST': 'cest',
    'PROPDV': 'preço',
    'PROCUS': 'custo unitário',
    'PROQMI': 'Estoque Mínimo',
    'PROCSOSN': 'CST',
    'PROPIS': 'CST PIS/COFINS',
    'PROCOFINS': 'CST PIS/COFINS',
    'PROIPI': '% IPI',
    'PROORIG': 'Origem',
    'PROICM': '% ICMS',
}

def migrar_produto(row, mapeamento):
    """Converter uma linha de produto ACSN para SgaCloud"""
    novo_registro = {}
    
    for campo_acsn, campo_sga in mapeamento.items():
        valor = row.get(campo_acsn)
        
        # Tratar valores nulos
        if pd.isna(valor):
            valor = ''
        
        # Aplicar conversões específicas
        if campo_sga == 'preço' or campo_sga == 'custo unitário':
            valor = str(valor).replace(',', '.')
        
        novo_registro[campo_sga] = valor
    
    return novo_registro

# Processar produtos
produtos_migrados = []
for _, row in df_acsn.iterrows():
    if row['codtab'] == 66:  # Apenas tabela PRODUTO
        produtos_migrados.append(migrar_produto(row, mapeamento))

# Criar DataFrame para exportação
df_migrado = pd.DataFrame(produtos_migrados)

# Exportar para template
with pd.ExcelWriter('SgaCloud/MERCADORIAS_MIGRADAS.xlsx', 
                    engine='openpyxl') as writer:
    df_template.to_excel(writer, sheet_name='Template', index=False)
    df_migrado.to_excel(writer, sheet_name='Dados', index=False)

print(f"Migrados {len(produtos_migrados)} produtos")
```

---

## Validações Necessárias

### Antes da Migração

1. **Verificar duplicidades** - Código PROCOD não pode se repetir
2. **Validar NCM** - Deve ter 8 dígitos
3. **Validar CEST** - Deve ter 7 dígitos
4. **Verificar CSOSN/CST** - Valores válidos conforme legislação

### Após a Migração

1. **Verificar encoding** - Caracteres especiais (acentos)
2. **Confirmar decimais** - Valores monetários com 2 casas
3. **Testar importação** - Upload no SgaCloud em ambiente de teste

---

## Problemas Comuns e Soluções

| Problema | Causa | Solução |
|----------|-------|---------|
| Preço com virgula | Formato brasileiro | Substituir ',' por '.' |
| Campos vazios | Dados não existem no ACSN | Deixar vazio ou usar padrão |
| Caracteres especiais | Encoding diferente | Normalizar para UTF-8 |
| CST inválido | Regime tributário | Mapear CSOSN → CST correto |
| NCM não encontrado | NCM não cadastrado | Cadastrar NCM no SgaCloud |

---

## Estrutura de Arquivos para Migração

```
Conversão de dados/
├── ACSN/
│   ├── LayoutProdutos.XLS      # Layout origem
│   ├── LayoutClientes.XLS      # (futuro)
│   └── LayoutFornecedores.XLS  # (futuro)
├── SgaCloud/
│   ├── TEMPLATE MERCADORIAS.xlsx  # Template destino
│   └── MERCADORIAS_MIGRADAS.xlsx # Resultado migração
├── docs/
│   ├── ACSN_LayoutProdutos_Analise.md
│   └── Migração_ACSN_SgaCloud_Guia.md
└── scripts/
    └── migrar_produtos.py      # Script de migração
```

---

## Próximos Passos

1. ✅ Analisar estrutura ACSN LayoutProdutos
2. ✅ Analisar template SgaCloud TEMPLATE MERCADORIAS
3. ⬜ Validar dados de exemplo (planilha real com produtos)
4. ⬜ Desenvolver script de migração
5. ⬜ Testar migração com dados fictícios
6. ⬜ Executar migração em produção
7. ⬜ Validar importação no SgaCloud
