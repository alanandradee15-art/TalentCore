# Reporte QA – TalentCore

## 1. Resumen ejecutivo  
El proyecto TalentCore, una aplicación monolítica basada en FastAPI, ha sido sometido a un conjunto de pruebas automatizadas con Pytest. Los 20 casos de prueba definidos en `tests/test_talentcore.py` se ejecutaron correctamente, confirmando la funcionalidad básica de gestión de empleados y solicitudes de vacaciones. Se detectó una advertencia de deprecación de Starlette, pero no afecta la ejecución de las pruebas.

## 2. Resultados reales de Pytest  
```
======================== 20 passed, 1 warning in 1.20s ========================
```
Todos los tests pasaron sin errores. La advertencia es de tipo `StarletteDeprecationWarning` relacionada con `httpx` y no impacta la cobertura funcional.

## 3. Funcionalidades verificadas  
| Funcionalidad | Test asociado | Resultado |
|---------------|---------------|-----------|
| Página principal | `test_pagina_principal` | ✔ |
| Salud del servidor | `test_salud_servidor` | ✔ |
| Listar empleados | `test_listar_empleados` | ✔ |
| Empleado inexistente | `test_empleado_inexistente` | ✔ |
| Vacaciones inexistentes | `test_vacaciones_inexistentes` | ✔ |
| Calcular días de vacaciones (varios casos) | `test_calcular_dias_vacaciones` | ✔ |
| Listar vacaciones | `test_listar_vacaciones` | ✔ |
| Historial de vacaciones | `test_historial_vacaciones` | ✔ |
| Consultar saldo | `test_consultar_saldo` | ✔ |
| Saldo empleado inexistente | `test_saldo_empleado_inexistente` | ✔ |
| Historial empleado inexistente | `test_historial_empleado_inexistente` | ✔ |
| Registrar empleado | `test_registrar_empleado` | ✔ |
| Consultar empleado registrado | `test_consultar_empleado_registrado` | ✔ |
| Registrar solicitud de vacaciones | `test_registrar_solicitud_vacaciones` | ✔ |

## 4. Pruebas pendientes  
- **Pruebas de autorización**: Validar que solo los roles correctos puedan crear, actualizar o eliminar empleados y solicitudes.  
- **Pruebas de flujo de aprobación/rechazo**: Confirmar que los supervisores y HR puedan aprobar o rechazar solicitudes y que el estado se actualice correctamente.  
- **Pruebas de integridad referencial**: Verificar que la eliminación de un empleado no deje registros huérfanos en la tabla de vacaciones.  
- **Pruebas de rendimiento**: Medir tiempos de respuesta bajo carga simulada.  
- **Pruebas de eventos Kafka**: Asegurar que las notificaciones y auditorías se publiquen correctamente.  
- **Pruebas de migraciones**: Confirmar que las migraciones de la base de datos se apliquen sin errores.  

## 5. Riesgos principales  
1. **Falta de pruebas de seguridad**: No se ha verificado la protección contra inyección SQL, CSRF o XSS.  
2. **Dependencia de `httpx` obsoleto**: La advertencia indica que la librería `httpx` está desactualizada; podría generar incompatibilidades futuras.  
3. **Cobertura limitada**: Solo se cubren casos de éxito; los escenarios de error (p.ej., datos inválidos, límites de negocio) no están testeados.  
4. **Persistencia de datos**: No se han validado las reglas de negocio de saldo de vacaciones (p.ej., no permitir solicitudes que excedan el saldo).  

## 6. Recomendaciones priorizadas  
1. **Implementar pruebas de autorización y flujo de aprobación** (prioridad alta).  
2. **Actualizar `httpx` a la versión 2.x** y ajustar el cliente de pruebas para eliminar la advertencia.  
3. **Añadir pruebas de validación de datos** (formato de fechas, motivos obligatorios, límites de días).  
4. **Realizar pruebas de rendimiento y carga** para garantizar la escalabilidad.  
5. **Agregar pruebas de eventos Kafka** para asegurar la correcta publicación y consumo de eventos.  
6. **Revisar y documentar las reglas de negocio de saldo** y crear tests que verifiquen su cumplimiento.  

> **Nota**: Los documentos presentados son extractos y no representan la totalidad del proyecto.