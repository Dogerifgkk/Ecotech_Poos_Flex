# Class Empleado
from datetime import date


class Empleado:
    MIN_NOMBRE = 2
    MAX_NOMBRE = 80
    MIN_CORREO = 5
    MAX_CORREO = 150

    def __init__(self, nombre, correo, id=None, direccion="",
                 telefono="", fecha_inicio_contrato=None, salario=0.0):
        self.id = id
        self.nombre = nombre      # pasa por el setter (valida)
        self.correo = correo      # pasa por el setter (valida)
        self.direccion = direccion
        self.telefono = telefono
        self.fecha_inicio_contrato = fecha_inicio_contrato or date.today()
        self.salario = salario    # pasa por el setter (valida)
        self.departamento = None  # pasa por el setter (valida)

    # ---------- validadores reutilizables (también los usa la consola) ----------
    @staticmethod
    def validar_nombre(nombre):
        if not isinstance(nombre, str):
            raise ValueError("El nombre debe ser texto.")
        nombre = " ".join(nombre.split()).title()   # normaliza espacios y mayúsculas
        if not (Empleado.MIN_NOMBRE <= len(nombre) <= Empleado.MAX_NOMBRE):
            raise ValueError(
                f"El nombre debe tener entre {Empleado.MIN_NOMBRE} "
                f"y {Empleado.MAX_NOMBRE} caracteres."
            )
        return nombre

    @staticmethod
    def validar_correo(correo):
        if not isinstance(correo, str):
            raise ValueError("El correo debe ser texto.")
        correo = correo.strip().lower()
        if not (Empleado.MIN_CORREO <= len(correo) <= Empleado.MAX_CORREO):
            raise ValueError(
                f"El correo debe tener entre {Empleado.MIN_CORREO} "
                f"y {Empleado.MAX_CORREO} caracteres."
            )
        partes = correo.split("@")
        if (len(partes) != 2 or not partes[0] or "." not in partes[1]
                or partes[1].startswith(".") or partes[1].endswith(".")
                or " " in correo):
            raise ValueError("El correo requiere usuario y dominio (ej: ana@ecotech.cl).")
        return correo

    # ---------- propiedades ----------
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = self.validar_nombre(valor)

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        self._correo = self.validar_correo(valor)

    @property
    def salario(self):
        return self._salario

    @salario.setter
    def salario(self, valor):
        valor = float(valor)
        if valor < 0:
            raise ValueError("El salario no puede ser negativo")
        self._salario = valor

    # Paso 5 · validar la referencia con una propiedad
    @property
    def departamento(self):
        return self._departamento

    @departamento.setter
    def departamento(self, valor):
        from departamento import Departamento   # import local: evita import circular
        if valor is not None and not isinstance(valor, Departamento):
            raise ValueError("Asigna un Departamento o None.")
        self._departamento = valor

    def obtener_datos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "fecha_inicio_contrato": self.fecha_inicio_contrato.isoformat(),
            "salario": self.salario,
        }
