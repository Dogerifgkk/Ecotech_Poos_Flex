# persistencia/empleado_dao.py
from persistencia.conexion import abrir_conexion, obtener_motor
from empleado import Empleado


class EmpleadoDAO:
    @staticmethod
    def insertar(empleado: Empleado):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        m = "?" if obtener_motor() == "sqlite" else "%s"
        cursor.execute(
            f"INSERT INTO empleado (nombre, correo) VALUES ({m}, {m})",
            (empleado.nombre, empleado.correo),
        )
        empleado.id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return empleado

    @staticmethod
    def listar():
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, correo FROM empleado ORDER BY id")
        filas = cursor.fetchall()
        conexion.close()
        return [Empleado(nombre=n, correo=c, id=i) for i, n, c in filas]

    @staticmethod
    def buscar_por_id(id_empleado):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        m = "?" if obtener_motor() == "sqlite" else "%s"
        cursor.execute(
            f"SELECT id, nombre, correo FROM empleado WHERE id = {m}",
            (id_empleado,),
        )
        fila = cursor.fetchone()
        conexion.close()
        if fila is None:
            return None
        return Empleado(nombre=fila[1], correo=fila[2], id=fila[0])

    @staticmethod
    def actualizar_departamento(empleado):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        m = "?" if obtener_motor() == "sqlite" else "%s"
        dep_id = empleado.departamento.id if empleado.departamento else None
        cursor.execute(
            f"UPDATE empleado SET departamento_id = {m} WHERE id = {m}",
            (dep_id, empleado.id),
        )
        filas = cursor.rowcount
        conexion.commit()
        conexion.close()
        return filas