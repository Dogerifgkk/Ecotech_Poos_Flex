# presentacion/menu_empleados.py
from empleado import Empleado
from departamento import Departamento
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.departamento_dao import DepartamentoDAO
from dominio.reporte import ReporteEmpleados, ReportePorDepartamento

def solicitar_id(mensaje="ID del empleado: "):
    while True:
        texto = input(mensaje).strip()
        try:
            numero = int(texto)
            if numero <= 0:
                raise ValueError("El ID debe ser positivo.")
        except ValueError:
            print("Ingresa un entero mayor que 0.")
        else:
            return numero


def crear_empleado():
    nombre = input("Nombre: ")
    correo = input("Correo: ")
    try:
        empleado = Empleado(nombre=nombre, correo=correo)
        EmpleadoDAO.insertar(empleado)
        print(f"Empleado registrado con id {empleado.id}")
    except ValueError as error:
        print(f"Error: {error}")


def listar_empleados():
    empleados = EmpleadoDAO.listar()
    if not empleados:
        print("No hay empleados registrados.")
        return
    for e in empleados:
        print(f"{e.id} | {e.nombre} | {e.correo}")


def crear_departamento():
    nombre = input("Nombre del departamento: ")
    descripcion = input("Descripción: ")
    try:
        departamento = Departamento(nombre=nombre, descripcion=descripcion)
        DepartamentoDAO.insertar(departamento)
        print(f"Departamento registrado con id {departamento.id}")
    except ValueError as error:
        print(f"Error: {error}")


def seleccionar_departamento():
    departamentos = DepartamentoDAO.listar()
    if not departamentos:
        print("No hay departamentos registrados.")
        return None
    for d in departamentos:
        print(f"{d.id} | {d.nombre}")
    id_dep = solicitar_id("ID del departamento: ")
    for d in departamentos:
        if d.id == id_dep:
            return d
    print("No existe ese departamento.")
    return None


# Paso 6
def asignar_departamento():
    empleado = EmpleadoDAO.buscar_por_id(solicitar_id())
    if empleado is None:
        print("No existe ese empleado.")
        return
    departamento = seleccionar_departamento()
    if departamento is None:
        return
    departamento.agregar_empleado(empleado)
    filas = EmpleadoDAO.actualizar_departamento(empleado)
    if filas == 1:
        print("Asignación guardada.")
    else:
        print("Consulta nuevamente para comprobar el resultado.")


# Paso 8
def mostrar_departamento():
    id_dep = solicitar_id("ID del departamento: ")
    departamento = DepartamentoDAO.buscar_con_empleados(id_dep)
    if departamento is None:
        print("No existe ese departamento.")
        return
    print(departamento.nombre)
    if not departamento.empleados:
        print("Este departamento no tiene empleados.")
    for empleado in departamento.empleados:
        print(f"{empleado.id}: {empleado.nombre}")


# Paso 10: polimorfismo
def imprimir_reportes(empleados, departamento):
    reportes = [
        ReporteEmpleados(empleados),
        ReportePorDepartamento(departamento),
    ]
    for reporte in reportes:
        print(reporte.generar())
        print()


def mostrar_reportes():
    id_dep = solicitar_id("ID del departamento para el reporte: ")
    departamento = DepartamentoDAO.buscar_con_empleados(id_dep)
    if departamento is None:
        print("No existe ese departamento.")
        return
    empleados = EmpleadoDAO.listar()
    imprimir_reportes(empleados, departamento)


def menu_empleados():
    while True:
        print("\n1. Registrar empleado")
        print("2. Listar empleados")
        print("3. Crear departamento")
        print("4. Asignar departamento a empleado")
        print("5. Mostrar departamento con sus empleados")
        print("6. Reportes")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            crear_empleado()
        elif opcion == "2":
            listar_empleados()
        elif opcion == "3":
            crear_departamento()
        elif opcion == "4":
            asignar_departamento()
        elif opcion == "5":
            mostrar_departamento()
        elif opcion == "6":
            mostrar_reportes()
        elif opcion == "0":
            break
        else:
            print("Elige una opción del menú.")