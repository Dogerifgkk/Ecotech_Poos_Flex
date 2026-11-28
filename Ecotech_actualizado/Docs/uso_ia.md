# Uso de herramientas de IA y validación crítica (criterios 2.1.5 y 3.1.4)

> **Completar antes de entregar.** Esta bitácora debe describir lo que ustedes realmente hicieron.
> Las filas marcadas con "COMPLETAR" son un recordatorio: reemplácenlas por casos reales
> (herramienta usada, qué pidieron, qué detectaron y qué decidieron). Cada integrante debe poder
> explicarlas en la defensa.

## 1. Regla del equipo
El código generado por IA no se pega sin revisarlo: se lee, se ejecuta, se prueba
(`py -m unittest test_ecotech -v`) y se decide **adoptar, modificar o descartar** con un criterio
técnico (seguridad, eficiencia, coherencia con el modelo).

## 2. Bitácora

| # | Herramienta | Qué se pidió (prompt) | Qué entregó la IA | Problemas / riesgos detectados | Decisión (adoptar / modificar / descartar) y criterio |
|---|---|---|---|---|---|
| 1 | Claude | "Revisa mi repositorio y créame una carpeta con la actualización de todo lo que falte por implementar del material de estas carpetas (clases U2 y U3, guía de evaluación)." | Revisión del repo contra la guía; carpeta `Ecotech_actualizado` con: `.gitignore` (excluye `*.db` y `*.log`), parser de la API más tolerante a distintos formatos JSON, una prueba nueva, diagrama de clases alineado al código y esta bitácora. | La IA **no pudo consultar la API real** (sin acceso a la red) ni ejecutar bcrypt real; el formato real de `api.boostr.cl` quedó por verificar. | **Modificar/validar:** se adoptó el parser tolerante, pero se verifica con la respuesta real en nuestro equipo y se ajusta si hace falta. Se ejecutaron las 30 pruebas. COMPLETAR: resultado de la prueba con la API real. |
| 2 | COMPLETAR | COMPLETAR: p. ej. "genera una función de login" | COMPLETAR | COMPLETAR: p. ej. contraseña en texto plano, mensaje que revela si el usuario existe, SQL con f-string | COMPLETAR: qué se cambió y por qué |
| 3 | COMPLETAR | COMPLETAR: p. ej. consumo de la API con `requests` | COMPLETAR | COMPLETAR: p. ej. sin `timeout`, sin `raise_for_status`, mensaje de error con detalles internos | COMPLETAR |
| 4 | COMPLETAR | COMPLETAR | COMPLETAR | COMPLETAR | COMPLETAR |

## 3. Criterios de seguridad aplicados en el código final

| Riesgo | Qué hace el código | Dónde |
|---|---|---|
| Inyección SQL | Consultas parametrizadas (`?` / `%s`), nunca concatenación | `persistencia/*_dao.py`, `conexion.marcador()` |
| Contraseñas expuestas | Se guarda solo el hash bcrypt con sal; `Usuario.__repr__` no muestra el hash | `servicios/autenticacion.py`, `dominio/usuario.py` |
| Enumeración de usuarios | Mismo mensaje "Usuario o contraseña incorrectos." para usuario inexistente o clave errónea | `presentacion/menu_usuario.py` |
| Falla de BD no debe dar acceso | `ErrorBD` se propaga y el login se rechaza | `servicios/autenticacion.autenticar` |
| Acciones sin permiso | `exigir_admin` / `exigir_sesion` antes de tocar DAO o API (no basta ocultar el menú) | `servicios/permisos.py` |
| Rol elegido por el usuario | Las cuentas nuevas siempre son `empleado`; solo admin crea cuentas | `crear_cuenta_empleado` |
| Llamadas externas colgadas | `timeout=(3, 5)` y `raise_for_status()` | `servicios/api_indicadores.py` |
| API caída o respuesta inválida | `except (RequestException, ValueError)` → respaldo local con la fecha original | `servicios/indicadores.py` |
| Datos externos no confiables | El JSON se convierte en `Indicador`, que valida código, fecha y valor positivo | `dominio/indicador.py` |
| Mensajes que filtran detalles | El usuario ve mensajes genéricos; el detalle va a `ecotech.log` | `presentacion/comun.py`, `main.py` |
| Secretos en el repositorio | `.env`, `*.db` y `*.log` en `.gitignore`; se entrega `.env.example` | `.gitignore` |
| Entradas del usuario | Validación por campo y reintento; ID positivo; código de indicador permitido solo `uf`/`dolar` | `presentacion/comun.py`, `servicios/indicadores.py` |

## 4. Limitaciones conocidas
- La API real de indicadores y MySQL deben probarse en el equipo del grupo (ver `Docs/matriz_pruebas.md`).
- El correo único se valida en la aplicación, no con restricción UNIQUE en la tabla.
