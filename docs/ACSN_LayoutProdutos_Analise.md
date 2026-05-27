# ACSN LayoutProdutos - Análise de Estrutura

## Visão Geral

Arquivo de layout de importação de produtos do sistema ACSN, contendo **44 campos** organizados em 3 tabelas lógicas (codtab).

---

## Tabela 1: PRODUTO (codtab=66) - Dados Cadastrais

| Campo | Nome | Tipo | Tamanho | Decimais | Descrição | Importa |
|-------|------|------|---------|----------|-----------|--------|
| A | PROCOD | C | 13 | 0 | Código | ✅ |
| B | PRODES | C | 60 | 0 | Descricao | ✅ |
| C | PROMAR | C | 6 | 0 | Marca | ✅ |
| D | PROUNI | C | 2 | 0 | Unidade | ✅ |
| E | PROATINAT | L | 1 | 0 | Ativo / Inativo | ✅ |
| F | PROCP1 | C | 15 | 0 | Campo Personalizado 1 | ✅ |
| G | PROCP2 | C | 15 | 0 | Campo Personalizado 2 | ✅ |
| H | PROREF | C | 20 | 0 | Referencia | ✅ |
| I | PROSIT | C | 3 | 0 | Situacao Tributaria | ✅ |
| J | PROCP3 | C | 15 | 0 | Campo Personalizado 3 | ✅ |
| K | PROCP4 | C | 15 | 0 | Campo Personalizado 4 | ✅ |
| L | PROPESO | N | 14 | 3 | Peso do Produto | ❌ |
| M | PROCODIPI | C | 3 | 0 | Codigo de Enquadramento do IPI | ❌ |
| N | PROCEST | C | 7 | 0 | Codigo CEST | ✅ |

---

## Tabela 2: PROLOJ (codtab=104) - Dados Comerciais e Fiscais

| Campo | Nome | Tipo | Tamanho | Decimais | Descrição | Importa | Máscara |
|-------|------|------|---------|----------|-----------|--------|---------|
| O | PROQMI | N | 11 | 3 | Quantidade minima | ✅ | 9,999,999.999 |
| P | PROPDC | N | 15 | 4 | Preco de compra | ✅ | 9,999,999,999,999.99 |
| Q | PROPDV | N | 15 | 4 | Preco de venda | ✅ | 9,999,999,999,999.99 |
| R | PROPCV | N | 10 | 4 | Margem | ✅ | 99,999.9999 |
| S | PROICM | N | 6 | 2 | ICMS de compra | ✅ | 9,999.99 |
| T | PROIPI | N | 6 | 2 | IPI | ✅ | 9,999.99 |
| U | COMISSAO | N | 6 | 2 | Comissao do vendedor | ✅ | 9,999.99 |
| V | PROFIN | N | 6 | 2 | Custo financeiro de compra | ✅ | 9,999.99 |
| W | PROFRE | N | 6 | 2 | Frete | ✅ | 9,999.99 |
| X | PROIPF | N | 6 | 2 | Imposto federal | ✅ | 9,999.99 |
| Y | PROIPE | N | 6 | 2 | ICMS Venda | ✅ | 9,999.99 |
| Z | PROCFV | N | 6 | 2 | Custo financeiro de venda | ✅ | 9,999.99 |
| AA | PROCOP | N | 6 | 2 | Custo operacional | ✅ | 9,999.99 |
| AB | PROCUS | N | 15 | 4 | Custo do produto | ✅ | 9,999,999,999,999.99 |
| AC | PRORENT | N | 9 | 4 | Rentabilidade | ✅ | 9,999.9999 |
| AD | PROCAPT | N | 6 | 2 | Capital de giro | ✅ | 9,999.99 |
| AE | PRODESC | N | 2 | 0 | Desconto maximo | ✅ | 99 |
| AF | PROIPECUS | N | 6 | 2 | Imposto estadual | ✅ | 9,999.99 |
| AG | PRODIFIMP | N | 6 | 2 | Diferenca de ICMS | ✅ | 9,999.99 |
| AH | PROEMB | N | 6 | 2 | Embalagem | ❌ | 9,999.99 |
| AI | PRODESCON | N | 6 | 2 | Desconto (Custo do Produto) | ❌ | 9,999.99 |
| AJ | PROLOTVD | N | 11 | 3 | Lote minimo de venda | ✅ | 9,999,999.999 |
| AK | PROORIG | C | 1 | 0 | Origem - CSOSN | ❌ | - |
| AL | PROCSOSN | C | 3 | 0 | CSOSN (Codigo de Situacao de Operacao) | ✅ | 999 |
| AM | PROSTIPI | C | 2 | 0 | Situacao tributaria do IPI | ❌ | - |
| AN | PROPIS | C | 2 | 0 | PIS - Codigo da Situacao Tributária | ✅ | 99 |
| AO | PROCOFINS | C | 2 | 0 | COFINS - Codigo da Situacao Tributária | ✅ | 99 |
| AP | PROADC | N | 6 | 2 | Custo Adicional | ✅ | 9,999.99 |

---

## Tabela 3: CLAFIS (codtab=175) - Classificação Fiscal (NCM)

| Campo | Nome | Tipo | Tamanho | Decimais | Descrição | Importa |
|-------|------|------|---------|----------|-----------|--------|---------|
| AQ | CLF_DES | C | 254 | 0 | Descricao NCM | ❌ |
| AR | CLF_NCM | C | 9 | 0 | Codigo NCM | ❌ |

---

## Observações Importantes para Desenvolvimento

### 1. Campos Obrigatórios para Migração
- **PROCOD** - Código do produto (chave primária)
- **PRODES** - Descrição
- **PROUNI** - Unidade de medida
- **PROCP1-PROCP4** - Campos customizáveis

### 2. Campos Condicionais
- **PROORIG** e **PROCSOSN** dependem do regime tributário (Simples Nacional usa CSOSN, Regime Normal usa CST)

### 3. Campos Não Importados
Os campos marcados como `importa=False` são informativos ou calculados internamente:
- PROPESO, PROCODIPI
- PROEMB, PRODESCON
- CLF_DES, CLF_NCM

### 4. Campos Fiscais com Máscara
- Percentuais: usar formato `XX.XX` (2 casas decimais)
- Valores monetários: usar formato com ponto decimal (não vírgula)

### 5. Tipos de Dados
- **C (Character)**: Texto/string
- **N (Numeric)**: Numérico com decimais configuráveis
- **L (Logical)**: Boolean (S/N ou 1/0)

---

## Sugestão de Mapeamento para SgaCloud

| ACSN Campo | SgaCloud Coluna | Observação |
|------------|-----------------|------------|
| PROCOD | codigo | Código do produto |
| PRODES | descrição | Descrição completa |
| PROREF | referência | Código de referência |
| PROMAR | marca | Marca do produto |
| PROUNI | embalagem | Unidade (sigla até 6 letras) |
| PROPESO | peso | Peso em kg |
| PROCEST | cest | Código CEST 7 dígitos |
| PROPDV | preço | Preço de venda |
| PROCUS | custo unitário | Custo do produto |
| PROQMI | Estoque Mínimo | Quantidade mínima |
| PROCSOSN | CST | CSOSN/CST do produto |
| PROPIS | CST PIS/COFINS | Código CST PIS |
| PROCOFINS | CST PIS/COFINS | Código CST COFINS |
| PROIPI | % IPI | Percentual IPI |
| PROORIG | Origem | 0=Nacional, 1=Importado |
| PROICM | % ICMS | Percentual ICMS |
| PROIPF | % PIS | Percentual PIS |
| - | % COFINS | Não existe campo direto (usar PROIPF ou configurar) |
