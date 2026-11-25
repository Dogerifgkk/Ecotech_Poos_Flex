# EcoTech · Programación Orientada a Objetos (U2–U3)

Aplicación de consola en Python para gestionar empleados y departamentos de EcoTech,
con cuentas de usuario (login con hash), permisos por tipo de usuario y un indicador
económico (UF / dólar) consultado a una API externa con respaldo local.

## Arquitectura

```
src/
├── main.py                  # arranque: prepara la BD, pide login y abre el menú
├── empleado.py              # Empleado (validaciones, propiedad departamento)
├── departamento.py          # Departamento (colección de empleados)
├── lab1.py                  # laboratorio 1: relación en memoria
├── dominio/                 # reglas del negocio, sin SQL ni consola
│   ├── reporte.py           # ReporteEmpleados / ReportePorDepartamento (herencia, polimorfismo)
│   ├── usuario.py           # Usuario (cuenta, rol, validaciones)
│   └── indicador.py         # Indicador (código, fecha, valor)
├── persistencia/            # SQL parametrizado; reconstruye objetos
│   ├── conexion.py          # SQLite/MySQL, transaccion(), ErrorBD
│   ├── crear_bd.py          # tablas + migración de la columna rol
│   ├── empleado_dao.py, departamento_dao.py, usuario_dao.py, indicador_dao.py
│   └── semilla.py           # datos ficticios repetibles
├── servicios/               # permisos y coordinación
│   ├── permisos.py          # exigir_sesion / exigir_admin
│   ├── autenticacion.py     # crear_hash, registrar_usuario, autenticar
│   ├── empleados.py         # acciones de empleados/departamentos con permiso
│   ├── api_indicadores.py   # HTTP + JSON -> Indicador
│   └── indicadores.py       # actualizar (API o respaldo) y consultar
├── presentacion/            # entradas y mensajes de consola
│   ├── comun.py, menu_empleados.py, menu_usuario.py, menu_indicadores.py
└── test_ecotech.py          # pruebas automáticas
```

Trayecto de una acción: **menú → servicio (permiso y reglas) → DAO (SQL) → BD**.
El DAO es quien reconstruye los objetos al leer; el menú solo pide datos y muestra resultados.

## Requisitos

- Python 3.10 o superior
- Paquetes de `requirements.txt` (PyMySQL, python-dotenv, bcrypt, requests)

## Instalación

Desde la carpeta del proyecto, en Git Bash:

```bash
py -m venv .venv
source .venv/Scripts/activate        # en Windows con Git Bash
pip install -r requirements.txt
```

## Configuración

1. Copia `.env.example` como `.env` (el archivo `.env` NO se sube a GitHub).
2. Por defecto usa **SQLite** (archivo `ecotech.db`), sin configurar nada más.
3. Para MySQL, edita `.env`: `DB_ENGINE=mysql`, `DB_HOST`, `DB_PORT`, `DB_USER`,
   `DB_PASSWORD` y `DB_NAME` (la base de datos debe existir).

## Crear la base de datos y las semillas

No hay que hacerlo a mano: `main.py` ejecuta `crear_tablas()` y `sembrar()` al iniciar.
Para hacerlo por separado (desde `src`):

```bash
py persistencia/crear_bd.py          # solo tablas
```

La semilla inserta únicamente lo que falta, así que se puede ejecutar muchas veces sin duplicar datos.
Para partir desde cero, borra `src/ecotech.db`.

## Ejecución

```bash
cd src
py main.py
```

Si la contraseña se ve mientras la escribes en Git Bash, ejecuta `winpty py main.py`.

## Cuentas de prueba (datos ficticios)

| Usuario | Contraseña | Tipo | Empleado vinculado |
|---|---|---|---|
| `admin` | `Admin2026!` | administrador | Administrador Ecotech |
| `ana_lopez` | `Ana2026!` | empleado | Ana Lopez (Soporte) |
| `luis_perez` | `Luis2026!` | empleado | Luis Perez (Soporte) |

Departamentos de la semilla: Soporte (Ana, Luis), Ventas (Marta), Recursos Humanos (Administrador),
Finanzas (vacío). Pedro Soto no tiene departamento ni cuenta (sirve para probar asignación y eliminación).

## Permisos

| Acción | Administrador | Empleado | Sin sesión |
|---|---|---|---|
| Registrar, listar, buscar, actualizar y eliminar empleados | Sí | No | No |
| Crear departamentos, asignar empleados, consultar departamento | Sí | No | No |
| Reportes | Sí | No | No |
| Crear cuentas de usuario (siempre rol `empleado`) | Sí | No | No |
| Actualizar UF/dólar desde Internet | Sí | No | No |
| Consultar el valor guardado de UF/dólar | Sí | Sí | No |
| Ver su propia ficha | Sí | Sí | No |
| Iniciar sesión / salir | Sí | Sí | Sí |

El menú oculta las opciones no permitidas, pero además **cada acción comprueba el permiso**
(`exigir_admin`): si un empleado escribe a mano una opción de administrador, es rechazada
antes de pedir datos o tocar la BD.

## Pruebas

Automáticas (BD temporal en SQLite y API simulada; no tocan tu `ecotech.db`):

```bash
cd src
py -m unittest test_ecotech -v
```

Matriz de pruebas con resultados esperados y observados, y problemas pendientes:
[`Docs/matriz_pruebas.md`](Docs/matriz_pruebas.md).

## Git

```bash
git clone URL
git status
git add .
git commit -m "mensaje"
git push
```
