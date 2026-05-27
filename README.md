# Conversor ACSN para SgaCloud

Conversor de dados do sistema ACSN para o formato SgaCloud.

## Funcionalidades

- **Conversão de Produtos**: Converte planilha de produtos para formato SgaCloud
- **Conversão de Clientes/Fornecedores**: Unifica clientes e fornecedores em uma única planilha
- **Código IBGE**: Busca automática do código IBGE para todos os 5.570 municípios brasileiros
- **Correção de Data**: Converte datas do formato `08-jan-25` para `08/01/2025`

## Arquivos do Projeto

```
Conversão de dados/
├── conversor_acsn_sgacloud.py    # Script principal (Python)
├── ibge_municipios.csv            # Banco de dados IBGE (5.570 municípios)
├── requirements.txt               # Dependências Python
├── compilar_linux.sh             # Script para compilar no Linux
├── README_LINUX.md               # Instruções específicas para Linux
├── dist/
│   └── ConversorACSN_SgaCloud.exe # Executável Windows
├── DadosACSN/
│   ├── PRODUTOS.XLS
│   ├── CLIENTES.XLS
│   └── FORNECEDORES.XLS
└── SgaCloud/
    ├── TEMPLATE MERCADORIAS.xlsx
    └── TEMPLATE CLIENTES.xlsx
```

---

## Windows

### Executar (sem Python instalado)

1. Copie a pasta `dist/` para o computador de destino
2. Certifique-se que `ibge_municipios.csv` está na mesma pasta do `.exe`
3. Execute `ConversorACSN_SgaCloud.exe`

### Executar (com Python instalado)

```bash
pip install -r requirements.txt
python conversor_acsn_sgacloud.py
```

### Compilar executável Windows

```bash
pip install pyinstaller
pyinstaller --onefile --name ConversorACSN_SgaCloud --add-data "ibge_municipios.csv;." conversor_acsn_sgacloud.py
```

---

## Linux

### Executar (com Python instalado)

1. Copie os arquivos:
   - `conversor_acsn_sgacloud.py`
   - `ibge_municipios.csv`
   - `requirements.txt`

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute:
   ```bash
   python conversor_acsn_sgacloud.py
   ```

### Compilar executável Linux

```bash
pip install pyinstaller
pyinstaller --onefile --name ConversorACSN_SgaCloud conversor_acsn_sgacloud.py
```

O executável será criado em `dist/ConversorACSN_SgaCloud`

---

## Como Usar o Aplicativo

### Conversão de Produtos

1. Execute o aplicativo
2. Na aba "Conversão Produtos":
   - Clique em "Selecionar PRODUCTS.XLS"
   - Selecione `DadosACSN/PRODUTOS.XLS`
   - Clique em "Selecionar Template" e escolha `SgaCloud/TEMPLATE MERCADORIAS.xlsx`
   - Clique em "Gerar Planilha SgaCloud"
3. O arquivo será salvo na pasta `output/` do diretório do template

### Conversão de Clientes/Fornecedores

1. Execute o aplicativo
2. Na aba "Conversão Clientes/Fornecedores":
   - Clique em "Selecionar Clientes" e escolha `DadosACSN/CLIENTES.XLS`
   - Clique em "Selecionar Fornecedores" e escolha `DadosACSN/FORNECEDORES.XLS`
   - Clique em "Selecionar Template" e escolha `SgaCloud/TEMPLATE CLIENTES.xlsx`
   - Clique em "Gerar PLANILHA CLIENTES SgaCloud"
3. O arquivo será salvo na pasta `output/` do diretório do template

---

## Mapeamento de Campos

### Produtos → SgaCloud

| Campo ACSN | Campo SgaCloud |
|------------|----------------|
| procod     | código         |
| prodes     | descrição      |
| clf_ncm    | ncm            |
| procest    | cest           |
| propdv     | preço          |
| procsosn   | cst (conversão 102→00, 500→60, 900→90) |
| propdc     | custo unitário |
| proref     | referência     |
| propis     | CST PIS/COFINS |
| proipi     | % IPI          |
| proqmi     | Estoque Mínimo |

### Clientes/Fornecedores → SgaCloud

| Campo ACSN | Campo SgaCloud |
|------------|----------------|
| fccod      | código         |
| fcnom      | razão/fantasia |
| fccpg      | cpf cnpj       |
| tipo       | C (cliente) ou F (fornecedor) |
| fcrg       | rg ie          |
| fcend      | logradouro     |
| fccom      | complemento    |
| fccep      | cep            |
| fcbai      | bairro         |
| fccid      | municipio      |
| fcest      | uf             |
| fccad      | cadastro       |
| fcemail    | email          |
| fcfon      | fone resid     |
| fclimcr    | limite         |
| IBGE       | código IBGE (busca automática) |

---

## Requisitos

- Python 3.8+ (para executar via script)
- Windows 10 ou superior (para .exe)

### Dependências Python

```
pandas
xlrd
openpyxl
```

---

## Observações

- O banco de dados IBGE contém 5.570 municípios brasileiros com códigos atualizados em 2024
- A busca de código IBGE utiliza normalização de acentos para melhor precisão
- O arquivo de saída é命名ado com timestamp: `MERCADORIAS_SGACLOUD_YYYYMMDD_HHMMSS.xlsx` ou `CLIENTE_FORNECEDOR_SGACLOUD_YYYYMMDD_HHMMSS.xlsx`