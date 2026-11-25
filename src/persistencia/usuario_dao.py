# persistencia/usuario_dao.py
from persistencia.conexion import marcador, transaccion
from dominio.usuario import Usuario

_SELECT = "SELECT id, empleado_id, nombre_usuario, password_hash, rol FROM usuario"


def _construir(fila):
    id_u, id_e, nombre, hash_, rol = fila
    return Usuario(nombre_usuario=nombre, password_hash=hash_,
                   empleado_id=id_e, id=id_u, rol=rol)


class UsuarioDAO:
    @staticmethod
    def insertar(usuario: Usuario):
        """Guarda la cuenta. Lanza ErrorIntegridad si el usuario o el empleado
        ya tienen cuenta, o si el empleado no existe."""
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                "INSERT INTO usuario (empleado_id, nombre_usuario, password_hash, rol) "
                f"VALUES ({m}, {m}, {m}, {m})",
                (usuario.empleado_id, usuario.nombre_usuario,
                 usuario.password_hash, usuario.rol),
            )
            usuario.id = cursor.lastrowid
        return usuario

    @staticmethod
    def buscar_por_nombre(nombre_usuario):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(f"{_SELECT} WHERE nombre_usuario = {m}", (nombre_usuario,))
            fila = cursor.fetchone()
        return None if fila is None else _construir(fila)

    @staticmethod
    def buscar_por_empleado_id(empleado_id):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(f"{_SELECT} WHERE empleado_id = {m}", (empleado_id,))
            fila = cursor.fetchone()
        return None if fila is None else _construir(fila)

    @staticmethod
    def contar():
        with transaccion() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuario")
            return cursor.fetchone()[0]
