import json
import os
import logging
import re
import requests
import unicodedata


def normalize(text: str) -> str:
    """Remove acentos, pontuação, lower case, trim"""
    if not text or text == 'nan':
        return ''
    text = unicodedata.normalize('NFKD', str(text))
    text = text.encode('ascii', 'ignore').decode('ascii')
    for ch in ["'", '"', "`", "´"]:
        text = text.replace(ch, '')
    # Strip " - " suffix (neighborhood appended to city name, e.g. "JABOATAO - GAL PIEDADE")
    text = text.split(' - ')[0]
    # Remove spaces in Portuguese contractions (e.g. "d oeste" -> "doeste" to match "doeste")
    text = re.sub(r'\b([dD])\s+(?=[aeiouAEIOU])', r'\1', text)
    return text.strip().lower()


# City name aliases: SGA name -> official IBGE name
_CITY_ALIASES = {
    'acu': 'assu',
    'açu': 'assu',
    'mossoró': 'mossoro',
    'mossoro': 'mossoro',
    'augusto severo': 'campo grande',
    'sao luiz': 'sao luis',
    'olho dagua do borges': 'olho d agua do borges',
    'moji mirim': 'mogi mirim',
    'v constança': 'sao paulo',
    'vila constanca': 'sao paulo',
}


def resolve_city_alias(name: str) -> str:
    """Resolve common city name variations to official IBGE names"""
    normalized = normalize(name)
    # Try direct alias
    if normalized in _CITY_ALIASES:
        return _CITY_ALIASES[normalized]
    # Try removing special chars
    clean = normalized.replace('-', ' ').replace("'", '').replace('"', '')
    if clean != normalized and clean in _CITY_ALIASES:
        return _CITY_ALIASES[clean]
    return normalized


_UF_BY_CITY_CACHE = None


def build_uf_fallback():
    """Build a dict of city->UF from known cities"""
    uf_map = {}
    # Common RN cities (primary region)
    rn_cities = {
        'mossoro', 'acu', 'assu', 'barauna', 'itaja', 'caraubas',
        'antonio martins', 'agua nova', 'angicos', 'areia branca',
        'campo grande', 'fatima', 'governador dix-sept rosado',
        'grossos', 'ipanguacu', 'itau', 'jandaira', 'marcelino vieira',
        'parau', 'parnamirim', 'pau dos ferros', 'porto do mangue',
        'ribeira', 'rodolfo fernandes', 'ruy barbosa', 'sao miguel',
        'serra do mel', 'tibau', 'timbauba dos batistas',
        'uparema', 'varzea', 'venha-ver', 'almino afonso',
        'apodi', 'areia branca', 'carnaubais', 'fernando pedroza',
        'ipueira', 'lucrecia', 'martins', 'olho-dagua do borges',
        'patu', 'raphael fernandes', 'santana do matos',
        'sao jose de mipibu', 'sao rafael', 'sergio de sa',
        'taboleiro grande', 'touros', 'triunfo potiguar',
        'upanema', 'vera cruz',
    }
    for c in rn_cities:
        uf_map[c] = 'rn'

    ce_cities = {
        'quixere', 'icapui', 'aracati', 'jaguaruana', 'limoeiro do norte',
        'morada nova', 'russas', 'tabuleiro do norte',
    }
    for c in ce_cities:
        uf_map[c] = 'ce'

    pb_cities = {'cajazeiras', 'sousa', 'patos', 'joao pessoa', 'campina grande'}
    for c in pb_cities:
        uf_map[c] = 'pb'

    pe_cities = {'recife', 'caruaru', 'petrolina', 'olinda'}
    for c in pe_cities:
        uf_map[c] = 'pe'

    return uf_map


def get_uf_fallback(city_normalized: str) -> str:
    global _UF_BY_CITY_CACHE
    if _UF_BY_CITY_CACHE is None:
        _UF_BY_CITY_CACHE = build_uf_fallback()
    return _UF_BY_CITY_CACHE.get(city_normalized, '')


class IBGELookup:
    """Lookup IBGE municipality codes with accent-robust matching"""
    
    def __init__(self, cache_file='config/ibge_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self._build_normalized_index()
    
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f'Error loading IBGE cache: {e}')
        return {}
    
    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f'Error saving IBGE cache: {e}')
    
    def _build_normalized_index(self):
        """Build index of normalized keys -> codes with alias resolution"""
        self.norm_index = {}
        for key, code in self.cache.items():
            parts = key.rsplit('-', 1)
            if len(parts) == 2:
                city_norm = normalize(parts[0])
                uf_norm = normalize(parts[1])
                self.norm_index[(city_norm, uf_norm)] = code
                if city_norm not in self.norm_index:
                    self.norm_index[city_norm] = code
                # Index alias names too
                alias_norm = resolve_city_alias(parts[0])
                if alias_norm != city_norm:
                    self.norm_index[(alias_norm, uf_norm)] = code
                    if alias_norm not in self.norm_index:
                        self.norm_index[alias_norm] = code
    
    def get_code(self, city_name, uf):
        """Get IBGE code with multiple fallback strategies"""
        city_norm = normalize(city_name)
        uf_norm = normalize(uf)
        
        if not city_norm:
            return ''
        
        # Strategy 1: Exact match (normalized city + UF)
        key = (city_norm, uf_norm)
        if key in self.norm_index:
            return self.norm_index[key]
        
        # Strategy 1b: Try alias resolution (e.g., "acu" -> "assu")
        alias_norm = resolve_city_alias(city_name)
        if alias_norm != city_norm:
            alias_key = (alias_norm, uf_norm)
            if alias_key in self.norm_index:
                return self.norm_index[alias_key]
        
        # Strategy 2: City-only match (if UF is wrong/empty)
        if city_norm in self.norm_index and isinstance(self.norm_index[city_norm], str):
            return self.norm_index[city_norm]
        
        # Strategy 3: Try with UF fallback (infer UF from known cities)
        if not uf_norm:
            uf_fallback = get_uf_fallback(city_norm)
            if uf_fallback:
                fallback_key = (city_norm, uf_fallback)
                if fallback_key in self.norm_index:
                    return self.norm_index[fallback_key]
        
        # Strategy 4: Search by city name only (check all UFs)
        for key, code in self.norm_index.items():
            if isinstance(key, tuple) and len(key) == 2:
                c, u = key
                if isinstance(c, str) and c == city_norm and isinstance(u, str):
                    return code
        
        # Strategy 5: Try to fetch from API
        try:
            url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                municipalities = response.json()
                for mun in municipalities:
                    mun_norm = normalize(mun['nome'])
                    if mun_norm == city_norm or mun_norm == alias_norm:
                        uf_sigla = mun['microrregiao']['mesorregiao']['UF']['sigla'].lower()
                        code = str(mun['id'])
                        cache_key = f"{mun['nome']}-{uf_sigla}"
                        self.cache[cache_key] = code
                        self._save_cache()
                        self._build_normalized_index()
                        logging.info(f'IBGE fetched for {city_name}-{uf}: {code}')
                        return code
        except Exception as e:
            logging.error(f'Error fetching IBGE for {city_name}-{uf}: {e}')
        
        return ''
