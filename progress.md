# Progresso do Projeto - Conversor ACSN para SgaCloud

## Concluído ✅

### 1. Conversão de Produtos
- **Script**: `conversor_acsn_sgacloud.py`
- **Executável**: `dist/ConversorACSN_SgaCloud.exe`
- **Dados**: 5.637 produtos convertidos
- **Template**: `SgaCloud/TEMPLATE MERCADORIAS.xlsx`
- **Mapeamento**:
  - procod → código
  - prodes → descrição
  - clf_ncm → ncm
  - procest → cest
  - propdv → preço
  - procsosn → cst (conversão 102→00, 500→60, 900→90)
  - propdc → custo unitário
  - proref → referência
  - propis → CST PIS/COFINS
  - proipi → % IPI
  - proqmi → Estoque Mínimo

### 2. Conversão de Clientes/Fornecedores
- **Script**: `conversor_acsn_sgacloud.py` (mesmo arquivo com abas)
- **Dados**: 
  - CLIENTES.XLS: 143 clientes
  - FORNECEDORES.XLS: 254 fornecedores
- **Template**: `SgaCloud/TEMPLATE CLIENTES.xlsx`
- **Mapeamento**:
  - fccod → código
  - fcnom → razao / fantasia
  - fccpg → cpf cnpj
  - tipo → C (cliente) ou F (fornecedor)
  - fcrg → rg ie
  - fcend → logradouro
  - fccom → complemento
  - fccep → cep
  - fcbai → bairro
  - fccid → municipio
  - fcest → uf
  - fccad → cadastro
  - fcemail → email
  - fcfon → fone resid
  - fclimcr → limite
  - numero → SN (padrão)
  - dt vencimento → 01/01/1900 (padrão)

### 3. Campos Obrigatórios Template SgaCloud (CLIENTES)
- codigo
- razao
- logradouro
- numero
- cep
- bairro
- ibge
- municipio
- uf
- cadastro
- aniversario
- limite
- dt vencimento

## Arquivos do Projeto

```
Conversão de dados/
├── conversor_acsn_sgacloud.py   # Script principal
├── dist/
│   └── ConversorACSN_SgaCloud.exe  # Executável
├── ACSN/
│   ├── LayoutClientes.XLS
│   ├── LayoutFornecedores.XLS
│   └── LayoutProdutos.XLS
├── DadosACSN/
│   ├── PRODUTOS.XLS (5637 registros)
│   ├── CLIENTES.XLS (143 registros)
│   └── FORNECEDORES.XLS (254 registros)
├── SgaCloud/
│   ├── TEMPLATE MERCADORIAS.xlsx
│   └── TEMPLATE CLIENTES.xlsx
└── docs/
    ├── ACSN_LayoutProdutos_Analise.md
    └── Migração_ACSN_SgaCloud_Guia.md
```

## Como Usar

1. Execute `dist/ConversorACSN_SgaCloud.exe`

2. **Aba Produtos**:
   - Selecione `DadosACSN/PRODUTOS.XLS`
   - Selecione `SgaCloud/TEMPLATE MERCADORIAS.xlsx`
   - Clique em "Gerar Planilha SgaCloud"

3. **Aba Clientes/Fornecedores**:
   - Selecione `DadosACSN/CLIENTES.XLS`
   - Selecione `DadosACSN/FORNECEDORES.XLS`
   - Selecione `SgaCloud/TEMPLATE CLIENTES.xlsx`
   - Clique em "Gerar PLANILHA CLIENTES SgaCloud"

## Pendente/Rever
- ~~Verificar se campos obrigatórios estão todos preenchidos~~ ✅ OK (100% produtos)
- ~~Testar conversão de clientes/fornecedores~~ ❌ PENDENTE — nenhum output gerado
- Validar dados no SgaCloud (ambiente de teste)
- Executar conversão de Clientes + Fornecedores via interface gráfica

---

## Última Execução: Squad Migração ACSN → SgaCloud (08/05/2026)

### Resultados
| Item | Status | Detalhes |
|------|--------|----------|
| Análise de fontes | ✅ | 5.637 produtos, 143 clientes, 254 fornecedores |
| Validação Produtos | ✅ | 100% campos obrigatórios preenchidos |
| Validação Clientes | ⚠️ | Conversão não executada — sem outputs |
| Validação Fornecedores | ⚠️ | Conversão não executada — sem outputs |

### Recomendação
1. ✅ Produtos prontos para importação no SgaCloud
2. ⏳ Executar conversão de Clientes + Fornecedores via `dist/ConversorACSN_SgaCloud.exe`
3. ⏳ Validar dados importados no SgaCloud em ambiente de teste
