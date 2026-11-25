# persistencia/empleado_dao.py
from persistencia.conexion import marcador, transaccion
from empleado import Empleado
from departamento import Departamento

_SELECT = """SELECT e.id, e.nombre, e.correo, d.id, d.nombre, d.descripcion
             FROM empleado e
             LEFT JOIN departamento d ON d.id = e.departamento_id"""


def _construir(fila):
    """Convierte una fila SQL en un Empleado (con su Departamento si lo tiene)."""
    id_e, nombre, correo, id_d, nombre_d, desc_d = fila
    empleado = Empleado(nombre=nombre, correo=correo, id=id_e)
    if id_d is not None:
        empleado.departamento = Departamento(nombre_d, desc_d or "", id=id_d)
    return empleado


class EmpleadoDAO:
    @staticmethod
    def insertar(empleado: Empleado):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                f"INSERT INTO empleado (nombre, correo) VALUES ({m}, {m})",
                (empleado.nombre, empleado.correo),
            )
            empleado.id = cursor.lastrowid
        return empleado

    @staticmethod
    def listar():
        with transaccion() as cursor:
            cursor.execute(f"{_SELECT} ORDER BY e.id")
            filas = cursor.fetchall()
        return [_construir(f) for f in filas]

    @staticmethod
    def buscar_por_id(id_empleado):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(f"{_SELECT} WHERE e.id = {m}", (id_empleado,))
            fila = cursor.fetchone()
        return None if fila is None else _construir(fila)

    @staticmethod
    def buscar_por_correo(correo):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(f"{_SELECT} WHERE e.correo = {m}", (correo,))
            fila = cursor.fetchone()
        return None if fila is None else _construir(fila)

    @staticmethod
    def actualizar(empleado: Empleado):
        """Guarda nombre y correo. Devuelve cuántas filas cambió (1 si existe)."""
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                f"UPDATE empleado SET nombre = {m}, correo = {m} WHERE id = {m}",
                (empleado.nombre, empleado.correo, empleado.id),
            )
            return cursor.rowcount

    @staticmethod
    def actualizar_departamento(empleado: Empleado):
        m = marcador()
        dep_id = empleado.departamento.id if empleado.departamento else None
        with transaccion() as cursor:
            cursor.execute(
                f"UPDATE empleado SET departamento_id = {m} WHERE id = {m}",
                (dep_id, empleado.id),
            )
            return cursor.rowcount

    @staticmethod
    def eliminar(id_empleado):
        """Borra por ID. Lanza ErrorIntegridad si otra tabla lo referencia
        (por ejemplo, si el empleado tiene una cuenta de usuario)."""
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(f"DELETE FROM empleado WHERE id = {m}", (id_empleado,))
            return cursor.rowcount
