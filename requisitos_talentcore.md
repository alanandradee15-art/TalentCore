# TalentCore – Sistema de Gestión de Empleados y Vacaciones

## Descripción del Producto  
Aplicación web que permite a la organización registrar y mantener datos de empleados, gestionar solicitudes de vacaciones y controlar el saldo y el historial de días utilizados. El sistema facilita la aprobación o rechazo de solicitudes por parte de los responsables y ofrece visibilidad completa de los registros de vacaciones.

## Actores  
| Actor | Rol | Responsabilidad principal |
|-------|-----|---------------------------|
| **Empleado** | Usuario final | Solicitar vacaciones, consultar saldo y historial |
| **Supervisor / Manager** | Aprobador | Revisar y aprobar/rechazar solicitudes de sus subordinados |
| **HR Manager** | Administrador de procesos | Supervisar todas las solicitudes, generar reportes, configurar reglas de negocio |
| **Administrador del Sistema** | Gestor de usuarios | Crear/editar/eliminar empleados, asignar roles y permisos |

## Alcance Funcional  
1. **Gestión de Empleados** – CRUD completo (crear, leer, actualizar, eliminar).  
2. **Solicitud de Vacaciones** – Empleado envía solicitud con fechas y motivo.  
3. **Aprobación/Rechazo** – Supervisor/HR revisa y decide.  
4. **Historial y Saldo** – Empleado y HR pueden consultar días disponibles y usados.  
5. **Notificaciones** – Email/SMS automático al empleado y aprobador.  
6. **Reportes** – Listado de solicitudes pendientes, aprobadas y rechazadas.  
7. **Seguridad** – Autenticación, autorización basada en roles y registro de auditoría.  

## Historias de Usuario (Prioridad)

| # | Prioridad | Historia | Criterios de Aceptación |
|---|-----------|----------|------------------------|
| 1 | **P1** | **Como empleado, quiero solicitar vacaciones** para poder planificar mis días libres. | 1. El empleado puede seleccionar rango de fechas y motivo. <br>2. Se valida que las fechas no se superpongan con solicitudes anteriores aprobadas. <br>3. Se muestra el saldo disponible antes de enviar. <br>4. La solicitud se guarda con estado “Pendiente”. <br>5. Se envía notificación al supervisor. |
| 2 | **P1** | **Como supervisor, quiero aprobar o rechazar solicitudes** para controlar el ausentismo. | 1. El supervisor ve lista de solicitudes pendientes. <br>2. Puede aprobar o rechazar con comentario opcional. <br>3. Al aprobar, el saldo del empleado se actualiza. <br>4. Se envía notificación al empleado con el resultado. |
| 3 | **P1** | **Como empleado, quiero consultar mi saldo de vacaciones** para saber cuántos días me quedan. | 1. La pantalla muestra días disponibles, usados y pendientes. <br>2. El saldo se actualiza en tiempo real tras aprobación/rechazo. |
| 4 | **P2** | **Como empleado, quiero ver mi historial de vacaciones** para revisar mis ausencias pasadas. | 1. Se listan todas las solicitudes con estado y fechas. <br>2. Se muestra detalle de cada solicitud (fecha, motivo, decisión). |
| 5 | **P2** | **Como HR Manager, quiero visualizar todas las solicitudes** para supervisar el cumplimiento de políticas. | 1. HR puede filtrar por empleado, estado, rango de fechas. <br>2. Se muestra información completa (empleado, fechas, aprobador, comentario). |
| 6 | **P2** | **Como HR Manager, quiero generar reportes de vacaciones** para análisis de ausentismo. | 1. Reporte exportable en PDF/Excel. <br>2. Incluye métricas: total días solicitados, aprobados, rechazados por período. |
| 7 | **P3** | **Como Administrador del Sistema, quiero gestionar empleados** (CRUD) para mantener datos actualizados. | 1. Se pueden crear, leer, actualizar y eliminar empleados. <br>2. Validación de campos obligatorios (nombre, email, ID). <br>3. Registro de auditoría de cambios. |
| 8 | **P3** | **Como Administrador del Sistema, quiero asignar roles y permisos** para controlar acceso. | 1. Se pueden crear roles (Empleado, Supervisor, HR, Admin). <br>2. Se asignan permisos específicos a cada rol. <br>3. Cambios se reflejan inmediatamente en la UI. |

## Reglas de Negocio a Confirmar  
1. **Límite anual de días** – ¿Cuántos días de vacaciones puede solicitar un empleado por año?  
2. **Política de acumulación** – ¿Se permite acumular días de años anteriores? Si es así, ¿cuál es el límite?  
3. **Periodo de solicitud** – ¿Cuánto tiempo antes de la fecha de inicio debe presentarse la solicitud?  
4. **Aprobación jerárquica** – ¿Requiere aprobación de supervisor y luego HR, o solo uno?  
5. **Intersección de fechas** – ¿Se permite que una solicitud se superponga parcialmente con otra aprobada?  
6. **Días no laborables** – ¿Se excluyen fines de semana y festivos del conteo de días?  
7. **Notificaciones** – ¿Qué canales (email, SMS, notificación interna) se utilizan y quiénes reciben?  
8. **Cancelación de solicitud** – ¿Puede el empleado cancelar una solicitud pendiente y bajo qué condiciones?  

## Dudas Pendientes  
- ¿Existe un proceso de “compensación” por horas extra que afecte el saldo de vacaciones?  
- ¿Se requiere firma electrónica o simplemente clic de aprobación?  
- ¿Qué nivel de detalle se necesita en los reportes (por departamento, por tipo de vacación)?  
- ¿Se integrará con sistemas externos (p. ej., calendario corporativo, ERP)?  
- ¿Qué mecanismo de auditoría se necesita (registro de IP, timestamp, usuario que modifica)?  

---