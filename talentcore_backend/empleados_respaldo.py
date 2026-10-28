
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from .database import obtener_conexion

# ==========================================
# MODULO DE EMPLEADOS - TALENTCORE
# ==========================================

router = APIRouter(
    prefix="/empleados",
    tags=["Empleados"]
)


# ==========================================
# MODELOS DE DATOS
# ==========================================

class EmpleadoCrear(BaseModel):
    nombre: str = Field(min_length=1)
    apellido: str = Field(min_length=1)
    correo: str
    puesto: str
    departamento: str
    anios_antiguedad: int = Field(default=1, ge=0)


class EmpleadoActualizar(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    puesto: Optional[str] = None
    departamento: Optional[str] = None
    anios_antiguedad: Optional[int] = Field(default=None, ge=0)


# ==========================================
# 1. REGISTRAR EMPLEADO
# ==========================================

@router.post("/")
def registrar_empleado(empleado: EmpleadoCrear):
    conexion = obtener_conexion()

    try:
        cursor = conexion.execute(
            """
            INSERT INTO empleados (
                nombre,
                apellido,
                correo,
                puesto,
                departamento,
                anios_antiguedad
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                empleado.nombre,
                empleado.apellido,
                empleado.correo,
                empleado.puesto,
                empleado.departamento,
                empleado.anios_antiguedad
            )
        )

        empleado_id = cursor.lastrowid
        conexion.commit()

        nuevo = conexion.execute(
            "SELECT * FROM empleados WHERE id = ?",
            (empleado_id,)
        ).fetchone()

        return {
            "mensaje": "Empleado registrado correctamente",
            "empleado": dict(nuevo)
        }

    finally:
        conexion.close()


# ==========================================
# 2. LISTAR EMPLEADOS
# ==========================================

@router.get("/")
def listar_empleados():
    conexion = obtener_conexion()

    try:
        registros = conexion.execute(
            "SELECT * FROM empleados ORDER BY id"
        ).fetchall()

        return [dict(fila) for fila in registros]

    finally:
        conexion.close()


# ==========================================
# 3. BUSCAR EMPLEADO
# ==========================================

@router.get("/{empleado_id}")
def buscar_empleado(empleado_id: int):
    conexion = obtener_conexion()

    try:
        empleado = conexion.execute(
            "SELECT * FROM empleados WHERE id = ?",
            (empleado_id,)
        ).fetchone()

        if empleado is None:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        return dict(empleado)

    finally:
        conexion.close()


# ==========================================
# 4. MODIFICAR EMPLEADO
# ==========================================

@router.put("/{empleado_id}")
def modificar_empleado(
    empleado_id: int,
    datos: EmpleadoActualizar
):
    conexion = obtener_conexion()

    try:
        empleado = conexion.execute(
            "SELECT * FROM empleados WHERE id = ?",
            (empleado_id,)
        ).fetchone()

        if empleado is None:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        cambios = datos.model_dump(exclude_unset=True)

        if "anios_antiguedad" in cambios:
            if cambios["anios_antiguedad"] is None:
                raise HTTPException(
                    status_code=400,
                    detail="La antiguedad no puede ser nula"
                )

        if cambios:
            campos = ", ".join(
                f"{campo} = ?" for campo in cambios
            )

            valores = list(cambios.values())
            valores.append(empleado_id)

            conexion.execute(
                f"UPDATE empleados SET {campos} WHERE id = ?",
                valores
            )

            conexion.commit()

        actualizado = conexion.execute(
            "SELECT * FROM empleados WHERE id = ?",
            (empleado_id,)
        ).fetchone()

        return {
            "mensaje": "Empleado actualizado correctamente",
            "empleado": dict(actualizado)
        }

    finally:
        conexion.close()


# ==========================================
# 5. ELIMINAR EMPLEADO
# ==========================================

@router.delete("/{empleado_id}")
def eliminar_empleado(empleado_id: int):
    conexion = obtener_conexion()

    try:
        empleado = conexion.execute(
            "SELECT * FROM empleados WHERE id = ?",
            (empleado_id,)
        ).fetchone()

        if empleado is None:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        solicitudes = conexion.execute(
            """
            SELECT COUNT(*)
            FROM vacaciones
            WHERE empleado_id = ?
            """,
            (empleado_id,)
        ).fetchone()[0]

        if solicitudes > 0:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se puede eliminar el empleado "
                    "porque tiene solicitudes de vacaciones"
                )
            )

        conexion.execute(
            "DELETE FROM empleados WHERE id = ?",
            (empleado_id,)
        )

        conexion.commit()

        return {
            "mensaje": "Empleado eliminado correctamente"
        }

    finally:
        conexion.close()
