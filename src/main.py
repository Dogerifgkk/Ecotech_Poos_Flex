from empleado import Empleado
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.crear_bd import crear_tablas

crear_tablas()

emp = Empleado(nombre="juanito", correo="correo@gmail.cl")
print(emp.obtener_datos())
EmpleadoDAO.insertar(emp)
print(emp.obtener_datos())   # ahora debe mostrar el id asignado