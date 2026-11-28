# servicios/empleados.py
# Capa de servicio: comprueba el permiso y luego llama al DAO.
# Trayecto de cada acción:  menú -> servicio (permiso + reglas) -> DAO (SQL)
from departamento import Departamento
from empleado import Empleado
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from servicios.permisos import campo, exigir_admin, exigir_sesion


def registrar_empleado(usuario, nombre, correo):
    exigir_admin(usuario)
    empleado = Empleado(nombre=nombre, correo=correo)       # valida (ValueError)
    if EmpleadoDAO.buscar_por_correo(empleado.correo) is not None:
        raise ValueError("Ya existe un empleado con ese correo.")
    return EmpleadoDAO.insertar(empleado)


def listar_empleados(usuario):
    exigir_admin(usuario)
    return EmpleadoDAO.listar()


def buscar_empleado(usuario, id_empleado):
    exigir_admin(usuario)
    return EmpleadoDAO.buscar_por_id(id_empleado)


def actualizar_correo(usuario, empleado, nuevo_correo):
    exigir_admin(usuario)
    nuevo_correo = Empleado.validar_correo(nuevo_correo)
    otro = EmpleadoDAO.buscar_por_correo(nuevo_correo)
    if otro is not None and otro.id != empleado.id:
        raise ValueError("Ya existe un empleado con ese correo.")
    empleado.correo = nuevo_correo
    return EmpleadoDAO.actualizar(empleado)


def eliminar_empleado(usuario, id_empleado):
    exigir_admin(usuario)
    return EmpleadoDAO.eliminar(id_empleado)


def crear_departamento(usuario, nombre, descripcion=""):
    exigir_admin(usuario)
    return DepartamentoDAO.insertar(Departamento(nombre, descripcion))


def listar_departamentos(usuario):
    exigir_admin(usuario)
    return DepartamentoDAO.listar()


def asignar_departamento(usuario, empleado, departamento):
    """El dominio relaciona los objetos; el DAO guarda la clave foránea."""
    exigir_admin(usuario)
    departamento.agregar_empleado(empleado)
    return EmpleadoDAO.actualizar_departamento(empleado)


def consultar_departamento(usuario, id_departamento):
    exigir_admin(usuario)
    return DepartamentoDAO.buscar_con_empleados(id_departamento)


def datos_para_reportes(usuario, id_departamento):
    """Devuelve (lista general de empleados, departamento completo o None)."""
    exigir_admin(usuario)
    departamento = DepartamentoDAO.buscar_con_empleados(id_departamento)
    if departamento is None:
        return None, None
    return EmpleadoDAO.listar(), departamento


def consultar_mi_ficha(usuario):
    """El ID sale de la sesión: nadie puede pedir la ficha de otra persona aquí."""
    exigir_sesion(usuario)
    return EmpleadoDAO.buscar_por_id(campo(usuario, "empleado_id"))
