
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Literal

from .database import obtener_conexion, calcular_dias_vacaciones

# ==========================================
# MODULO DE VACACIONES - TALENTCORE
# ==========================================

router = APIRouter(
    prefix="/vacaciones",
    tags=["Vacaciones"]
)


# ==========================================
# MODELOS DE DATOS
# ==========================================

class SolicitudVacaciones(BaseModel):
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    motivo: str


class CambioEstado(BaseModel):
    estado: Literal["Aprobada", "Rechazada"]


# ==========================================
# FUNCION AUXILIAR
# ==========================================

def convertir_solicitud(fila):
    return dict(fila)


# ==========================================
# 1. REGISTRAR SOLICITUD
# ==========================================

@router.post("/")
def solicitar_vacaciones(solicitud: SolicitudVacaciones):

    if solicitud.fecha_fin < solicitud.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha final no puede ser anterior a la inicial"
        )

    conexion = obtener_conexion()

    try:
        empleado = conexion.execute(
            "SELECT id FROM empleados WHERE id = ?",
            (solicitud.empleado_id,)
        ).fetchone()

        if empleado is None:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        dias_solicitados = (
            solicitud.fecha_fin - solicitud.fecha_inicio
        ).days + 1

        cursor = conexion.execute(
            """
            INSERT INTO vacaciones (
                empleado_id,
                fecha_inicio,
                fecha_fin,
                motivo,
                dias_solicitados,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                solicitud.empleado_id,
                solicitud.fecha_inicio.isoformat(),
                solicitud.fecha_fin.isoformat(),
                solicitud.motivo,
                dias_solicitados,
                "Pendiente"
            )
        )

        conexion.commit()

        nueva_solicitud = conexion.execute(
            "SELECT * FROM vacaciones WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return {
            "mensaje": "Solicitud registrada correctamente",
            "solicitud": convertir_solicitud(nueva_solicitud)
        }

    finally:
        conexion.close()


# ==========================================
# 2. LISTAR TODAS LAS SOLICITUDES
# ==========================================

@router.get("/")
def listar_vacaciones():

    conexion = obtener_conexion()

    try:
        solicitudes = conexion.execute(
            "SELECT * FROM vacaciones ORDER BY id"
        ).fetchall()

        return [
            convertir_solicitud(fila)
            for fila in solicitudes
        ]

    finally:
        conexion.close()


# ==========================================
# 3. CONSULTAR UNA SOLICITUD
# ==========================================

@router.get("/{solicitud_id}")
def buscar_solicitud(solicitud_id: int):

    conexion = obtener_conexion()

    try:
        solicitud = conexion.execute(
            "SELECT * FROM vacaciones WHERE id = ?",
            (solicitud_id,)
        ).fetchone()

        if solicitud is None:
            raise HTTPException(
                status_code=404,
                detail="Solicitud no encontrada"
            )

        return convertir_solicitud(solicitud)

    finally:
        conexion.close()


# ==========================================
# 4. APROBAR O RECHAZAR VACACIONES
# ==========================================

@router.put("/{solicitud_id}/estado")
def cambiar_estado(
    solicitud_id: int,
    cambio: CambioEstado
):

    conexion = obtener_conexion()

    try:
        # Iniciar transaccion para proteger la validacion
        conexion.execute("BEGIN IMMEDIATE")

        solicitud = conexion.execute(
            "SELECT * FROM vacaciones WHERE id = ?",
            (solicitud_id,)
        ).fetchone()

        if solicitud is None:
            raise HTTPException(
                status_code=404,
                detail="Solicitud no encontrada"
            )

        if solicitud["estado"] != "Pendiente":
            raise HTTPException(
                status_code=400,
                detail="La solicitud ya fue procesada"
            )

        # NUEVA VALIDACION: COMPROBAR SALDO
        if cambio.estado == "Aprobada":

            empleado = conexion.execute(
                """
                SELECT anios_antiguedad
                FROM empleados
                WHERE id = ?
                """,
                (solicitud["empleado_id"],)
            ).fetchone()

            if empleado is None:
                raise HTTPException(
                    status_code=404,
                    detail="Empleado no encontrado"
                )

            dias_anuales = calcular_dias_vacaciones(
                empleado["anios_antiguedad"]
            )

            resultado = conexion.execute(
                """
                SELECT COALESCE(SUM(dias_solicitados), 0)
                FROM vacaciones
                WHERE empleado_id = ?
                  AND estado = 'Aprobada'
                """,
                (solicitud["empleado_id"],)
            ).fetchone()

            dias_utilizados = resultado[0]
            dias_disponibles = max(
                0,
                dias_anuales - dias_utilizados
            )

            if solicitud["dias_solicitados"] > dias_disponibles:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Saldo insuficiente de vacaciones. "
                        f"Dias disponibles: {dias_disponibles}. "
                        f"Dias solicitados: "
                        f"{solicitud['dias_solicitados']}."
                    )
                )

        conexion.execute(
            """
            UPDATE vacaciones
            SET estado = ?
            WHERE id = ?
            """,
            (cambio.estado, solicitud_id)
        )

        conexion.commit()

        solicitud_actualizada = conexion.execute(
            "SELECT * FROM vacaciones WHERE id = ?",
            (solicitud_id,)
        ).fetchone()

        return {
            "mensaje": "Estado actualizado correctamente",
            "solicitud": convertir_solicitud(
                solicitud_actualizada
            )
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ==========================================
# 5. HISTORIAL DE VACACIONES POR EMPLEADO
# ==========================================

@router.get("/empleado/{empleado_id}/historial")
def historial_vacaciones(empleado_id: int):

    conexion = obtener_conexion()

    try:
        empleado = conexion.execute(
            "SELECT id FROM empleados WHERE id = ?",
            (empleado_id,)
        ).fetchone()

        if empleado is None:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        solicitudes = conexion.execute(
            """
            SELECT *
            FROM vacaciones
            WHERE empleado_id = ?
            ORDER BY id
            """,
            (empleado_id,)
        ).fetchall()

        historial = [
            convertir_solicitud(fila)
            for fila in solicitudes
        ]

        return {
            "empleado_id": empleado_id,
            "total_solicitudes": len(historial),
            "historial": historial
        }

    finally:
        conexion.close()


# ==========================================
# 6. CONSULTAR SALDO DE VACACIONES
# ==========================================

@router.get("/empleado/{empleado_id}/saldo")
def consultar_saldo_vacaciones(empleado_id: int):

    conexion = obtener_conexion()

    try:
        empleado = conexion.execute(
            """
            SELECT id, nombre, apellido, anios_antiguedad
            FROM empleados
            WHERE id = ?
            """,
            (empleado_id,)
        ).fetchone()

        if empleado is None:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        dias_anuales = calcular_dias_vacaciones(
            empleado["anios_antiguedad"]
        )

        resumen = conexion.execute(
            """
            SELECT
                COALESCE(SUM(
                    CASE WHEN estado = 'Aprobada'
                    THEN dias_solicitados ELSE 0 END
                ), 0) AS dias_utilizados,

                COALESCE(SUM(
                    CASE WHEN estado = 'Pendiente'
                    THEN dias_solicitados ELSE 0 END
                ), 0) AS dias_pendientes

            FROM vacaciones
            WHERE empleado_id = ?
            """,
            (empleado_id,)
        ).fetchone()

        dias_utilizados = resumen["dias_utilizados"]
        dias_pendientes = resumen["dias_pendientes"]

        dias_disponibles = max(
            0,
            dias_anuales - dias_utilizados
        )

        return {
            "empleado_id": empleado_id,
            "nombre": empleado["nombre"],
            "apellido": empleado["apellido"],
            "anios_antiguedad": empleado["anios_antiguedad"],
            "dias_anuales": dias_anuales,
            "dias_utilizados": dias_utilizados,
            "dias_pendientes": dias_pendientes,
            "dias_disponibles": dias_disponibles
        }

    finally:
        conexion.close()
