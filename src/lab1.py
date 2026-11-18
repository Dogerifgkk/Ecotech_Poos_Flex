from empleado import Empleado
from departamento import Departamento

dep = Departamento(nombre="ventas", descripcion="Área comercial")
ana = Empleado(nombre="ana lopez", correo="ana@mail.cl")
luis = Empleado(nombre="luis perez", correo="luis@mail.cl")

dep.agregar_empleado(ana)
dep.agregar_empleado(luis)
dep.agregar_empleado(ana)    # asignación repetida

print([e.nombre for e in dep.empleados])


print(ana.departamento.nombre)