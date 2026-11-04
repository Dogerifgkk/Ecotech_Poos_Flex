from dominio.empleado import Empleado

emp = Empleado("juanito", "correo@gmail.cl")

emp2 = Empleado(
    correo="julio@gmail.cl",
    nombre="julio",
)

print(emp.mostrar_datos())
print(emp2.mostrar_datos())

