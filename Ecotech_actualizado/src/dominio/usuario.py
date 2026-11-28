# src/dominio/usuario.py
ROLES = ("admin", "empleado")


class Usuario:
    """Cuenta de acceso. NO hereda de Empleado: se asocia a él por empleado_id."""
    MIN_USUARIO = 3
    MAX_USUARIO = 40
    MIN_CLAVE = 6

    def __init__(self, nombre_usuario, password_hash, empleado_id, id=None,
                 rol="empleado"):
        if type(empleado_id) is not int or empleado_id <= 0:
            raise ValueError("El ID del empleado debe ser positivo.")
        if rol not in ROLES:
            raise ValueError("Rol de usuario no válido.")
        self.id = id
        self.empleado_id = empleado_id
        self.nombre_usuario = self.normalizar_usuario(nombre_usuario)
        self.password_hash = password_hash   # resultado del hash, nunca la clave
        self.rol = rol

    @classmethod
    def normalizar_usuario(cls, nombre):
        if not isinstance(nombre, str):
            raise TypeError("El usuario debe ser texto.")
        nombre = nombre.strip().lower()
        if not cls.MIN_USUARIO <= len(nombre) <= cls.MAX_USUARIO:
            raise ValueError("Usuario fuera del largo permitido.")
        if not all(c.isascii() and (c.isalnum() or c in "_.") for c in nombre):
            raise ValueError("Use letras ASCII, números, punto o guion bajo.")
        return nombre

    @classmethod
    def validar_clave(cls, clave):
        if not isinstance(clave, str):
            raise TypeError("La contraseña debe ser texto.")
        if len(clave) < cls.MIN_CLAVE:
            raise ValueError(f"Use al menos {cls.MIN_CLAVE} caracteres.")
        return clave   # Sin strip, lower ni truncado.

    def __repr__(self):
        # Nunca mostramos el hash en pantalla ni en logs.
        return (f"Usuario(id={self.id}, nombre_usuario={self.nombre_usuario!r}, "
                f"empleado_id={self.empleado_id}, rol={self.rol!r})")
