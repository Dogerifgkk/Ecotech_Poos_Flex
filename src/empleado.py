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

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        valor = " ".join(valor.split()).title()   # normaliza
        if not (self.MIN_NOMBRE <= len(valor) <= self.MAX_NOMBRE):
            raise ValueError(
                f"El nombre debe tener entre {self.MIN_NOMBRE} "
                f"y {self.MAX_NOMBRE} caracteres"
            )
        self._nombre = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        valor = valor.strip().lower()
        if not (self.MIN_CORREO <= len(valor) <= self.MAX_CORREO) or "@" not in valor:
            raise ValueError("Correo inválido")
        self._correo = valor

    @property
    def salario(self):
        return self._salario

    @salario.setter
    def salario(self, valor):
        valor = float(valor)
        if valor < 0:
            raise ValueError("El salario no puede ser negativo")
        self._salario = valor

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