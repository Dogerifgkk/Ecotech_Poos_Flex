# persistencia/crear_bd.py
from persistencia.conexion import obtener_motor, transaccion

SQL_SQLITE = {
    "departamento": '''
        CREATE TABLE IF NOT EXISTS departamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )''',
    "empleado": '''
        CREATE TABLE IF NOT EXISTS empleado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            departamento_id INTEGER REFERENCES departamento(id)
        )''',
    "usuario": '''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL UNIQUE REFERENCES empleado(id),
            nombre_usuario TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'empleado'
        )''',
    "indicador": '''
        CREATE TABLE IF NOT EXISTS indicador (
            codigo VARCHAR(10) NOT NULL,
            fecha CHAR(10) NOT NULL,
            valor REAL NOT NULL,
            PRIMARY KEY (codigo, fecha)
        )''',
}

SQL_MYSQL = {
    "departamento": '''
        CREATE TABLE IF NOT EXISTS departamento (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(255)
        )''',
    "empleado": '''
        CREATE TABLE IF NOT EXISTS empleado (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(150) NOT NULL,
            departamento_id INT NULL,
            FOREIGN KEY (departamento_id) REFERENCES departamento(id)
        )''',
    "usuario": '''
        CREATE TABLE IF NOT EXISTS usuario (
            id INT PRIMARY KEY AUTO_INCREMENT,
            empleado_id INT NOT NULL UNIQUE,
            nombre_usuario VARCHAR(40) NOT NULL UNIQUE,
            password_hash VARCHAR(100) NOT NULL,
            rol VARCHAR(10) NOT NULL DEFAULT 'empleado',
            FOREIGN KEY (empleado_id) REFERENCES empleado(id)
        )''',
    "indicador": '''
        CREATE TABLE IF NOT EXISTS indicador (
            codigo VARCHAR(10) NOT NULL,
            fecha CHAR(10) NOT NULL,
            valor DOUBLE NOT NULL,
            PRIMARY KEY (codigo, fecha)
        )''',
}

ORDEN = ["departamento", "empleado", "usuario", "indicador"]   # respeta las FK


def _usuario_tiene_rol(cursor):
    if obtener_motor() == "sqlite":
        cursor.execute("PRAGMA table_info(usuario)")
        return any(fila[1] == "rol" for fila in cursor.fetchall())
    cursor.execute("SHOW COLUMNS FROM usuario LIKE 'rol'")
    return cursor.fetchone() is not None


def migrar_usuario_rol(cursor):
    """Migración: si la tabla usuario es antigua (sin rol), agrega la columna."""
    if not _usuario_tiene_rol(cursor):
        if obtener_motor() == "sqlite":
            cursor.execute(
                "ALTER TABLE usuario ADD COLUMN rol TEXT NOT NULL DEFAULT 'empleado'")
        else:
            cursor.execute(
                "ALTER TABLE usuario ADD COLUMN rol VARCHAR(10) NOT NULL DEFAULT 'empleado'")


def crear_tablas():
    sql = SQL_SQLITE if obtener_motor() == "sqlite" else SQL_MYSQL
    with transaccion() as cursor:
        for tabla in ORDEN:
            cursor.execute(sql[tabla])
        migrar_usuario_rol(cursor)


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos preparada correctamente.")
