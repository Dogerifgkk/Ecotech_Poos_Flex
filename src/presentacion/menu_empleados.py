# presentacion/menu_empleados.py
from dominio.reporte import ReporteEmpleados, ReportePorDepartamento
from empleado import Empleado
from persistencia.conexion import ErrorIntegridad
from presentacion.comun import confirmar, ejecutar_seguro, leer_validado, solicitar_id
from presentacion.menu_indicadores import menu_indicadores
from presentacion.menu_usuario import crear_cuenta
from servicios import empleados as servicio
from servicios.permisos import exigir_admin


# ---------- entradas con reintento solo del campo incorrecto ----------
def solicitar_nombre():
    return leer_validado("Nombre", Empleado.validar_nombre)


def solicitar_correo():
    return leer_validado("Correo", Empleado.validar_correo)


def mostrar_empleado(empleado):
    departamento = empleado.departamento.nombre if empleado.departamento else "(sin departamento)"
    print(f"{empleado.id} | {empleado.nombre} | {empleado.correo} | {departamento}")


# ---------- CRUD de empleados (solo admin: el servicio lo exige) ----------
def crear_empleado(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    nombre = solicitar_nombre()
    if nombre is None:
        print("Registro cancelado.")
        return
    while True:
        correo = solicitar_correo()
        if correo is None:
            print("Registro cancelado.")
            return
        try:
            empleado = servicio.registrar_empleado(usuario, nombre, correo)
        except ValueError as error:          # por ejemplo, correo repetido
            print(f"{error} Prueba con otro correo.")
        else:
            print(f"Empleado registrado. ID: {empleado.id}")
            return


def listar_empleados(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    empleados = servicio.listar_empleados(usuario)
    if not empleados:
        print("No hay empleados registrados.")
        return
    for e in empleados:
        mostrar_empleado(e)


def buscar_empleado(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    empleado = servicio.buscar_empleado(usuario, solicitar_id())
    if empleado is None:
        print("No existe un empleado con ese ID.")
    else:
        mostrar_empleado(empleado)


def actualizar_empleado(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    empleado = servicio.buscar_empleado(usuario, solicitar_id())
    if empleado is None:
        print("No existe un empleado con ese ID.")
        return
    mostrar_empleado(empleado)
    nuevo_correo = solicitar_correo()
    if nuevo_correo is None:
        print("Actualización cancelada.")
        return
    if nuevo_correo == empleado.correo:
        print("El correo es el mismo; no hay cambios.")
        return
    try:
        filas = servicio.actualizar_correo(usuario, empleado, nuevo_correo)
    except ValueError as error:
        print(f"No se actualizó: {error}")
        return
    if filas == 1:
        print("Correo actualizado correctamente.")
    else:
        print("Vuelve a consultar el estado del empleado.")


def eliminar_empleado(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    empleado = servicio.buscar_empleado(usuario, solicitar_id())
    if empleado is None:
        print("No existe un empleado con ese ID.")
        return
    mostrar_empleado(empleado)
    if not confirmar(f"¿Eliminar a {empleado.nombre}?"):
        print("Eliminación cancelada. El registro se conserva.")
        return
    try:
        filas = servicio.eliminar_empleado(usuario, empleado.id)
    except ErrorIntegridad:
        # Una IntegrityError al borrar NO significa "correo duplicado":
        # aquí significa que otra tabla (por ejemplo usuario) referencia al empleado.
        print("No se puede eliminar: el empleado tiene registros relacionados "
              "(por ejemplo, una cuenta de usuario).")
        return
    if filas == 1:
        print("Empleado eliminado.")
    else:
        print("Vuelve a consultar el estado del empleado.")


# ---------- departamentos ----------
def crear_departamento(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    nombre = input("Nombre del departamento: ")
    descripcion = input("Descripción (opcional): ")
    try:
        departamento = servicio.crear_departamento(usuario, nombre, descripcion)
    except ValueError as error:
        print(f"No se creó el departamento: {error}")
    else:
        print(f"Departamento registrado con id {departamento.id}")


def seleccionar_departamento(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    departamentos = servicio.listar_departamentos(usuario)
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


def asignar_departamento(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    empleado = servicio.buscar_empleado(usuario, solicitar_id())
    if empleado is None:
        print("No existe ese empleado.")
        return
    departamento = seleccionar_departamento(usuario)
    if departamento is None:
        return
    filas = servicio.asignar_departamento(usuario, empleado, departamento)
    if filas == 1:
        print("Asignación guardada.")
    else:
        print("Consulta nuevamente para comprobar el resultado.")


def mostrar_departamento(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    id_dep = solicitar_id("ID del departamento: ")
    departamento = servicio.consultar_departamento(usuario, id_dep)
    if departamento is None:
        print("No existe ese departamento.")
        return
    print(departamento.nombre)
    if not departamento.empleados:
        print("Este departamento no tiene empleados.")
    for empleado in departamento.empleados:
        print(f"{empleado.id}: {empleado.nombre}")


# ---------- reportes: polimorfismo ----------
def imprimir_reportes(empleados, departamento):
    reportes = [
        ReporteEmpleados(empleados),
        ReportePorDepartamento(departamento),
    ]
    for reporte in reportes:
        print(reporte.generar())     # misma llamada, cada objeto responde a su manera
        print()


def mostrar_reportes(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    id_dep = solicitar_id("ID del departamento para el reporte: ")
    empleados, departamento = servicio.datos_para_reportes(usuario, id_dep)
    if departamento is None:
        print("No existe ese departamento.")
        return
    imprimir_reportes(empleados, departamento)


# ---------- opciones para cualquier sesión ----------
def mi_ficha(usuario):
    empleado = servicio.consultar_mi_ficha(usuario)
    if empleado is None:
        print("No se encontró tu ficha de empleado.")
    else:
        mostrar_empleado(empleado)


def abrir_indicadores(usuario):
    menu_indicadores(usuario)


# ---------- menú principal según el tipo de usuario ----------
OPCIONES = {
    "1": ("Registrar empleado", crear_empleado),
    "2": ("Listar empleados", listar_empleados),
    "3": ("Buscar empleado por ID", buscar_empleado),
    "4": ("Actualizar correo de un empleado", actualizar_empleado),
    "5": ("Eliminar empleado", eliminar_empleado),
    "6": ("Asignar departamento a un empleado", asignar_departamento),
    "7": ("Mostrar reportes", mostrar_reportes),
    "8": ("Consultar departamento con sus empleados", mostrar_departamento),
    "9": ("Crear departamento", crear_departamento),
    "10": ("Crear cuenta de usuario", crear_cuenta),
    "11": ("Indicadores (UF / dólar)", abrir_indicadores),
    "12": ("Mi ficha", mi_ficha),
}
OPCIONES_EMPLEADO = ("11", "12")


def opciones_visibles(usuario):
    if getattr(usuario, "rol", None) == "admin":
        return list(OPCIONES)
    return list(OPCIONES_EMPLEADO)


def menu_empleados(usuario):
    while True:
        print(f"\n=== EcoTech · {usuario.nombre_usuario} ({usuario.rol}) ===")
        for numero in opciones_visibles(usuario):
            print(f"{numero}. {OPCIONES[numero][0]}")
        print("0. Cerrar sesión")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            break
        if opcion in OPCIONES:
            # Ocultar una opción no basta: si un empleado escribe "5", el SERVICIO
            # la rechaza con PermissionError antes de tocar la BD.
            ejecutar_seguro(OPCIONES[opcion][1], usuario)
        else:
            print("Elige una opción del menú.")
