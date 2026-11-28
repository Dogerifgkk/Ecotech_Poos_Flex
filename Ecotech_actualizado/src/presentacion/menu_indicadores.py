# presentacion/menu_indicadores.py
from presentacion.comun import ejecutar_seguro
from servicios.indicadores import actualizar_indicador, consultar_guardado
from servicios.permisos import exigir_admin

CODIGOS = {"1": "uf", "2": "dolar"}


def elegir_codigo():
    opcion = input("Indicador: 1) UF  2) Dólar  (Enter para cancelar): ").strip()
    if not opcion:
        return None
    if opcion not in CODIGOS:
        print("Elige 1 o 2.")
        return None
    return CODIGOS[opcion]


def mostrar_indicador(indicador, origen):
    if indicador is None:
        print("No hay información disponible: la API no respondió y no hay respaldo guardado.")
        return
    if origen == "api":
        texto_origen = "API (guardado ahora en la BD)"
    else:
        texto_origen = "respaldo local (la API no respondió)"
    # Se muestra SIEMPRE la fecha del dato: no se afirma que sea "el valor de hoy".
    print(f"{indicador.codigo.upper()} | fecha del dato: {indicador.fecha} | "
          f"valor: {indicador.valor:,.2f} | origen: {texto_origen}")


def consultar_guardado_menu(usuario):
    codigo = elegir_codigo()
    if codigo is None:
        return
    indicador = consultar_guardado(usuario, codigo)
    if indicador is None:
        print("Aún no hay un valor guardado. Un administrador debe actualizar primero.")
    else:
        mostrar_indicador(indicador, "respaldo")


def actualizar_menu(usuario):
    exigir_admin(usuario)   # primera instrucción de una acción administrativa
    codigo = elegir_codigo()
    if codigo is None:
        return
    indicador, origen = actualizar_indicador(usuario, codigo)
    mostrar_indicador(indicador, origen)


def menu_indicadores(usuario):
    while True:
        print("\n--- Indicadores ---")
        print("1. Consultar valor guardado")
        if getattr(usuario, "rol", None) == "admin":
            print("2. Actualizar desde Internet")
        print("0. Volver")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            ejecutar_seguro(consultar_guardado_menu, usuario)
        elif opcion == "2":
            # Aunque la opción no se muestre, si alguien la escribe el servicio la rechaza.
            ejecutar_seguro(actualizar_menu, usuario)
        elif opcion == "0":
            break
        else:
            print("Elige una opción del menú.")
