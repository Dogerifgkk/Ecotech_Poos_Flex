# persistencia/conexion.py
import os
import sqlite3
from contextlib import contextmanager

# pymysql y dotenv son opcionales: si usas SQLite no hace falta tenerlos instalados.
try:
    import pymysql
    from pymysql.constants import CLIENT
except ImportError:          # pragma: no cover
    pymysql = None
    CLIENT = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:          # pragma: no cover
    pass


class ErrorBD(Exception):
    """Falló una operación en la base de datos (conexión, SQL, commit...)."""


class ErrorIntegridad(ErrorBD):
    """Se incumplió una restricción: UNIQUE, clave foránea, NOT NULL..."""


_TIPOS_INTEGRIDAD = (sqlite3.IntegrityError,) + (
    (pymysql.err.IntegrityError,) if pymysql else ()
)
_TIPOS_BD = (sqlite3.Error,) + ((pymysql.err.Error,) if pymysql else ())


def obtener_motor():
    return os.getenv("DB_ENGINE", "sqlite").lower()


def marcador():
    """Marcador de parámetros SQL según el motor: ? en SQLite, %s en MySQL."""
    return "?" if obtener_motor() == "sqlite" else "%s"


def abrir_conexion():
    motor = obtener_motor()

    if motor == "sqlite":
        conexion = sqlite3.connect(os.getenv("DB_NAME", "ecotech.db"))
        conexion.execute("PRAGMA foreign_keys = ON")   # SQLite no las exige por defecto
        return conexion

    if motor == "mysql":
        if pymysql is None:
            raise ErrorBD("Falta instalar PyMySQL (pip install -r requirements.txt).")
        return pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            charset="utf8mb4",
            client_flag=CLIENT.FOUND_ROWS,   # rowcount = filas encontradas, no solo cambiadas
        )
    raise ValueError(f"Motor no soportado: {motor}")


def _revertir(conexion):
    try:
        if conexion is not None:
            conexion.rollback()
    except Exception:
        pass


@contextmanager
def transaccion():
    """Abre conexión y cursor, hace commit al terminar bien y rollback si falla.

    Convierte los errores de la librería de BD en ErrorBD / ErrorIntegridad,
    para que las capas de arriba no dependan de SQLite ni de MySQL.
    Uso:
        with transaccion() as cursor:
            cursor.execute(...)
    """
    conexion = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        yield cursor
        conexion.commit()
    except _TIPOS_INTEGRIDAD as error:
        _revertir(conexion)
        raise ErrorIntegridad(str(error)) from error
    except _TIPOS_BD as error:
        _revertir(conexion)
        raise ErrorBD(str(error)) from error
    except Exception:
        _revertir(conexion)
        raise
    finally:
        if conexion is not None:
            conexion.close()
