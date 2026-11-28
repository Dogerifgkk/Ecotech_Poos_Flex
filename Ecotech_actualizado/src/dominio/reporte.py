# dominio/reporte.py


class ReporteEmpleados:
    def __init__(self, empleados):
        self.empleados = list(empleados)

    def generar(self):
        return self._formatear(self.empleados, "Reporte general")

    def _formatear(self, empleados, titulo):
        lineas = [titulo, "-" * len(titulo)]
        if not empleados:
            lineas.append("(sin empleados)")
        for e in empleados:
            lineas.append(f"{e.id}: {e.nombre} | {e.correo}")
        lineas.append(f"Total: {len(empleados)}")
        return "\n".join(lineas)


class ReportePorDepartamento(ReporteEmpleados):
    def __init__(self, departamento):
        super().__init__(departamento.empleados)
        self.departamento = departamento

    def generar(self):
        titulo = f"Departamento: {self.departamento.nombre}"
        return self._formatear(self.empleados, titulo)