# departamento.py
from empleado import Empleado


class Departamento:
    MIN_NOMBRE = 2
    MAX_NOMBRE = 80

    def __init__(self, nombre, descripcion="", id=None):
        self.id = id
        self.nombre = nombre            # pasa por el setter (valida)
        self.descripcion = descripcion
        self._empleados = []            # lista interna (privada)
        self.gerente = None

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise ValueError("El nombre del departamento debe ser texto.")
        valor = " ".join(valor.split())
        if not (self.MIN_NOMBRE <= len(valor) <= self.MAX_NOMBRE):
            raise ValueError(
                f"El nombre del departamento debe tener entre {self.MIN_NOMBRE} "
                f"y {self.MAX_NOMBRE} caracteres."
            )
        self._nombre = valor

    @property
    def empleados(self):
        return list(self._empleados)    # copia: no se modifica desde afuera

    def agregar_empleado(self, empleado: Empleado):
        anterior = empleado.departamento
        if anterior is not None and anterior is not self:
            anterior.quitar_empleado(empleado)   # un empleado, un solo departamento
        if empleado not in self._empleados:      # evita duplicados
            self._empleados.append(empleado)
        empleado.departamento = self

    def quitar_empleado(self, empleado: Empleado):
        if empleado in self._empleados:
            self._empleados.remove(empleado)
            empleado.departamento = None

    def obtener_datos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "total_empleados": len(self._empleados),
        }
