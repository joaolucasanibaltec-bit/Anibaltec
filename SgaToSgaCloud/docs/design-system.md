# Design System — SGA → SGAcloud Converter

## Marca
- **Empresa:** Anibaltec Automação (Grupo Porto Tecnologia)
- **Segmento:** Automação comercial, varejo, food service, pagamentos
- **Tonalidade:** Profissional, confiável, tradicional

## Paleta de Cores

### Primária (Navy Anibaltec)
| Token | Cor | Uso |
|-------|-----|-----|
| `--color-bg-primary` | `#0f1a2e` | Fundo da janela, fundo do app |
| `--color-bg-surface` | `#1a2d4a` | Frames, cards, entries |
| `--color-bg-border` | `#2a3f5f` | Bordas, separadores |

### Accent (Âmbar)
| Token | Cor | Uso |
|-------|-----|-----|
| `--color-accent` | `#d4942b` | Botões principais, progresso, abas selecionadas |
| `--color-accent-hover` | `#b87a1f` | Hover de botões |
| `--color-accent-glow` | `#d4942b` | Indicadores, checkmarks |

### Neutra
| Token | Cor | Uso |
|-------|-----|-----|
| `--color-text-primary` | `#ffffff` | Texto principal |
| `--color-text-secondary` | `#e0e0e0` | Texto secundário (logs) |
| `--color-text-muted` | `#6b7f9f` | Placeholder, dicas, desabilitado |

### Semântica
| Token | Cor | Uso |
|-------|-----|-----|
| `--color-success` | `#2ecc71` | Sucesso, check |
| `--color-warning` | `#f1c40f` | Alerta |
| `--color-error` | `#e74c3c` | Erro |

## Tipografia
- **Fonte:** Default do sistema (CustomTkinter)
- **Tamanhos:**
  - Título: `CTkFont(size=18, weight="bold")`
  - Seção: `CTkFont(size=14, weight="bold")`
  - Corpo: `CTkFont(size=13)`
  - Rótulo: `CTkFont(size=12)`
  - Detalhes: `CTkFont(size=11)`

## Componentes

### Botões
- **Primário (Âmbar):** `fg_color="#d4942b"`, `hover_color="#b87a1f"`
- **Perigo (Vermelho):** `fg_color="#e74c3c"`, `hover_color="#c0392b"`
- **Sucesso (Verde):** `fg_color="#2ecc71"`, `hover_color="#27ae60"`
- **Ghost (transparente):** `fg_color="transparent"`, `border_color="#2a3f5f"`
- **Cantos:** `corner_radius=6`
- **Altura padrão:** 36px
- **Altura grande:** 44px

### Cards
- `fg_color="#1a2d4a"`, `border_color="#2a3f5f"`, `corner_radius=8`
- Padding interno: 16px
- Margem entre cards: 12px

### Inputs
- Fundo: `#1a2d4a`, borda: `#2a3f5f`, `corner_radius=6`
- Altura: 34px
- Placeholder: `#6b7f9f`

### Wizard Steps
- **Ativo:** Texto branco + indicador âmbar (`#d4942b`)
- **Inativo:** Texto `#6b7f9f` + indicador `#2a3f5f`
- **Completo:** Texto `#6b7f9f` + indicador verde (`#2ecc71`)
- Conector entre steps: linha `#2a3f5f`

## Layout

### Janela
- **Tamanho:** 860x660 (wizard maior)
- **Título:** "SGA → SGAcloud Converter"
- **Ícone:** Anibaltec (se disponível)
- **Mínimo:** 720x560

### Wizard
```
┌──────────────────────────────────────┐
│  [1] Config  ─── [2] Mercadorias ───│
│  ─── [3] Clientes  ─── [4] Gerar    │
├──────────────────────────────────────┤
│                                      │
│         CONTEÚDO DA ETAPA            │
│                                      │
├──────────────────────────────────────┤
│  [Voltar]              [Avançar]     │
│  Progress: ████████░░ 80%           │
│  Log: ...                            │
└──────────────────────────────────────┘
```

### Etapa 1 — Configurações
- Card único centralizado
- Campo: CEP Padrão (placeholder "Ex: 59500000")
- Info texto explicativo

### Etapa 2 — Mercadorias
- 3 pares (Label + Entry + Botão):
  - Planilha SGA (Produtos) → CSV
  - Template SGAcloud → XLSX
  - Arquivo de Saída → XLSX
- Info box explicativa no final

### Etapa 3 — Clientes/Fornecedores
- 4 pares (Label + Entry + Botão):
  - Planilha SGA (Clientes) → CSV
  - Planilha SGA (Fornecedores) → CSV
  - Template SGAcloud → XLSX
  - Arquivo de Saída → XLSX
- Info box explicativa no final

### Etapa 4 — Gerar
- Resumo dos arquivos selecionados (cards de confirmação)
- **Checkboxes independentes:**
  - [x] Converter Mercadorias (disponível se preenchido na etapa 2)
  - [x] Converter Clientes/Fornecedores (disponível se preenchido na etapa 3)
- Se apenas Mercadorias preenchido → só mostra checkbox Mercadorias
- Se apenas Clientes preenchido → só mostra checkbox Clientes
- Se ambos preenchidos → ambos selecionados por padrão
- Botão "GERAR ARQUIVOS" grande (44px, verde)
- Barra de progresso âmbar
- Painel de log
- Status indicator

## Interações

### Navegação
- Botão "Voltar": etapa anterior (desabilitado na etapa 1)
- Botão "Avançar": próxima etapa (vira "Gerar" na etapa 4)
- Transição suave (mudança de frame)
- Indicador de etapa no topo sempre visível

### Validação
- Etapa 2: validar se paths foram preenchidos antes de avançar
- Etapa 3: validar se paths foram preenchidos antes de avançar
- Etapa 4: confirmar antes de converter
- **Conversão independente**: permitir converter apenas Mercadorias, apenas Clientes, ou ambos
- Se apenas uma etapa foi preenchida, avançar direto para Gerar
- Ao menos uma conversão deve estar selecionada para habilitar o botão "GERAR ARQUIVOS"

### Feedback
- Progress bar âmbar durante conversão
- Log em tempo real no painel inferior
- Check verde ao concluir
- Alertas amarelos para warnings
- Erro vermelho com mensagens claras

## Tema CustomTkinter
O tema está em `config/anibaltec_theme.json`.
Carregar com: `ctk.set_default_color_theme("config/anibaltec_theme.json")`
