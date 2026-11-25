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


def extraer_primero(datos, codigo=None):
    """Adaptador: del JSON crudo toma la primera observación y devuelve un Indicador.
    Formato de la clase: {"codigo": "uf", "serie": [{"fecha": ..., "valor": ...}]}.
    También acepta las claves en inglés (code/series/date/value) y un envoltorio "data"."""
    if not isinstance(datos, dict):
        raise ValueError("Respuesta de la API no válida.")
    if isinstance(datos.get("data"), dict):
        datos = datos["data"]
    if codigo and isinstance(datos.get(codigo), dict):
        datos = datos[codigo]
    codigo_api = _primero(datos, "codigo", "code")
    serie = _primero(datos, "serie", "series")
    if not isinstance(serie, list) or not serie or not isinstance(serie[0], dict):
        raise ValueError("La respuesta no trae observaciones.")
    if codigo and codigo_api and str(codigo_api).strip().lower() != codigo:
        raise ValueError("La API devolvió otro indicador.")
    observacion = serie[0]
    return Indicador(
        codigo_api if codigo_api is not None else codigo,
        _primero(observacion, "fecha", "date"),
        _primero(observacion, "valor", "value"),
    )


def obtener_indicador(codigo="uf"):
    return extraer_primero(obtener_json(), codigo)


def obtener_uf():
    return obtener_indicador("uf")
