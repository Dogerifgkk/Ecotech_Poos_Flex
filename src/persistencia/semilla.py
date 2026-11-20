# persistencia/semilla.py
from departamento import Departamento
from empleado import Empleado
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO

DEPARTAMENTOS = [
    ("Soporte", "Atención y soporte técnico"),
    ("Ventas", "Área comercial"),
    ("Recursos Humanos", "Gestión de personas"),
    ("Finanzas", "Departamento sin empleados"),
]

EMPLEADOS = [
    ("ana lopez", "ana@ecotech.cl", "Soporte"),
    ("luis perez", "luis@ecotech.cl", "Soporte"),
    ("marta rojas", "marta@ecotech.cl", "Ventas"),
    ("pedro soto", "pedro@ecotech.cl", None),
]


def sembrar():
    deps = {d.nombre: d for d in DepartamentoDAO.listar()}
    for nombre, descripcion in DEPARTAMENTOS:
        if nombre not in deps:
            deps[nombre] = DepartamentoDAO.insertar(Departamento(nombre, descripcion))

    existentes = {e.correo for e in EmpleadoDAO.listar()}
    for nombre, correo, nombre_dep in EMPLEADOS:
        if correo in existentes:
            continue
        empleado = EmpleadoDAO.insertar(Empleado(nombre, correo))
        if nombre_dep is not None:
            deps[nombre_dep].agregar_empleado(empleado)
            EmpleadoDAO.actualizar_departamento(empleado)