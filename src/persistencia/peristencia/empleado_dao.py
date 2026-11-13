# persistencia/empleado_dao.py
from persistencia.conexion import abrir_conexion, obtener_motor
from dominio.empleado import Empleado    #ajusta ruta

class EmpleadoDAO:
    @staticmethod
    def insertar(empleado: Empleado):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        marcador = "?" if obtener_motor() == "sqlite" else "%s"
        
        sql = f""" 
            INSERT INTO empleado (nombre, correo)
            VALUES ({marcador}, {marcador})
        """
        cursor.execute(sql, (empleado.nombre, empleado.correo))
        empleado.id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return empleado
    
    @staticmethod
    def listar():
        conexion = abrir_conexion()
        cursor = conexion.cursor()

        sql = (
            "Select id, nombre, correo"
            "FROM empleado ORDER BY id"
        )
        cursor.execute(sql)
        filas = cursor.fetchall()

        empleados = []
        for id_empleados, nombre , correo in filas:
            empleado = Empleado(
                nombre=nombre, correo=correo, id=id_empleados
            )
            empleados.append(empleado)
            conexion.close()
            return empleados