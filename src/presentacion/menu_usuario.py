# presentacion/menu_usuario.py
from getpass import getpass

from dominio.usuario import Usuario
from persistencia.conexion import ErrorBD
from presentacion.comun import logger, solicitar_id
from servicios.autenticacion import autenticar, crear_cuenta_empleado
from servicios.empleados import buscar_empleado
from servicios.permisos import exigir_admin


def solicitar_login():
    nombre = input("Usuario: ")
    clave = getpass("Contraseña: ")
    try:
        usuario = autenticar(nombre, clave)
    except (TypeError, ValueError):
        print("No se pudo validar el acceso.")
        return None
    except ErrorBD:
        logger.exception("Fallo de BD al autenticar.")
        print("No se pudo verificar el acceso en este momento. Intenta más tarde.")
        return None
    if usuario is None:
        print("Usuario o contraseña incorrectos.")
    else:
        print("Sesión iniciada correctamente.")
    return usuario


def crear_cuenta(usuario_actual):
    exigir_admin(usuario_actual)   # primera instrucción de una acción administrativa
    """Opción administrativa: crea la cuenta de un empleado existente."""
    empleado = buscar_empleado(usuario_actual, solicitar_id("ID del empleado para la cuenta: "))
    if empleado is None:
        print("No existe un empleado con ese ID.")
        return
    print(f"Empleado: {empleado.nombre} <{empleado.correo}>")
    nombre = input("Nombre de usuario: ")
    clave = getpass("Contraseña (mínimo 6 caracteres): ")
    repetir = getpass("Repite la contraseña: ")
    if clave != repetir:
        print("Las contraseñas no coinciden. No se creó la cuenta.")
        return
    try:
        cuenta = crear_cuenta_empleado(usuario_actual, nombre, clave, empleado.id)
    except (TypeError, ValueError) as error:
        print(f"No se creó la cuenta: {error}")
    else:
        print(f"Cuenta '{cuenta.nombre_usuario}' creada con rol {cuenta.rol}.")
