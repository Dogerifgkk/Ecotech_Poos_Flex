# persistencia/departamento_dao.py
from persistencia.conexion import marcador, transaccion
from departamento import Departamento
from empleado import Empleado


def reconstruir_departamento(filas):
    """filas: (dep_id, dep_nombre, emp_id, emp_nombre, emp_correo) por cada empleado."""
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
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                f"INSERT INTO departamento (nombre, descripcion) VALUES ({m}, {m})",
                (departamento.nombre, departamento.descripcion),
            )
            departamento.id = cursor.lastrowid
        return departamento

    @staticmethod
    def listar():
        with transaccion() as cursor:
            cursor.execute("SELECT id, nombre, descripcion FROM departamento ORDER BY id")
            filas = cursor.fetchall()
        return [Departamento(n, d or "", id=i) for i, n, d in filas]

    @staticmethod
    def buscar_con_empleados(id_dep):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                f"""SELECT d.id, d.nombre, e.id AS id_e, e.nombre AS nombre_e, e.correo
                    FROM departamento d
                    LEFT JOIN empleado e ON e.departamento_id = d.id
                    WHERE d.id = {m}
                    ORDER BY e.id""",
                (id_dep,),
            )
            filas = cursor.fetchall()
        return reconstruir_departamento(filas)
