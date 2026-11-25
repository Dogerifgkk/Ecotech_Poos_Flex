# servicios/autenticacion.py
import bcrypt

from dominio.usuario import Usuario
from persistencia.conexion import ErrorIntegridad
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.usuario_dao import UsuarioDAO

MAX_BYTES_BCRYPT = 72


def crear_hash(clave):
    """Valida la clave y devuelve el hash (con sal aleatoria incluida)."""
    clave = Usuario.validar_clave(clave)
    clave_bytes = clave.encode("utf-8")
    if len(clave_bytes) > MAX_BYTES_BCRYPT:
        raise ValueError("Máximo 72 bytes UTF-8 para bcrypt.")
    return bcrypt.hashpw(clave_bytes, bcrypt.gensalt()).decode("utf-8")


def registrar_usuario(nombre, clave, empleado_id, rol="empleado"):
    """Crea una cuenta vinculada a un empleado existente.
    Por defecto recibe el menor permiso ('empleado')."""
    password_hash = crear_hash(clave)                       # valida la clave
    usuario = Usuario(nombre_usuario=nombre, password_hash=password_hash,
                      empleado_id=empleado_id, rol=rol)     # valida el resto
    if EmpleadoDAO.buscar_por_id(empleado_id) is None:
        raise ValueError("No existe un empleado con ese ID.")
    if UsuarioDAO.buscar_por_nombre(usuario.nombre_usuario) is not None:
        raise ValueError("Ese nombre de usuario ya está en uso.")
    if UsuarioDAO.buscar_por_empleado_id(empleado_id) is not None:
        raise ValueError("Ese empleado ya tiene una cuenta.")
    try:
        UsuarioDAO.insertar(usuario)
    except ErrorIntegridad as error:    # por si dos personas registran a la vez
        raise ValueError("No se pudo crear la cuenta: usuario o empleado ya registrado.") from error
    return usuario


def autenticar(nombre, clave):
    """Devuelve el Usuario si las credenciales son correctas; si no, None.
    Los fallos de BD (ErrorBD) NO se convierten en acceso: se propagan."""
    nombre = Usuario.normalizar_usuario(nombre)
    if not isinstance(clave, str):
        return None
    datos = clave.encode("utf-8")
    if not 0 < len(datos) <= MAX_BYTES_BCRYPT:
        return None
    cuenta = UsuarioDAO.buscar_por_nombre(nombre)
    if cuenta is None:
        return None
    if not bcrypt.checkpw(datos, cuenta.password_hash.encode("utf-8")):
        return None
    return cuenta


def crear_cuenta_empleado(usuario_actual, nombre, clave, empleado_id):
    """Acción administrativa: solo un admin crea cuentas, siempre con rol 'empleado'.
    El permiso se comprueba ANTES de tocar la BD."""
    from servicios.permisos import exigir_admin
    exigir_admin(usuario_actual)
    return registrar_usuario(nombre, clave, empleado_id, rol="empleado")
