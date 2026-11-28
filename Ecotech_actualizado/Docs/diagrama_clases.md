# Diagrama de clases · EcoTech (coincide con el código entregado)

Este diagrama refleja lo **realmente implementado**. `Proyecto` y `Gerente` del diseño inicial
no se implementaron (no se pedían en las clases 1–7); `Departamento.gerente` queda como atributo
reservado (`None`).

```mermaid
classDiagram
    class Empleado {
        +int id
        -str _nombre
        -str _correo
        +str direccion
        +str telefono
        +date fecha_inicio_contrato
        -float _salario
        -Departamento _departamento
        +validar_nombre(nombre)$
        +validar_correo(correo)$
        +obtener_datos() dict
    }
    class Departamento {
        +int id
        -str _nombre
        +str descripcion
        -list _empleados
        +gerente
        +agregar_empleado(empleado)
        +empleados list
    }
    class Usuario {
        +int id
        +int empleado_id
        +str nombre_usuario
        +str password_hash
        +str rol
        +normalizar_usuario(nombre)$
        +validar_clave(clave)$
    }
    class Indicador {
        +str codigo
        +str fecha
        +float valor
        +validar_codigo(c)$
        +validar_fecha(f)$
        +validar_valor(v)$
    }
    class ReporteEmpleados {
        +list empleados
        +generar() str
    }
    class ReportePorDepartamento {
        +Departamento departamento
        +generar() str
    }
    class EmpleadoDAO
    class DepartamentoDAO
    class UsuarioDAO
    class IndicadorDAO

    Departamento "0..1" o-- "0..*" Empleado : agrupa
    Usuario "0..1" --> "1" Empleado : empleado_id
    ReporteEmpleados <|-- ReportePorDepartamento
    ReporteEmpleados ..> Empleado : lista
    ReportePorDepartamento --> Departamento
    EmpleadoDAO ..> Empleado : reconstruye
    DepartamentoDAO ..> Departamento : reconstruye
    UsuarioDAO ..> Usuario : reconstruye
    IndicadorDAO ..> Indicador : reconstruye
```

## Cómo se tradujo el modelo a Python

| Relación del modelo | Cómo se implementó |
|---|---|
| Departamento agrupa Empleados (1 a muchos) | `Departamento._empleados` (lista privada) y `Empleado.departamento` (propiedad validada); en la BD, `empleado.departamento_id` (clave foránea). |
| Usuario pertenece a un Empleado (1 a 1) | `Usuario.empleado_id`; en la BD, `usuario.empleado_id UNIQUE` con clave foránea. `Usuario` no hereda de `Empleado`. |
| ReportePorDepartamento es un ReporteEmpleados | Herencia: `class ReportePorDepartamento(ReporteEmpleados)`; ambos responden a `generar()` (polimorfismo). |
| Indicador (UF/dólar) | Objeto de dominio con clave compuesta `(codigo, fecha)` en la tabla `indicador`. |
