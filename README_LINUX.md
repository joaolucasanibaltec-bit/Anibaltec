# Conversor ACSN para SgaCloud - Versão Linux

## Instalação

1. **Copie os arquivos para o Linux:**
   - `conversor_acsn_sgacloud.py`
   - `ibge_municipios.csv`
   - `requirements.txt`

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute:**
   ```bash
   python conversor_acsn_sgacloud.py
   ```

## Compilar executável (opcional)

Para criar um executável standalone:
```bash
pip install pyinstaller
pyinstaller --onefile conversor_acsn_sgacloud.py
```

O executável será criado em `dist/ConversorACSN_SgaCloud`