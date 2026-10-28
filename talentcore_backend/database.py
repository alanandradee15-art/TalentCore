
import sqlite3
from pathlib import Path

# ==========================================
# BASE DE DATOS - TALENTCORE
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "talentcore.db"


def obtener_conexion():
    conexion = sqlite3.connect(DATABASE_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


# ==========================================
# FORMULA DE VACACIONES DEL PROFESOR
# ==========================================

def calcular_dias_vacaciones(anios_antiguedad):
    if anios_antiguedad < 1:
        return 0

    return min(
        12 + 2 * (anios_antiguedad - 1),
        20
    )


# ==========================================
# AGREGAR COLUMNAS SIN BORRAR REGISTROS
# ==========================================

def agregar_columna_si_falta(conexion, tabla, columna, definicion):
    columnas = {
        fila["name"]
        for fila in conexion.execute(
            f"PRAGMA table_info({tabla})"
        ).fetchall()
    }

    if columna not in columnas:
        conexion.execute(
            f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}"
        )


# ==========================================
# INICIALIZAR Y ACTUALIZAR BASE DE DATOS
# ==========================================

def inicializar_base_datos():
    conexion = obtener_conexion()

    try:
        # Crear tablas originales si no existen
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                correo TEXT NOT NULL,
                puesto TEXT NOT NULL,
                departamento TEXT NOT NULL
            )
        """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS vacaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empleado_id INTEGER NOT NULL,
                fecha_inicio TEXT NOT NULL,
                fecha_fin TEXT NOT NULL,
                motivo TEXT NOT NULL,
                dias_solicitados INTEGER NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Pendiente',
                FOREIGN KEY (empleado_id)
                    REFERENCES empleados(id)
            )
        """)

        # Nuevos datos de empleados
        agregar_columna_si_falta(
            conexion, "empleados", "rol",
            "TEXT NOT NULL DEFAULT 'Empleado'"
        )

        agregar_columna_si_falta(
            conexion, "empleados", "anios_antiguedad",
            "INTEGER NOT NULL DEFAULT 1"
        )

        agregar_columna_si_falta(
            conexion, "empleados", "manager_id",
            "INTEGER REFERENCES empleados(id)"
        )

        # Nuevos datos de solicitudes
        agregar_columna_si_falta(
            conexion, "vacaciones", "aprobador_id",
            "INTEGER REFERENCES empleados(id)"
        )

        agregar_columna_si_falta(
            conexion, "vacaciones", "comentario_decision",
            "TEXT"
        )

        agregar_columna_si_falta(
            conexion, "vacaciones", "fecha_decision",
            "TEXT"
        )

        # Tabla para auditoria
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                accion TEXT NOT NULL,
                entidad TEXT NOT NULL,
                entidad_id INTEGER,
                fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                detalle TEXT
            )
        """)

        conexion.commit()

        print(
            "Base de datos TalentCore "
            "actualizada correctamente"
        )

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


if __name__ == "__main__":
    inicializar_base_datos()
