import requests
import logging
import re
import time

VIA_CEP_URL = 'https://viacep.com.br/ws/{cep}/json/'
AWESOME_API_URL = 'https://cep.awesomeapi.com.br/json/{cep}'
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 0.35

# Generic locality CEPs that APIs cannot resolve (e.g., central CEP of a city)
_CEP_OVERRIDES = {
    '59600000': {'localidade': 'Mossoró', 'uf': 'RN', 'ibge': '2408003'},
}

_cache = {}


def _format_cep(cep: str) -> str:
    digits = re.sub(r'\D', '', cep)
    if len(digits) == 7:
        yield '0' + digits
        return
    if len(digits) == 8:
        yield digits
        return
    if len(digits) > 8:
        yield digits[:8]


def _viacep(cep: str) -> dict | None:
    time.sleep(REQUEST_DELAY)
    url = VIA_CEP_URL.format(cep=cep)
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code == 200:
        data = resp.json()
        if 'erro' not in data:
            return {
                'cep': data.get('cep', ''),
                'localidade': data.get('localidade', ''),
                'uf': data.get('uf', ''),
                'ibge': data.get('ibge', ''),
            }
    return None


def _awesomeapi(cep: str) -> dict | None:
    time.sleep(REQUEST_DELAY)
    url = AWESOME_API_URL.format(cep=cep)
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code == 200:
        data = resp.json()
        if 'city' in data and 'state' in data:
            return {
                'cep': data.get('cep', ''),
                'localidade': data.get('city', ''),
                'uf': data.get('state', ''),
                'ibge': data.get('ibge', ''),
            }
    return None


_SOURCES = [_viacep, _awesomeapi]


def lookup_cep(cep: str) -> dict | None:
    if not cep:
        return None
    for formatted in _format_cep(cep):
        if formatted in _cache:
            return _cache[formatted]
        if formatted in _CEP_OVERRIDES:
            result = _CEP_OVERRIDES[formatted].copy()
            _cache[formatted] = result
            return result
        for source in _SOURCES:
            try:
                result = source(formatted)
                if result:
                    _cache[formatted] = result
                    return result
            except requests.RequestException as e:
                logging.warning(f'{source.__name__} error for CEP {formatted}: {e}')
            except Exception as e:
                logging.warning(f'Unexpected {source.__name__} error for CEP {formatted}: {e}')
    return None
