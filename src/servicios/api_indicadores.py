# servicios/api_indicadores.py  (solo HTTP y JSON; no toca la BD)
import requests

from dominio.indicador import Indicador

URL = "https://api.boostr.cl/economy/indicators.json"
TIMEOUT = (3, 5)      # (segundos para conectar, segundos para leer)
CODIGOS = ("uf", "dolar")


def obtener_json():
    respuesta = requests.get(URL, timeout=TIMEOUT)
    respuesta.raise_for_status()     # error HTTP -> excepción
    return respuesta.json()          # texto JSON -> dict/list de Python


def _primero(diccionario, *claves):
    for clave in claves:
        if clave in diccionario:
            return diccionario[clave]
    return None


def _buscar_item(datos, codigo):
    """Ubica el diccionario del indicador dentro del JSON, sea cual sea su envoltorio:
    {"data": {...}}, {"data": [ {...}, {...} ]} o {"uf": {...}, "dolar": {...}}."""
    if isinstance(datos, dict) and "data" in datos:
        datos = datos["data"]
    if isinstance(datos, list):
        for elemento in datos:
            if isinstance(elemento, dict):
                cod = _primero(elemento, "codigo", "code")
                if codigo is None or str(cod).strip().lower() == codigo:
                    return elemento
        raise ValueError("La API no trae el indicador pedido.")
    if not isinstance(datos, dict):
        raise ValueError("Respuesta de la API no válida.")
    if codigo and isinstance(datos.get(codigo), dict):
        return datos[codigo]
    return datos


def extraer_primero(datos, codigo=None):
    """Adaptador: del JSON crudo toma la primera observación y devuelve un Indicador.
    Formato de la clase: {"codigo": "uf", "serie": [{"fecha": ..., "valor": ...}]}.
    También acepta claves en inglés (code/series/date/value), el envoltorio "data",
    una lista de indicadores y un indicador "plano" (con value/date sin serie)."""
    if not isinstance(datos, (dict, list)):
        raise ValueError("Respuesta de la API no válida.")
    item = _buscar_item(datos, codigo)
    codigo_api = _primero(item, "codigo", "code")
    if codigo and codigo_api and str(codigo_api).strip().lower() != codigo:
        raise ValueError("La API devolvió otro indicador.")
    serie = _primero(item, "serie", "series")
    if isinstance(serie, list) and serie and isinstance(serie[0], dict):
        observacion = serie[0]
    elif _primero(item, "valor", "value") is not None:
        observacion = item                      # indicador plano, sin serie
    else:
        raise ValueError("La respuesta no trae observaciones.")
    return Indicador(
        codigo_api if codigo_api is not None else codigo,
        _primero(observacion, "fecha", "date"),
        _primero(observacion, "valor", "value"),
    )


def obtener_indicador(codigo="uf"):
    return extraer_primero(obtener_json(), codigo)


def obtener_uf():
    return obtener_indicador("uf")
