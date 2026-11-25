# Matriz de pruebas · EcoTech

**Cómo se probó.** Las pruebas automáticas (`py -m unittest test_ecotech -v`, 29 casos) se ejecutaron
con SQLite temporal y la API simulada. Además se hizo un recorrido manual de `main.py` con entrada
por consola. La API real y MySQL **no** se probaron (ver "Pendientes").

Resultado de la última ejecución automática: **29 pruebas, todas OK**.

| # | Caso | Resultado esperado | Resultado observado |
|---|---|---|---|
| 1 | Login admin correcto | "Sesión iniciada correctamente." y abre el menú | OK |
| 2 | Clave incorrecta | "Usuario o contraseña incorrectos." y permite reintentar | OK |
| 3 | Usuario inexistente | Mismo mensaje genérico | OK |
| 4 | Tres intentos fallidos | El programa termina sin abrir el menú | OK |
| 5 | Fallo de consulta en la BD al autenticar | No entra; mensaje de que no se pudo verificar | OK (fallo simulado) |
| 6 | Rol se conserva tras reiniciar | Al volver a iniciar sesión el rol sigue igual | OK |
| 7 | Hash guardado ≠ clave | La BD guarda un hash bcrypt, nunca la clave | OK |
| 8 | Crear cuenta repetida (usuario, empleado, clave corta, empleado inexistente) | Rechazo con mensaje; no se crean duplicados | OK |
| 9 | Empleado escribe a mano una opción de admin | "Permiso denegado" sin pedir datos ni escribir en la BD | OK |
| 10 | Empleado intenta actualizar UF | PermissionError; no consulta la API ni escribe | OK |
| 11 | Mi ficha (empleado) | Muestra su propio nombre, correo y departamento | OK |
| 12 | Semilla ejecutada 2 veces | Mismos conteos de empleados, departamentos y cuentas | OK |
| 13 | Asignar empleado a departamento y repetir | Una sola aparición; relación guardada en la BD | OK |
| 14 | Departamento: ausente, vacío y con empleados | "No existe…", "No tiene empleados" y lista de nombres | OK |
| 15 | Reportes (misma llamada `generar()`) | Reporte general y reporte del departamento, con totales distintos | OK |
| 16 | Eliminar: cancelar | El registro se conserva | OK |
| 17 | Eliminar: confirmar (empleado sin cuenta) | Se elimina | OK |
| 18 | Eliminar un empleado con cuenta | Rechazado por la BD; mensaje claro; el registro se conserva | OK |
| 19 | Correo duplicado al registrar/actualizar | Rechazo con mensaje | OK |
| 20 | Admin actualiza UF (API simulada) | Valida, guarda y muestra origen "API" | OK (API simulada) |
| 21 | Consulta local posterior | El valor guardado se lee sin Internet, con su fecha | OK |
| 22 | API falla (sin red, tiempo agotado, HTTP 500, JSON inválido) | Usa el respaldo con su fecha original | OK (fallos simulados) |
| 23 | API falla y no hay respaldo | "No hay información disponible" | OK (también sin red real) |
| 24 | Mismo código y fecha guardados dos veces | Una sola fila | OK |
| 25 | Mismo código y fecha con otro valor | Sigue una fila; se actualiza el valor (política elegida) | OK |
| 26 | Migración: tabla `usuario` antigua sin `rol` | Se agrega la columna `rol` | OK |
| 27 | Actualizar UF contra la API real | Dato guardado y mostrado | **Pendiente** (no verificada) |
| 28 | Todo el recorrido con MySQL | Mismos resultados que SQLite | **Pendiente** (no probado) |
| 29 | Reiniciar el programa y consultar (en tu equipo) | La relación y la cuenta reaparecen desde la BD | **Completar al probar** |

## Problemas pendientes (con honestidad)

- **API real sin verificar.** `extraer_primero` está hecho con el formato JSON de la clase
  (`codigo` / `serie` / `fecha` / `valor`) y acepta variantes en inglés. Si la respuesta real de
  `api.boostr.cl` difiere, solo hay que ajustar esa función.
- **MySQL sin probar.** Las sentencias para MySQL están escritas (`ON DUPLICATE KEY UPDATE`,
  `FOUND_ROWS`), pero solo se ejecutaron en SQLite.
- **Correo único solo en la aplicación.** La tabla `empleado` no tiene restricción UNIQUE en `correo`;
  el servicio lo valida antes de insertar.
- **`getpass` en Git Bash** puede mostrar la contraseña; con `winpty py main.py` se oculta.
- **`Proyecto` y `Gerente`** aparecen en el diagrama UML pero no se pedían en estas clases y no se implementaron.
