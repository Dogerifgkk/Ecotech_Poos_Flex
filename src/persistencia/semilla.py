# persistencia/semilla.py
# Esquema -> Semilla -> Consulta. La semilla inserta solo lo que FALTA,
# así puede ejecutarse muchas veces sin duplicar datos. Todos los datos son ficticios.
from departamento import Departamento
from empleado import Empleado
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.usuario_dao import UsuarioDAO

DEPARTAMENTOS = [
    ("Soporte", "Atención y soporte técnico"),
    ("Ventas", "Área comercial"),
    ("Recursos Humanos", "Gestión de personas"),
    ("Finanzas", "Departamento sin empleados"),
]

EMPLEADOS = [
    ("administrador ecotech", "admin@ecotech.cl", "Recursos Humanos"),
    ("ana lopez", "ana@ecotech.cl", "Soporte"),
    ("luis perez", "luis@ecotech.cl", "Soporte"),
    ("marta rojas", "marta@ecotech.cl", "Ventas"),
    ("pedro soto", "pedro@ecotech.cl", None),   # sin departamento y sin cuenta
]

# (usuario, contraseña de prueba, correo del empleado, rol)
CUENTAS = [
    ("admin", "Admin2026!", "admin@ecotech.cl", "admin"),
    ("ana_lopez", "Ana2026!", "ana@ecotech.cl", "empleado"),
    ("luis_perez", "Luis2026!", "luis@ecotech.cl", "empleado"),
]


def sembrar():
    from servicios.autenticacion import registrar_usuario   # evita ciclos al importar

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

    for usuario, clave, correo, rol in CUENTAS:
        if UsuarioDAO.buscar_por_nombre(usuario) is not None:
            continue
        empleado = EmpleadoDAO.buscar_por_correo(correo)
        if empleado is not None and UsuarioDAO.buscar_por_empleado_id(empleado.id) is None:
            registrar_usuario(usuario, clave, empleado.id, rol=rol)
