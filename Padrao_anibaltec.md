# Padrão Anibaltec — Identidade Visual & Padrões de Desenvolvimento Web

## 1. Identidade Visual

### Marca
- **Empresa:** Anibaltec Automação (Grupo Porto Tecnologia)
- **Segmento:** Automação comercial, varejo, food service, pagamentos
- **Tonalidade:** Profissional, confiável, tradicional
- **Produto:** SGA → SGAcloud Converter (migração de dados SGA para SGAcloud)

### Paleta de Cores (Tema Escuro)

| Token CSS | Cor | Uso |
|-----------|-----|-----|
| `--bg-primary` | `#0f1a2e` | Fundo do app, fundo da página |
| `--bg-surface` | `#1a2d4a` | Cards, frames, inputs |
| `--bg-border` | `#2a3f5f` | Bordas, separadores |
| `--accent` | `#d4942b` | Botões primários, progresso, steps ativos |
| `--accent-hover` | `#b87a1f` | Hover de botões |
| `--text-primary` | `#ffffff` | Texto principal |
| `--text-secondary` | `#e0e0e0` | Texto secundário |
| `--text-muted` | `#6b7f9f` | Placeholder, dicas, desabilitado |
| `--success` | `#2ecc71` | Sucesso, check |
| `--warning` | `#f1c40f` | Alerta |
| `--error` | `#e74c3c` | Erro |

### Tipografia (Web)
- **Font stack:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Tamanhos:** Title 22px, Section 18px, Body 14px, Label 13px, Muted 12px
- **Pesos:** Bold (700) para títulos, Semi-bold (600) para botões, Normal (400) para corpo

### Favicon
- SVG em `frontend/public/favicon.svg` — diamante/raio gradiente roxo (`#863bff` → `#7e14ff`)
- Importado via `<link>` no `index.html`

---

## 2. Estrutura do Projeto (Web)

```
frontend/                          # React + TypeScript + Vite
├── public/
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── api/
│   │   └── client.ts              # Axios API client
│   ├── components/
│   │   ├── StepIndicator.tsx       # Wizard step indicator
│   │   ├── StepConfig.tsx          # Step 1: Config
│   │   ├── StepProducts.tsx        # Step 2: Products
│   │   ├── StepClients.tsx         # Step 3: Clients
│   │   └── StepGenerate.tsx        # Step 4: Generate
│   ├── styles/
│   │   └── theme.css              # CSS custom properties theme
│   ├── types/
│   │   └── index.ts               # TypeScript interfaces
│   ├── assets/                    # Static images
│   ├── App.tsx                    # Root component + state management
│   ├── App.css                    # Legacy (não usar)
│   ├── index.css                  # Entry CSS (importa theme.css)
│   └── main.tsx                   # Entry point
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
└── tsconfig.node.json

backend/                           # FastAPI (Python)
├── main.py                        # App init, CORS, routes, static
├── requirements.txt
├── routes/
│   ├── files.py                   # GET /api/templates, POST /api/upload
│   └── convert.py                 # POST /api/convert/products|clients|both
├── services/
│   └── converter_service.py       # Orchestrates core engine
├── schemas/                       # Pydantic schemas
├── templates/                     # XLSX templates
└── uploads/                       # Temp uploaded files
```

---

## 3. Padrões de Código — Frontend (React + TypeScript)

### Convenções de Nomenclatura
- **Arquivos de componente:** PascalCase (`StepConfig.tsx`)
- **Arquivos de utilidade:** camelCase (`client.ts`)
- **Arquivos de estilo:** lowercase (`theme.css`)
- **Componentes:** PascalCase, default export
- **Funções:** camelCase (`fetchTemplates`, `handleConvert`)
- **Variáveis:** camelCase (`convertProductsEnabled`, `productOutputName`)
- **Interfaces:** PascalCase (`interface Props`, `interface Template`)
- **CSS classes:** kebab-case (`btn-primary`, `text-muted`, `mt-1`)
- **Constantes:** UPPER_SNAKE_CASE (`TOTAL_STEPS`)

### Estrutura de Componente
```tsx
interface Props {
  propName: string;
  onAction: (value: string) => void;
}

export default function ComponentName({ propName, onAction }: Props) {
  return (
    <div className="card">
      {/* conteúdo */}
    </div>
  );
}
```

### Padrão de Props
- Props definidas como `interface Props` no topo do arquivo
- Destructuring no parâmetro da função
- `onChange`, `onToggle`, `onConvert` para callbacks
- Tipagem explícita com TypeScript

### Gerenciamento de Estado (App.tsx)
- Todo estado global no componente pai (`App.tsx`)
- Estado elevado (lifting state up): `App.tsx` gerencia os estados, passa via props
- Hooks: `useState` e `useEffect` (sem biblioteca externa de estado)
- `addLog` e `updateProgress` como funções callback passadas adiante

### Padrão Async
```tsx
const handleConvert = async () => {
  setConverting(true);
  try {
    const blob = await convertProducts(sgaFile, templateName, outputName);
    downloadBlob(blob, outputName);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Erro desconhecido";
    addLog(`Erro: ${message}`);
  } finally {
    setConverting(false);
  }
};
```

### API Client (axios)
```tsx
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});
```
- Endpoints exportados como `async function`
- Upload via `FormData`
- Download via `responseType: "blob"` + `downloadBlob()` helper
- Proxy configurado no `vite.config.ts` para `/api` → `localhost:8000`

### Padrões CSS
- **CSS puro com Custom Properties** (sem CSS-in-JS, Tailwind ou CSS Modules)
- Tema definido em `:root` no `theme.css`
- Classes utilitárias: `.mt-1`, `.mt-2`, `.mb-1`, `.mb-2`, `.flex`, `.gap-1`, `.gap-2`, `.items-center`, `.justify-between`
- Botões: `.btn` + variante (`.btn-primary`, `.btn-success`, `.btn-ghost`)
- Cards: `.card` (surface + border + 8px radius)
- Texto: `.text-muted`, `.text-success`, `.text-error`

### Config TypeScript
- Target: ES2023
- JSX: react-jsx (React 19)
- Strict mode: `noUnusedLocals`, `noUnusedParameters`
- Module: ESNext, bundler resolution
- `erasableSyntaxOnly: true`

---

## 4. Padrões de Código — Backend (FastAPI + Python)

### Estrutura de Rota
```python
router = APIRouter()

@router.post("/convert/products")
async def convert_products(
    sga_file: UploadFile = File(...),
    template_name: str = Form("TEMPLATE MERCADORIAS.xlsx"),
):
    sga_path = _save_upload(sga_file)
    try:
        svc = ConverterService()
        out_path = svc.convert_products(sga_path, template_path, output_name)
        return FileResponse(out_path, ...)
    except Exception as e:
        raise HTTPException(500, f"Erro: {str(e)}")
    finally:
        sga_path.unlink(missing_ok=True)
```

### Helpers
- `_save_upload()`: salva arquivo com UUID, retorna Path
- `_get_template()`: localiza template no disco
- Cleanup sempre em `finally`

### Service Layer
```python
class ConverterService:
    def __init__(self):
        self.reader = SGAReader()
        self.converter = Converter()
        self.writer = XLSXWriter()
        self.ibge = IBGELookup()
```
- Inicializa recursos no `__init__`
- Métodos que orquestram pipeline completo

### Error Handling
- `try/except` com `HTTPException` + código e mensagem em português
- `finally` para limpeza de arquivos temporários

---

## 5. Padrões de Layout

### Wizard Pattern (4 Steps)
```
 Config → Mercadorias → Clientes → Gerar
```
- `StepIndicator`: círculos (36px) + conectores (2px) + labels
- Estados: completo (verde), ativo (âmbar), inativo (slate)
- Navegação: "Voltar" (ghost) | "Avançar" (primary)
- Validação por step antes de avançar

### Card Pattern
- `background: var(--bg-surface)`, `border: 1px solid var(--bg-border)`
- `border-radius: 8px`, `padding: 14px`
- `margin-bottom: 10px`

### Botões
| Variant | Classe | Cor |
|---------|--------|-----|
| Primary | `.btn-primary` | `--accent` (#d4942b) |
| Success | `.btn-success` | `--success` (#2ecc71) |
| Ghost | `.btn-ghost` | transparente + borda `--accent` |

### Formulários
- Input text: padding 10px 12px, border-radius 6px, focus accent
- File input: file-selector-button estilizado com accent
- Select: mesmo padrão do input
- Radio/Checkbox: accent-color definido, 16-18px
- Labels: block, 13px, text-secondary

### Progress Bar
- Container: 8px height, bg-border, border-radius 4px
- Fill: accent, transition width 0.3s ease
- Label: text-muted 12px

### Log Panel
- Card com max-height 160px, overflow-y auto
- Monospace font, 12px
- Linhas de erro em vermelho, demais em text-secondary

---

## 6. Convenções Gerais

### Imports (Frontend)
```tsx
import { useState, useEffect } from "react";
import ComponentName from "./components/ComponentName";
import { fetchTemplates, type Template } from "./api/client";
```

### Imports (Backend)
```python
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from backend.services.converter_service import ConverterService
```

### Path Resolution (Backend)
```python
BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "src"))
```

### Proxy (Dev)
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true }
  }
}
```

### Scripts (package.json)
- `npm run dev` — Vite dev server
- `npm run build` — tsc + vite build
- `npm run lint` — ESLint
- `npm run preview` — Preview production build

### Dependências Principais
- **Frontend:** React 19, TypeScript 6, Vite 8, Axios, react-dropzone
- **Backend:** FastAPI, Uvicorn, Pandas, OpenPyXL, Requests, python-multipart

---

## 7. Migração Desktop → Web (Mapeamento)

| Desktop (CustomTkinter) | Web (React + CSS) |
|-------------------------|-------------------|
| `CTkFrame` | `.card` |
| `CTkButton(fg_color="#d4942b")` | `.btn-primary` |
| `CTkEntry` | `input[type="text"]` |
| `CTkCheckBox` | `input[type="checkbox"]` + `.checkbox-label` |
| `CTkRadioButton` | `input[type="radio"]` + `.radio-row` |
| `CTkProgressBar` | `.progress-bar` inline style |
| `CTkTextbox` (logs) | `.card` monospace + scroll |
| `CTkFont(size=13)` | `font-size: 14px` (body) |
| `corner_radius=6` | `border-radius: 6px` |
| `fg_color="#1a2d4a"` | `background: var(--bg-surface)` |
| JSON theme file | `:root` CSS custom properties |
