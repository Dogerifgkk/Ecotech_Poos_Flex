# servicios/indicadores.py  (permisos y coordinación: API -> objeto -> BD)
import requests

from persistencia.indicador_dao import IndicadorDAO
from servicios.api_indicadores import CODIGOS, obtener_indicador
from servicios.permisos import exigir_admin, exigir_sesion


def _validar_codigo(codigo):
    if codigo not in CODIGOS:
        raise ValueError("Indicador no disponible. Use: " + ", ".join(CODIGOS) + ".")
    return codigo


def actualizar_indicador(usuario, codigo="uf"):
    """Solo admin. Devuelve (Indicador|None, 'api'|'respaldo').
    Si la API falla, usa el último valor guardado en la BD local."""
    exigir_admin(usuario)
    _validar_codigo(codigo)
    try:
        indicador = obtener_indicador(codigo)
    except (requests.RequestException, ValueError):
        return IndicadorDAO.ultimo(codigo), "respaldo"
    IndicadorDAO.guardar(indicador)       # el commit ocurre dentro de guardar()
    return indicador, "api"


def actualizar_uf(usuario):
    return actualizar_indicador(usuario, "uf")


def consultar_guardado(usuario, codigo="uf"):
    """Admin y empleado pueden consultar el último valor guardado (sin Internet)."""
    exigir_sesion(usuario)
    _validar_codigo(codigo)
    return IndicadorDAO.ultimo(codigo)
