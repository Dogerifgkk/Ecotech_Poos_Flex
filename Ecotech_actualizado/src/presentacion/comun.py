# presentacion/comun.py  (funciones de consola que usan todos los menús)
import logging

from persistencia.conexion import ErrorBD

logger = logging.getLogger("ecotech")


def solicitar_id(mensaje="ID del empleado: "):
    while True:
        texto = input(mensaje).strip()
        try:
            numero = int(texto)
            if numero <= 0:
                raise ValueError("El ID debe ser positivo.")
        except ValueError:
            print("Ingresa un entero mayor que 0.")
        else:
            return numero


def confirmar(pregunta):
    while True:
        respuesta = input(f"{pregunta} (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Responde s o n.")


def leer_validado(etiqueta, validador):
    """Repite SOLO este campo hasta que sea válido. Enter vacío cancela (devuelve None)."""
    while True:
        valor = input(f"{etiqueta} (Enter para cancelar): ")
        if not valor.strip():
            return None
        try:
            return validador(valor)
        except ValueError as error:
            print(f"{etiqueta} inválido: {error}")


def ejecutar_seguro(accion, *args):
    """Ejecuta una acción del menú y explica los fallos sin cerrar el programa."""
    try:
        accion(*args)
    except PermissionError as error:
        print(f"Permiso denegado: {error}")
    except ErrorBD:
        logger.exception("Fallo en la base de datos.")
        print("No se pudo completar la operación en la BD.")
