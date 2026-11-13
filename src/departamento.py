# departamento.py
from empleado import Empleado


class Departamento:
    MIN_NOMBRE = 2
    MAX_NOMBRE = 80

    def __init__(self, nombre, descripcion="", id=None):
        self.id = id
        self.nombre = nombre            # pasa por el setter (valida)
        self.descripcion = descripcion
        self.empleados = []             # agregación: 0..* empleados
        self.gerente = None             # relación "dirige": 0..1 gerente

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

    def agregar_empleado(self, empleado: Empleado):
        if empleado not in self.empleados:
            self.empleados.append(empleado)

    def quitar_empleado(self, empleado: Empleado):
        if empleado in self.empleados:
            self.empleados.remove(empleado)

    def obtener_datos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "total_empleados": len(self.empleados),
        }