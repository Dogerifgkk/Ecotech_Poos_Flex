#Class Empleado

from datetime import date


class Empleado:

    MIN_NOMBRE = 2
    MAX_NOMBRE = 80
    MIN_CORREO = 5
    MAX_CORREO = 150

    def __init__(self, nombre, correo, id=None, direccion="",
                 telefono="", fecha_inicio_contrato=None, salario=0.0):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.direccion = direccion
        self.telefono = telefono
        self.fecha_inicio_contrato = fecha_inicio_contrato or date.today()
        self.salario = salario

        @property
        def nombre(self):
            return self._nombre
        
        @nombre.setter
        def nombre(self, valor):
            valor = " ".join(valor.split()).title()     #normaliza
            if not (self.MIN.NOMBRE <= len(valor) <= self.MAX_NOMBRE):
                raise ValueError(
                    f"El nombre"
                )