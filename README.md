# SGA → SGAcloud

Conversor de dados do sistema **SGA** (CSV) para os templates **SGAcloud** (XLSX).

## Sobre

Este programa lê as planilhas exportadas pelo sistema SGA (produtos, clientes e fornecedores) e converte para o formato dos templates do SGAcloud, preenchendo automaticamente:

- **Códigos IBGE** — consulta automática por município, com fallback por CEP (ViaCEP)
- **Valores padrão** — CST, CFOP, CSOSN, origem, tributações conforme o template
- **Endereços** — normalização de campos (número, bairro, CEP, cidade, UF)
- **Registros sem localização** — opção de manter, preencher com dados padrão ou remover

Suporta conversão independente: apenas produtos, apenas clientes, ou ambos de uma vez.

### Formatos de entrada

| Arquivo | Origem |
|---|---|
| `planilha_produtos.csv` | SGA → Relatórios → Mercadorias |
| `planilha_clientes.csv` | SGA → Relatórios → Clientes |
| `planilha_fornecedor.csv` | SGA → Relatórios → Fornecedores |

### Formatos de saída

| Arquivo | Destino |
|---|---|
| `MERCADORIAS.xlsx` | SGAcloud → Importar → Mercadorias |
| `CLIENTES.xlsx` | SGAcloud → Importar → Clientes |

---

## Como usar

### Opção 1 — Desktop (janela gráfica)

Recomendado para uso local em um único computador.

**Windows:** Dê duplo clique em `run_desktop.bat`
**Linux:** `./run_desktop.sh` (ou `make run-desktop`)

O assistente de 4 etapas guiará a conversão:

1. **Config** — escolha diretórios, o que converter, e como tratar registros sem cidade/UF
2. **Mercadorias** — confirme os produtos que serão exportados (estoque > 0)
3. **Clientes** — confirme os clientes que serão exportados
4. **Gerar** — clique em "Converter" e aguarde os arquivos prontos

### Opção 2 — Web (servidor local)

Recomendado para acesso de múltiplos computadores na rede.

```bash
# Windows
run_web.bat

# Linux
./run_web.sh
```

Acesse pelo navegador: **http://localhost:8000**

Para usar de outro computador na mesma rede, acesse **http://{IP_DO_SERVIDOR}:8000**

### Opção 3 — Docker

```bash
docker build -t sga-converter .
docker run -p 8000:8000 sga-converter
```

---

## Instalação (primeira execução)

Os scripts `run_web.bat` / `run_web.sh` criam o ambiente virtual e instalam dependências automaticamente.

Para instalar manualmente:

**Windows:** `pip install -r requirements.txt`
**Linux:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

**Linux:** antes de usar os scripts `.sh`:
```bash
chmod +x run_web.sh run_desktop.sh
```

---

## Dependências

- Python 3.10+
- customtkinter, pandas, openpyxl, requests (desktop + web)
- fastapi, uvicorn, python-multipart (web)

---

## Suporte

**Anibaltec Automação — Grupo Porto Tecnologia**
Mossoró/RN
