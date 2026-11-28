# servicios/permisos.py
# Autenticar = "¿quién eres?"  Autorizar = "¿puedes hacer esto?"
# Estas funciones se llaman ANTES de tocar el DAO o la API.
from dominio.usuario import ROLES, Usuario


def campo(sesion, nombre):
    """Lee un dato de la sesión (acepta un Usuario o un diccionario)."""
    if isinstance(sesion, dict):
        return sesion.get(nombre)
    return getattr(sesion, nombre, None)


def exigir_sesion(sesion):
    if not isinstance(sesion, (Usuario, dict)):
        raise PermissionError("Inicie sesión.")
    if campo(sesion, "rol") not in ROLES:
        raise PermissionError("Acceso no permitido.")
    empleado_id = campo(sesion, "empleado_id")
    if type(empleado_id) is not int or empleado_id <= 0:
        raise PermissionError("Sesión inválida.")


def exigir_admin(sesion):
    exigir_sesion(sesion)
    if campo(sesion, "rol") != "admin":
        raise PermissionError("Acción solo para administrador.")
