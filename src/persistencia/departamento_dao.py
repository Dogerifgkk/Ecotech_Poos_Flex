# persistencia/departamento_dao.py
from persistencia.conexion import abrir_conexion, obtener_motor
from departamento import Departamento
from empleado import Empleado


def reconstruir_departamento(filas):
    if not filas:
        return None
    departamento = Departamento(filas[0][1], id=filas[0][0])
    for _, _, id_emp, nombre, correo in filas:
        if id_emp is not None:
            empleado = Empleado(nombre, correo, id=id_emp)
            departamento.agregar_empleado(empleado)
    return departamento


class DepartamentoDAO:
    @staticmethod
    def insertar(departamento):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        m = "?" if obtener_motor() == "sqlite" else "%s"
        cursor.execute(
            f"INSERT INTO departamento (nombre, descripcion) VALUES ({m}, {m})",
            (departamento.nombre, departamento.descripcion),
        )
        departamento.id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return departamento

    @staticmethod
    def listar():
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, descripcion FROM departamento ORDER BY id")
        filas = cursor.fetchall()
        conexion.close()
        return [Departamento(n, d or "", id=i) for i, n, d in filas]

    @staticmethod
    def buscar_con_empleados(id_dep):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        m = "?" if obtener_motor() == "sqlite" else "%s"
        cursor.execute(
            f"""SELECT d.id, d.nombre, e.id, e.nombre, e.correo
                FROM departamento d
                LEFT JOIN empleado e ON e.departamento_id = d.id
                WHERE d.id = {m}
                ORDER BY e.id""",
            (id_dep,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return reconstruir_departamento(filas)