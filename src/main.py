from src.empleado import Empleado
from persistencia.empleado_dao import EmpleadoDAO
from dominio.departamento import Departamento
from persistencia_crear_hd import crear_tablas
crear_tablas()

emp = Empleado("correo@gmail.cl","juanito")
print(emp.mostrar_datos())
EmpleadoDAO.insertar(emp)
print(emp.mostrar_datos())


