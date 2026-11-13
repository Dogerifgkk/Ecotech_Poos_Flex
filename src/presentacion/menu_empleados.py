# presentacion/menu.py
from empleado import Empleado
from persistencia.empleado_dao import EmpleadoDAO

import logging
from sqlite3 import IntegrityError, OperationalError

logger = logging.getLogger(__name__)


def guardar_empleado(empleado):
    try:
        EmpleadoDAO.insertar(empleado)
    except IntegrityError:
        logger.exception("Restricción de BD al registrar.")
        print("Revisa las restricciones de los datos.")
    except OperationalError:
        logger.exception("Fallo al registrar en la BD.")
        print("No se pudo completar la operación.")
    else:
        print(f"Empleado registrado. ID: {empleado.id}")


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


def menu_empleados():
    while True:
        print("\n1. Registrar\n2. Listar\n0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            crear_empleado()
        elif opcion == "2":
            listar_empleados()
        elif opcion == "0":
            break
        else:
            print("Elige 0, 1 o 2.")


def solicitar_nombre():
    while True:
        valor = input("Nombre: ")
        try:
            return Empleado.validar_nombre(valor)
        except ValueError as error:
            print(f"Nombre inválido: {error}")


def solicitar_correo():
    while True:
        valor = input("Nombre: ")
        try:
            return Empleado.validar_nombre(valor)
        except ValueError as error:
            print(f"Nombre inválido: {error}")


def solicitar_datos(txt, value=""):
    if value:
        entrada = input(f"{txt} [{value}]: ").strip()
        return entrada or value
    return input(f"{txt}: ").strip()


def solicitar_id():
    while True:
        texto = input("ID del empleado: ").strip()
        try:
            id_empleado = int(texto)
            if id_empleado <= 0:
                raise ValueError("El ID debe ser positivo.")
        except ValueError:
            print("Ingresa un entero mayor que 0.")
        else:
            return id_empleado


