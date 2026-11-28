# main.py: la aplicación solo se abre con una cuenta válida
import logging

from persistencia.conexion import ErrorBD
from persistencia.crear_bd import crear_tablas
from persistencia.semilla import sembrar
from presentacion.menu_empleados import menu_empleados
from presentacion.menu_usuario import solicitar_login
from servicios.empleados import consultar_mi_ficha

MAX_INTENTOS = 3


def preparar_bd():
    try:
        crear_tablas()     # esquema
        sembrar()          # semilla: solo inserta lo que falta
    except ErrorBD:
        logging.getLogger("ecotech").exception("No se pudo preparar la BD.")
        print("No se pudo preparar la base de datos. Revisa tu archivo .env.")
        return False
    return True


def main():
    logging.basicConfig(
        filename="ecotech.log", level=logging.ERROR, encoding="utf-8",
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if not preparar_bd():
        return

    usuario_actual = None
    for _ in range(MAX_INTENTOS):
        usuario_actual = solicitar_login()
        if usuario_actual is not None:
            break
    if usuario_actual is None:
        print("No se pudo iniciar sesión. Saliendo.")
        return

    # Mini desafío: mostrar a qué empleado pertenece la cuenta (sin mostrar el hash).
    try:
        ficha = consultar_mi_ficha(usuario_actual)
    except ErrorBD:
        print("No se pudo recuperar el empleado de la cuenta. No se puede continuar.")
        return
    if ficha is None:
        print("La cuenta no tiene un empleado vinculado. No se puede continuar.")
        return
    print(f"Sesión: {usuario_actual.nombre_usuario} → {ficha.nombre} <{ficha.correo}>")

    menu_empleados(usuario_actual)
    usuario_actual = None
    print("Sesión cerrada.")


if __name__ == "__main__":
    main()
