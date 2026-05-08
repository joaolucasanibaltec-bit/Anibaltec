import pandas as pd
import logging
import re
from config.mappings import PRODUCT_MAPPING, CLIENT_MAPPING, SUPPLIER_MAPPING

class Converter:
    """Convert SGA DataFrames to SGAcloud format"""
    
    def convert_products(self, df_sga: pd.DataFrame) -> pd.DataFrame:
        """Convert SGA products to SGAcloud format with proper formatting"""
        
        # Filter: only products with stock > 0
        if 'estoque' in df_sga.columns:
            # Convert estoque from string (comma as decimal) to numeric
            df_sga['estoque_numeric'] = pd.to_numeric(
                df_sga['estoque'].astype(str).str.replace(',', '.'), 
                errors='coerce'
            )
            original_count = len(df_sga)
            df_sga = df_sga[df_sga['estoque_numeric'] > 0].copy()
            logging.info(f'Filtered products: {original_count} -> {len(df_sga)} (estoque > 0)')
            df_sga.drop('estoque_numeric', axis=1, inplace=True)
        
        # Define target columns in TEMPLATE ORDER (skip col 1 "COLUNA")
        template_cols = ['codigo', 'descricao', 'gtin/ean', 'embalagem', 'ncm', 'cest', 'preco', 'cst',
                       'Solicitar Balança', 'Exportar p/ Balança', 'custo unitario', 'estoque',
                       'referencia', 'secao', 'grupo', 'subgrupo', 'marca', 'peso', 'altura',
                       'largura', 'comprimento', 'dias de validade', 'CST PIS/COFINS', 'CST IPI',
                       'EnquadramentoIpi', 'Tipo', 'Origem', '% IPI', '% PIS', '% COFINS',
                       'Descricao Adicional', 'Benef. Fiscal', 'Observações', 'Estoque Mínimo',
                       'Estoque Máximo', '% Redução de ICMS', '% ICMS', 'Nat. Receita PIS/COFINS',
                       'CNPJ/CPF fornecedor', 'Class Trib (CBS/IBS)', 'Class Trib (IS)']
        
        # Create target DataFrame
        df_target = pd.DataFrame(index=range(len(df_sga)), columns=template_cols)
        df_target = df_target.fillna('')  # Fill all with empty strings
        
        # Process codigo field: check if it's GTIN/EAN (8, 12, 13, or 14 digits without leading zeros)
        if 'codigo' in df_sga.columns:
            gtin_count = 0
            regular_count = 0
            for idx, codigo_val in enumerate(df_sga['codigo'].astype(str).str.strip()):
                # Remove leading zeros to get actual length
                codigo_sem_zeros = codigo_val.lstrip('0') if codigo_val.isdigit() else codigo_val
                codigo_sem_zeros = codigo_sem_zeros if codigo_sem_zeros else '0'  # Handle all zeros
                
                # Debug: print first 10 values
                if idx < 10:
                    is_gtin = codigo_sem_zeros.isdigit() and len(codigo_sem_zeros) in [8, 12, 13, 14]
                    logging.info(f'idx={idx}, codigo="{codigo_val}", sem_zeros="{codigo_sem_zeros}", len_sem_zeros={len(codigo_sem_zeros)}, is_gtin={is_gtin}')
                
                # Check if it's GTIN/EAN (based on length without leading zeros)
                if codigo_sem_zeros.isdigit() and len(codigo_sem_zeros) in [8, 12, 13, 14]:
                    # It's a GTIN/EAN code
                    df_target.iloc[idx, df_target.columns.get_loc('gtin/ean')] = codigo_val
                    df_target.iloc[idx, df_target.columns.get_loc('codigo')] = ''
                    gtin_count += 1
                else:
                    # Regular product code
                    df_target.iloc[idx, df_target.columns.get_loc('codigo')] = codigo_val
                    regular_count += 1
            logging.info(f'GTIN/EAN codes: {gtin_count}, Regular codes: {regular_count}')
        
        # Fill mapped columns from SGA (excluding codigo which was handled above)
        for sga_col, (target_col, _) in PRODUCT_MAPPING.items():
            if sga_col == 'codigo':
                continue  # Already processed above
            if sga_col in df_sga.columns and target_col in df_target.columns:
                df_target[target_col] = df_sga[sga_col].astype(str).fillna('').values
            else:
                if sga_col not in df_sga.columns:
                    logging.warning(f'SGA column "{sga_col}" not found in source')
        
        # Format data according to template requirements (row 2 descriptions)
        df_target = self._format_product_data(df_target)
        
        # NOTE: CNPJ/CPF fornecedor (col 40) is NOT filled per user request
        df_target['CNPJ/CPF fornecedor'] = ''
        
        logging.info(f'Converted {len(df_target)} product records')
        return df_target
    
    def _format_product_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format product data according to template column requirements"""
        # Col 6: ncm - 8 digits
        if 'ncm' in df.columns:
            df['ncm'] = df['ncm'].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('\\N', '', regex=False)
            df['ncm'] = df['ncm'].apply(lambda x: x.zfill(8) if x and x != 'nan' else '')
        
        # Col 7: cest - 7 digits (handle \N as empty)
        if 'cest' in df.columns:
            df['cest'] = df['cest'].astype(str).str.replace('\\N', '', regex=False).str.replace(' ', '')
            df['cest'] = df['cest'].apply(lambda x: x.zfill(7) if x and x != 'nan' and len(x) > 0 else '')
        
        # Col 8: preco - 2 decimal places (empty if nan)
        if 'preco' in df.columns:
            df['preco'] = pd.to_numeric(df['preco'].astype(str).str.replace(',', '.'), errors='coerce')
            df['preco'] = df['preco'].apply(lambda x: '' if pd.isna(x) else f"{x:.2f}")
        
        # Col 9: cst - 2 digits (apply mapping: 102->00, 500->60, 400->40)
        if 'cst' in df.columns:
            df['cst'] = df['cst'].astype(str).str.split('-').str[0].str.strip()
            # Apply mapping rules for specific codes (2-digit output)
            cst_map = {'102': '00', '500': '60', '400': '40'}
            df['cst'] = df['cst'].apply(lambda x: cst_map.get(x, x) if x and x != 'nan' and x.isdigit() else '')
            # For other codes, take first 2 digits
            def format_cst(val):
                if not val or val == 'nan' or not val.isdigit():
                    return ''
                # If already 2 digits, return as is
                if len(val) == 2:
                    return val
                # If 3+ digits, take first 2
                if len(val) >= 2:
                    return val[:2].zfill(2)
                # If 1 digit, pad to 2
                return val.zfill(2) if len(val) > 0 else ''
            
            df['cst'] = df['cst'].apply(format_cst)
        
        # Col 12: custo unitário - 2 decimal places
        if 'custo unitario' in df.columns:
            df['custo unitario'] = pd.to_numeric(df['custo unitario'].astype(str).str.replace(',', '.'), errors='coerce')
            df['custo unitario'] = df['custo unitario'].apply(lambda x: '' if pd.isna(x) else f"{x:.2f}")
        
        # Col 13: estoque - up to 3 decimal places
        if 'estoque' in df.columns:
            df['estoque'] = pd.to_numeric(df['estoque'].astype(str).str.replace(',', '.'), errors='coerce')
            df['estoque'] = df['estoque'].apply(lambda x: '' if pd.isna(x) else f"{x:.3f}")
        
        # Col 19: peso - up to 3 decimal places
        if 'peso' in df.columns:
            df['peso'] = pd.to_numeric(df['peso'].astype(str).str.replace(',', '.'), errors='coerce')
            df['peso'] = df['peso'].apply(lambda x: '' if pd.isna(x) else f"{x:.3f}")
        
        # Col 16: subgrupo - keep full aliquota text (format: "XX - YY,YY %")
        if 'subgrupo' in df.columns:
            df['subgrupo'] = df['subgrupo'].astype(str).apply(lambda x: '' if x == 'nan' else x.strip())
            logging.info(f'Subgrupo sample: {df["subgrupo"].iloc[0] if len(df) > 0 else "empty"}')
        
        # Col 27: Tipo - default 0 (Mercadoria para revenda)
        if 'Tipo' in df.columns:
            df['Tipo'] = df['Tipo'].astype(str).replace('nan', '0').fillna('0')
        
        # Col 28: Origem - 1 decimal, default 0 (Nacional)
        if 'Origem' in df.columns:
            df['Origem'] = pd.to_numeric(df['Origem'], errors='coerce')
            df['Origem'] = df['Origem'].apply(lambda x: '0' if pd.isna(x) else f"{x:.1f}")
        
        # Col 38: % ICMS - 2 decimal places (if exists)
        if '% ICMS' in df.columns:
            df['% ICMS'] = pd.to_numeric(df['% ICMS'], errors='coerce')
            df['% ICMS'] = df['% ICMS'].apply(lambda x: '' if pd.isna(x) else f"{x:.2f}")
        
        return df
    
    def _parse_address(self, address):
        """Extract street and number from address. Returns (street, number)."""
        if not address or pd.isna(address) or address == '':
            return ('', 'SN')
        address = str(address).strip()
        # Match numbers at the end (with optional letter like 123A)
        match = re.search(r'\s+(\d+[A-Za-z]?)\s*$', address)
        if match:
            numero = match.group(1).strip()
            logradouro = address[:match.start()].strip()
            return (logradouro, numero)
        return (address, 'SN')
    
    def convert_clients_suppliers_no_ibge(self, df_clients: pd.DataFrame, df_suppliers: pd.DataFrame, ibge_lookup=None, default_cep: str = '', handle_missing: str = 'keep', fill_city: str = '', fill_uf: str = '') -> pd.DataFrame:
        """Convert clients and suppliers. handle_missing: 'keep'|'fill'|'remove'"""
        
        # Process clients: column mapping, address parsing, date conversion
        df_c = None
        if df_clients is not None and len(df_clients) > 0:
            df_c = df_clients.copy()
            for sga_col, (target_col, _) in CLIENT_MAPPING.items():
                if sga_col in df_c.columns:
                    df_c[target_col] = df_c[sga_col].fillna('').astype(str)
                else:
                    df_c[target_col] = ''
            
            df_c['tipo'] = 'C'
            parsed = df_c.get('logradouro', '').astype(str).apply(lambda x: self._parse_address(x))
            df_c['logradouro'] = parsed.apply(lambda x: x[0])
            df_c['numero'] = parsed.apply(lambda x: x[1])
            df_c.loc[df_c['numero'] == '', 'numero'] = 'SN'
            
            if default_cep:
                df_c['cep'] = df_c.get('cep', '').replace('', default_cep).replace('nan', default_cep)
            
            for date_col in ['cadastro', 'aniversario']:
                if date_col in df_c.columns:
                    dates = pd.to_datetime(df_c[date_col], format='%Y-%m-%d', errors='coerce')
                    df_c[date_col] = dates.dt.strftime('%d/%m/%Y').fillna('01/01/1900')
                    df_c.loc[df_c[date_col] == 'NaT', date_col] = '01/01/1900'
        
        # Process suppliers: column mapping, address parsing, date conversion
        df_s = None
        if df_suppliers is not None and len(df_suppliers) > 0:
            df_s = df_suppliers.copy()
            for sga_col, (target_col, _) in SUPPLIER_MAPPING.items():
                if sga_col in df_s.columns:
                    df_s[target_col] = df_s[sga_col].fillna('').astype(str)
                else:
                    df_s[target_col] = ''
            
            df_s['tipo'] = 'F'
            parsed = df_s.get('logradouro', '').astype(str).apply(lambda x: self._parse_address(x))
            df_s['logradouro'] = parsed.apply(lambda x: x[0])
            df_s['numero'] = parsed.apply(lambda x: x[1])
            
            if default_cep:
                df_s['cep'] = df_s.get('cep', '').replace('', default_cep).replace('nan', default_cep)
            
            for date_col in ['cadastro', 'aniversario']:
                if date_col in df_s.columns:
                    dates = pd.to_datetime(df_s[date_col], format='%Y-%m-%d', errors='coerce')
                    df_s[date_col] = dates.dt.strftime('%d/%m/%Y').fillna('01/01/1900')
                    df_s.loc[df_s[date_col] == 'NaT', date_col] = '01/01/1900'
        
        # CEP lookup for missing city/UF in clients
        if ibge_lookup and df_c is not None and 'cep' in df_c.columns:
            from src.cep_lookup import lookup_cep
            missing = df_c['municipio'].isin(['', '\\N', 'nan']) | df_c['uf'].isin(['', '\\N', 'nan'])
            has_cep = ~df_c['cep'].isin(['', '\\N', 'nan'])
            need = missing & has_cep
            if need.any():
                for idx in df_c[need].index:
                    result = lookup_cep(df_c.at[idx, 'cep'])
                    if result:
                        if df_c.at[idx, 'municipio'] in ['', '\\N', 'nan']:
                            df_c.at[idx, 'municipio'] = result['localidade']
                        if df_c.at[idx, 'uf'] in ['', '\\N', 'nan']:
                            df_c.at[idx, 'uf'] = result['uf']
        
        # CEP lookup for missing city/UF in suppliers
        if ibge_lookup and df_s is not None and 'cep' in df_s.columns:
            from src.cep_lookup import lookup_cep
            missing = df_s['municipio'].isin(['', '\\N', 'nan']) | df_s['uf'].isin(['', '\\N', 'nan'])
            has_cep = ~df_s['cep'].isin(['', '\\N', 'nan'])
            need = missing & has_cep
            if need.any():
                for idx in df_s[need].index:
                    result = lookup_cep(df_s.at[idx, 'cep'])
                    if result:
                        if df_s.at[idx, 'municipio'] in ['', '\\N', 'nan']:
                            df_s.at[idx, 'municipio'] = result['localidade']
                        if df_s.at[idx, 'uf'] in ['', '\\N', 'nan']:
                            df_s.at[idx, 'uf'] = result['uf']
        
        # Collect unique city/UF pairs for batched IBGE lookup (from enriched data)
        city_uf_codes = {}
        if ibge_lookup:
            unique_cities = set()
            for df_src in [df_c, df_s]:
                if df_src is not None and 'municipio' in df_src.columns:
                    cidades = df_src['municipio'].fillna('').astype(str).str.strip()
                    ufs = df_src['uf'].fillna('').astype(str).str.strip()
                    mask = (cidades != '') & (cidades != 'nan')
                    ufs_clean = ufs.where((ufs != '') & (ufs != 'nan'), other='')
                    unique_cities.update(zip(cidades[mask], ufs_clean[mask]))
            
            for cidade, uf in unique_cities:
                code = ibge_lookup.get_code(cidade, uf)
                city_uf_codes[(cidade, uf)] = code if code else ''
        
        # IBGE lookup for clients
        df_all = None
        if df_c is not None:
            if ibge_lookup:
                def lookup_ibge(row):
                    cidade = str(row.get('municipio', '')).strip()
                    uf = str(row.get('uf', '')).strip()
                    if not cidade or cidade == 'nan':
                        return ''
                    code = city_uf_codes.get((cidade, uf), '')
                    if code:
                        return code
                    if uf:
                        code = city_uf_codes.get((cidade, ''), '')
                        if code:
                            return code
                    return ibge_lookup.get_code(cidade, uf)
                df_c['ibge'] = df_c.apply(lookup_ibge, axis=1)
                # CEP fallback for records still without IBGE
                from src.cep_lookup import lookup_cep
                no_ibge = df_c['ibge'].isin(['', '\\N', 'nan'])
                has_cep = ~df_c['cep'].isin(['', '\\N', 'nan'])
                need_cep = no_ibge & has_cep
                for idx in df_c[need_cep].index:
                    result = lookup_cep(df_c.at[idx, 'cep'])
                    if result and result.get('ibge'):
                        df_c.at[idx, 'ibge'] = result['ibge']
                        if df_c.at[idx, 'municipio'] in ['', '\\N', 'nan']:
                            df_c.at[idx, 'municipio'] = result['localidade']
                        if df_c.at[idx, 'uf'] in ['', '\\N', 'nan']:
                            df_c.at[idx, 'uf'] = result['uf']
            else:
                df_c['ibge'] = ''
            df_all = df_c
        
        # IBGE lookup for suppliers
        if df_s is not None:
            if ibge_lookup:
                def lookup_ibge_s(row):
                    cidade = str(row.get('municipio', '')).strip()
                    uf = str(row.get('uf', '')).strip()
                    if not cidade or cidade == 'nan':
                        return ''
                    code = city_uf_codes.get((cidade, uf), '')
                    if code:
                        return code
                    if uf:
                        code = city_uf_codes.get((cidade, ''), '')
                        if code:
                            return code
                    return ibge_lookup.get_code(cidade, uf)
                df_s['ibge'] = df_s.apply(lookup_ibge_s, axis=1)
                # CEP fallback for records still without IBGE
                from src.cep_lookup import lookup_cep
                no_ibge = df_s['ibge'].isin(['', '\\N', 'nan'])
                has_cep = ~df_s['cep'].isin(['', '\\N', 'nan'])
                need_cep = no_ibge & has_cep
                for idx in df_s[need_cep].index:
                    result = lookup_cep(df_s.at[idx, 'cep'])
                    if result and result.get('ibge'):
                        df_s.at[idx, 'ibge'] = result['ibge']
                        if df_s.at[idx, 'municipio'] in ['', '\\N', 'nan']:
                            df_s.at[idx, 'municipio'] = result['localidade']
                        if df_s.at[idx, 'uf'] in ['', '\\N', 'nan']:
                            df_s.at[idx, 'uf'] = result['uf']
            else:
                df_s['ibge'] = ''
            
            df_all = pd.concat([df_all, df_s], ignore_index=True) if df_all is not None else df_s
        
        if df_all is None:
            df_all = pd.DataFrame()
        
        # Ensure template columns exist
        template_cols = ['codigo', 'razao', 'fantasia', 'cpf cnpj', 'tipo', 'rg ie', 'im',
                       'logradouro', 'numero', 'complemento', 'cep', 'bairro', 'ibge',
                       'municipio', 'uf', 'cadastro', 'aniversario', 'email', 'fone resid',
                       'fone comercial', 'celular', 'limite', 'val receber', 'dt vencimento',
                       'id classificacao tributaria', 'Observação']
        
        for col in template_cols:
            if col not in df_all.columns:
                df_all[col] = ''
        
        df_all = df_all[template_cols]
        
        # Handle records without IBGE according to user preference
        if handle_missing == 'remove':
            before = len(df_all)
            df_all = df_all[df_all['ibge'].astype(bool)].copy()
            logging.info(f'Removed {before - len(df_all)} records without location data')
        elif handle_missing == 'fill' and (fill_city or fill_uf):
            missing = ~df_all['ibge'].astype(bool)
            ct = missing.sum()
            if ct:
                if fill_city:
                    df_all.loc[missing, 'municipio'] = fill_city
                if fill_uf:
                    df_all.loc[missing, 'uf'] = fill_uf
                if ibge_lookup and fill_city:
                    code = ibge_lookup.get_code(fill_city, fill_uf)
                    if code:
                        df_all.loc[missing, 'ibge'] = code
                logging.info(f'Filled location data for {ct} records ({fill_city}/{fill_uf})')
        
        logging.info(f'Converted {len(df_all)} client/supplier records')
        return df_all
