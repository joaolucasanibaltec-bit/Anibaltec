# Documentação Completa — SGA → SGAcloud

---

## 1. Visão Geral

**SGA → SGAcloud** é um conversor de dados que lê arquivos CSV exportados do sistema SGA (retaguarda comercial) e os converte para o formato XLSX dos templates de importação do SGAcloud (plataforma web).

### Problema resolvido

O SGA exporta relatórios em CSV com estrutura própria. O SGAcloud exige planilhas XLSX em formato específico com códigos IBGE, tributações e campos padronizados. Fazer esta conversão manualmente para milhares de registros é inviável.

### Funcionalidades principais

- Conversão de produtos (mercadorias) — 6.104 registros
- Conversão de clientes — 14.992 registros (clientes + fornecedores)
- Conversão independente (apenas produtos, apenas clientes, ou ambos)
- Consulta automática de códigos IBGE (5571 municípios em cache)
- Consulta de CEP via ViaCEP + AwesomeAPI como fallback
- Tratamento flexível de registros sem localização (manter / preencher / remover)
- Interface desktop (CustomTkinter) e web (FastAPI + React)

---

## 2. Arquitetura

```
SgaToSgaCloud/
│
├── app.py                 # Interface desktop (CustomTkinter)
├── src/                   # Núcleo do conversor
│   ├── converter.py       #   Lógica principal de conversão
│   ├── ibge_lookup.py     #   Consulta de códigos IBGE
│   ├── cep_lookup.py      #   Consulta de CEP (ViaCEP)
│   ├── reader.py          #   Leitura de CSV (UTF-8/Latin-1)
│   └── xlsx_writer.py     #   Escrita de XLSX com formatação
├── config/                # Configurações
│   ├── mappings.py        #   Mapeamento coluna-fonte → coluna-destino
│   ├── anibaltec_theme.json  # Tema CustomTkinter
│   └── ibge_cache.json    #   Cache de códigos IBGE (5571 municípios)
├── backend/               # Servidor web
│   ├── main.py            #   App FastAPI + FrontendMiddleware
│   ├── routes/
│   │   └── convert.py     #   Endpoints de conversão
│   └── services/
│       └── converter_service.py  # Wrapper do src/ para API
├── frontend/dist/         # Interface React compilada
├── SgaCloud/              # Templates XLSX de origem
├── output/                # Arquivos convertidos
├── run_web.bat / .sh      # Launcher web
├── run_desktop.bat / .sh  # Launcher desktop
├── Makefile               # Targets Linux
└── Dockerfile             # Container Docker
```

### Camadas

1. **Apresentação** — `app.py` (desktop) ou `frontend/dist/` (web)
2. **Serviço** — `backend/services/converter_service.py` (web) ou integração direta (desktop)
3. **Domínio** — `src/` (regras de negócio da conversão)
4. **Infraestrutura** — `config/` (mapeamentos, cache, tema)

---

## 3. Módulos

### 3.1 `src/converter.py`

Núcleo do sistema. Contém a lógica de conversão para produtos e clientes.

**Classes e funções:**

- `Converter` — classe principal
  - `__init__(base_path, ...)` — recebe caminhos de templates e CSVs
  - `convert_products()` — converte `planilha_produtos.csv` → `MERCADORIAS.xlsx`
  - `convert_clients(suppliers_path)` — converte `planilha_clientes.csv` + `planilha_fornecedor.csv` → `CLIENTES.xlsx`
  - `convert_both()` — executa ambas as conversões
  - `_get_clientes()` — lê e mescla clientes + fornecedores

**Fluxo de conversão de produtos:**

1. Lê CSV de produtos (`src/reader.py`)
2. Filtra apenas registros com estoque > 0
3. Mantém colunas do mapeamento `PRODUCT_MAPPING`
4. Renomeia colunas conforme template SGAcloud
5. Preenche valores padrão (CST, CFOP, CSOSN, origem, tributações)
6. Ordena colunas conforme template
7. Escreve XLSX com `xlsx_writer.py`

**Fluxo de conversão de clientes:**

1. Lê CSV de clientes e fornecedores
2. Remove duplicatas por documento (CPF/CNPJ)
3. Renomeia colunas conforme mapeamento `CLIENT_MAPPING`
4. Aplica `handle_missing` (manter / preencher / remover registros sem cidade/UF)
5. Consulta códigos IBGE para cada registro
6. Aplica regras de formatação (numero → "SN" quando vazio, etc.)
7. Ordena colunas e escreve XLSX

### 3.2 `src/ibge_lookup.py`

Sistema de consulta de códigos IBGE por nome do município e UF.

**Componentes:**

- `IBGELookup` — classe principal
  - Carrega cache de `config/ibge_cache.json` (5571 municípios)
  - `get_codigo(cidade, uf)` → código IBGE de 7 dígitos ou None

**Estratégias de matching (5 níveis):**

1. Match exato (normalizado)
2. Remoção de sufixos ` - *`, ` - ` etc.
3. Correção de contracções (`d oeste` → `doeste`)
4. Tabela de aliases manuais
5. UF fallback (se há apenas UF, tenta match só por UF)

**Normalização:**

- Remove acentos (`NFD` → compose)
- Upper case
- Remove pontuação
- Remove espaços extras
- Tabela de aliases: `acu → assu`, `moji mirim → mogi mirim`, `v constança → sao paulo`

**Cache IBGE:**

- Construído via API do IBGE (`https://servicodados.ibge.gov.br/api/v1/localidades/municipios`)
- 5571 municípios
- Salvos com `ensure_ascii=False` para preservar caracteres acentuados
- Recriação automática se o cache estiver corrompido ou desatualizado

### 3.3 `src/cep_lookup.py`

Sistema de consulta de CEP com 3 níveis de fallback.

**Fluxo:**

1. **ViaCEP** (tenta primeiro) — `viacep.com.br/ws/{cep}/json/`
2. **AwesomeAPI** (fallback) — `cep.awesomeapi.com.br/json/{cep}`
3. **Override hardcoded** (último recurso) — dicionário `_CEP_OVERRIDES` para CEPs genéricos como 59600000

**CEP_OVERRIDES:**

```python
_CEP_OVERRIDES = {
    "59600000": {  # Mossoró (CEP genérico central)
        "cidade": "Mossoró",
        "uf": "RN",
        "ibge": "2408003"
    }
}
```

**Coordenador de consultas:** `get_cidade_uf(cep)` é chamado pelo `converter.py` para registros que têm CEP mas não têm cidade/UF preenchidos.

### 3.4 `src/reader.py`

Leitor de CSV com detecção automática de encoding.

**Comportamento:**

1. Tenta UTF-8 primeiro
2. Se falhar, tenta Latin-1 (ISO-8859-1)
3. Se falhar, tenta UTF-16

**Funções:**

- `read_csv(path, col_map)` → retorna DataFrame com colunas renomeadas

### 3.5 `src/xlsx_writer.py`

Escritor de XLSX mantendo a formatação do template original.

**Funcionalidades:**

- Carrega template XLSX como base
- Preserva formatação (cores, bordas, fontes)
- Abaixa dados a partir da linha 2 (mantém cabeçalho)
- Ajusta automaticamente o espaçamento das colunas

### 3.6 `config/mappings.py`

Define os mapeamentos de colunas entre CSV de origem e template de destino.

**Estrutura:**

- `PRODUCT_MAPPING` — mapeamento para mercadorias (cerca de 40 colunas)
- `CLIENT_MAPPING` — mapeamento para clientes (cerca de 30 colunas)
- `SUPPLIER_MAPPING` — mapeamento para fornecedores

**Valores padrão:** cada mapeamento inclui valores fixos para colunas que não existem no CSV de origem:
- CST, CFOP, CSOSN para produtos
- Tipo de contribuinte, tributações para clientes

---

## 4. Tratamento de Registros sem Localização (`handle_missing`)

Presente em 3 camadas:

### 4.1 `src/converter.py`

```python
def convert_clients(self, handle_missing='keep', fill_city='', fill_uf=''):
```

- `'keep'` — mantém registros como estão (cidade/UF em branco)
- `'fill'` — preenche cidade/UF com `fill_city` e `fill_uf`, depois consulta IBGE
- `'remove'` — remove registros que não têm cidade nem UF

### 4.2 Desktop (`app.py`)

Radio buttons na tela de Config:
- "Manter" (default)
- "Preencher com:" → campos de cidade e UF aparecem
- "Remover"

### 4.3 Web (`frontend/`)

Mesmo comportamento no `StepConfig.tsx` com radio buttons e campos condicionais.

---

## 5. Interface Desktop

### Tecnologia

- **CustomTkinter** (tema escuro)
- PyInstaller-compatible (build com `SGAtoSGAcloud.spec`)
- Resolução: 900×650, não redimensionável

### Temas (Anibaltec)

- **Primária:** Navy `#0f1a2e`
- **Acento:** Amber `#d4942b`

15 tipos de widget configurados em `config/anibaltec_theme.json`:
CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkCheckBox, CTkRadioButton,
CTkOptionMenu, CTkComboBox, CTkScrollbar, CTkTextbox, CTkProgressBar,
CTkSlider, CTkSwitch, CTkTabview

### Wizard de 4 etapas

| Etapa | Tela | Função |
|---|---|---|
| Config | Configuração | Diretórios, tipo de conversão, handle_missing |
| Mercadorias | Pré-visualização | Confirma produtos (estoque > 0) |
| Clientes | Pré-visualização | Confirma clientes |
| Gerar | Conversão | Botão Converter + barra de progresso |

---

## 6. Interface Web

### 6.1 Backend (FastAPI)

**Arquitetura:**

- `backend/main.py` — app FastAPI com CORS + FrontendMiddleware
- `backend/routes/convert.py` — endpoints de conversão
- `backend/services/converter_service.py` — wrapper do `src/converter.py`

**Middleware:**

- `CORSMiddleware` — permite acesso de qualquer origem (LAN)
- `FrontendMiddleware` — intercepta requisições que não são `/api/` nem `/assets/` e serve `index.html` (SPA)

**Endpoints:**

| Método | Rota | Parâmetros | Descrição |
|---|---|---|---|
| POST | `/api/convert/products` | `csv_produtos`, `template_mercadorias` | Converte apenas produtos |
| POST | `/api/convert/clients` | `csv_clientes`, `csv_fornecedor`, `template_clientes`, `handle_missing`, `fill_city`, `fill_uf` | Converte apenas clientes |
| POST | `/api/convert/both` | Todos os anteriores | Converte produtos e clientes |
| GET | `/api/health` | — | Health check |

**Para cada endpoint:**

1. Recebe arquivos via `UploadFile` (multipart/form-data)
2. Salva em diretório temporário
3. Instancia `Converter` com os caminhos
4. Executa conversão
5. Retorna arquivo XLSX como `FileResponse` (download automático)

### 6.2 Frontend (React + TypeScript + Vite)

**Componentes:**

- `App.tsx` — estado global (step, opções, parâmetros handle_missing)
- `Wizard.tsx` — navegação entre etapas
- `StepConfig.tsx` — formulário de configuração (diretórios, tipo, handle_missing)
- `StepProdutos.tsx` / `StepClientes.tsx` — pré-visualização OK
- `StepGerar.tsx` — botão de conversão e progresso

**API client:** `src/api/client.ts` — funções `convertProducts`, `convertClients`, `convertBoth`

**Proxy (dev):** Vite proxy `/api` → `http://localhost:8000`

**Build:** `npm run build` → `frontend/dist/`

---

## 7. Cobertura IBGE

### Dados atuais

- **Total de registros:** 14.992 (clientes + fornecedores)
- **Cobertura:** 99,37% (14.898/14.992)
- **Não resolvidos:** 94 registros sem cidade, UF ou CEP — verdadeiramente sem dados de localização

### Resoluções aplicadas

| Técnica | Registros |
|---|---|
| Match direto por cidade/UF | ~11.000 |
| Consulta CEP (ViaCEP + AwesomeAPI) | ~3.800 |
| Hardcoded CEP 59600000 → Mossoró/RN | 10 |
| Normalização de nome (acentos, sufixos) | 4 |
| Aliases manuais | 2 |

---

## 8. Testes

### Desktop (28 testes)

`docs/test-report.md` — 28/28 testes aprovados:
- Carregamento de tema
- Leitura de CSV
- Conversão de produtos
- Conversão de clientes
- IBGE lookup (casos normais, borda, aliases)
- CEP lookup
- Validação de regras de negócio

### Web (21 testes)

`docs/test-report-web.md` — 21/21 testes aprovados:
- Health check
- Upload e conversão de produtos
- Upload e conversão de clientes
- Conversão combinada
- Tratamento de erros (arquivos faltantes, formato inválido)

---

## 9. Deploy e Distribuição

### Pasta portátil (`SgaToSgaCloud/`)

Contém tudo que é necessário para executar o programa:
- Código fonte completo
- Frontend compilado
- Templates
- Scripts launcher (Windows .bat, Linux .sh)
- Makefile (Linux)
- Dockerfile

### Windows

Duplo clique em `run_web.bat` ou `run_desktop.bat`.

### Linux

```bash
chmod +x run_web.sh run_desktop.sh
./run_web.sh        # servidor web
# ou
./run_desktop.sh    # interface desktop
# ou
make run-web        # via Makefile
```

### Docker

```bash
docker build -t sga-converter .
docker run -p 8000:8000 sga-converter
```

### Requisitos de sistema

- Python 3.10 ou superior
- Pip
- 500 MB de RAM
- 100 MB de disco

### Dependências Python

```
customtkinter>=5.2.0
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.31.0
fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6
```

---

## 10. Fluxo de Dados Completo

```
[SGA] → CSV exportado
  │
  ▼
src/reader.py (UTF-8/Latin-1)
  │
  ▼
Filtragem (estoque > 0, duplicatas por doc)
  │
  ▼
Mapeamento (config/mappings.py)
  │
  ▼
[Dados sem cidade/UF?]
  ├── SIM → handle_missing
  │         ├── keep:  mantém em branco
  │         ├── fill:  preenche com dados fornecidos
  │         └── remove: exclui registro
  │
  ▼
IBGE lookup (src/ibge_lookup.py)
  │
  ├── Match por cidade/UF → OK
  ├── Match por CEP → src/cep_lookup.py
  │     ├── ViaCEP
  │     ├── AwesomeAPI (fallback)
  │     └── CEP_OVERRIDES (último recurso)
  │
  ▼
Formatação final (numero 'SN', CST, CFOP, etc.)
  │
  ▼
src/xlsx_writer.py → XLSX formatado
  │
  ▼
[SGAcloud] → Importar planilha
```

---

## 11. Manutenção

### Atualizar cache IBGE

O cache em `config/ibge_cache.json` pode ser recriado excluindo o arquivo e executando:
```python
from src.ibge_lookup import rebuild_ibge_cache
rebuild_ibge_cache()  # baixa os 5571 municípios da API do IBGE
```

### Adicionar alias de cidade

Editar `IBGELookup._CITY_ALIASES` em `src/ibge_lookup.py`:
```python
_CITY_ALIASES = {
    "variacao": "nome oficial",
    ...
}
```

### Adicionar override de CEP

Editar `_CEP_OVERRIDES` em `src/cep_lookup.py`:
```python
_CEP_OVERRIDES = {
    "00000000": {"cidade": "Cidade", "uf": "UF", "ibge": "0000000"},
    ...
}
```

---

## 12. Histórico de Versões

| Versão | Data | Mudanças |
|---|---|---|
| 1.0.0 | — | Versão inicial com conversão produtos + clientes |
| 1.1.0 | — | IBGE lookup com cache, aliases, normalização |
| 1.2.0 | — | Interface web (FastAPI + React) |
| 1.3.0 | — | CEP lookup (ViaCEP + AwesomeAPI) |
| 1.4.0 | — | `handle_missing` (keep / fill / remove) |
| 1.5.0 | — | Desktop refatorado para wizard 4 etapas |
| 1.6.0 | — | Frontend SPA com FrontendMiddleware, deploy portátil |

---

## Suporte

**Anibaltec Automação — Grupo Porto Tecnologia**
Mossoró/RN
