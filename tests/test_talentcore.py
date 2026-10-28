
import sqlite3

import pytest
from fastapi.testclient import TestClient

from talentcore_backend.main import app
from talentcore_backend.database import (
    calcular_dias_vacaciones,
    inicializar_base_datos,
)
from talentcore_backend import database


client = TestClient(app)


# BASE DE DATOS TEMPORAL PARA TODAS LAS PRUEBAS
@pytest.fixture(autouse=True)
def base_temporal(tmp_path, monkeypatch):
    ruta_temporal = tmp_path / "talentcore_pruebas.db"

    # Redirigir la aplicacion a una base temporal.
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        ruta_temporal,
    )

    # Crear las tablas de empleados y vacaciones.
    inicializar_base_datos()

    # Crear empleado de ejemplo con ID 1.
    conexion = database.obtener_conexion()
    try:
        conexion.execute(
            """
            INSERT INTO empleados (
                id,
                nombre,
                apellido,
                correo,
                puesto,
                departamento,
                anios_antiguedad
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "Empleado",
                "Prueba",
                "empleado.prueba@example.com",
                "Analista",
                "Tecnologia",
                2,
            ),
        )
        conexion.commit()
    finally:
        conexion.close()

    yield ruta_temporal


# PRUEBA 1: Pagina principal
def test_pagina_principal():
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == "Bienvenido a TalentCore"


# PRUEBA 2: Salud del servidor
def test_salud_servidor():
    respuesta = client.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "OK"


# PRUEBA 3: Listar empleados
def test_listar_empleados():
    respuesta = client.get("/api/v1/empleados")

    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


# PRUEBA 4: Empleado inexistente
def test_empleado_inexistente():
    respuesta = client.get("/api/v1/empleados/999999")

    assert respuesta.status_code == 404


# PRUEBA 5: Solicitud inexistente
def test_vacaciones_inexistentes():
    respuesta = client.get("/vacaciones/999999")

    assert respuesta.status_code == 404


# PRUEBAS 6 A 12: Calculo por antiguedad
@pytest.mark.parametrize(
    "antiguedad, esperado",
    [
        (0, 0),
        (1, 12),
        (2, 14),
        (3, 16),
        (4, 18),
        (5, 20),
        (6, 20),
    ],
)
def test_calcular_dias_vacaciones(antiguedad, esperado):
    assert calcular_dias_vacaciones(antiguedad) == esperado


# PRUEBA 13: Listar vacaciones
def test_listar_vacaciones():
    respuesta = client.get("/vacaciones/")

    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


# PRUEBA 14: Historial de vacaciones
def test_historial_vacaciones():
    respuesta = client.get("/vacaciones/empleado/1/historial")

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["empleado_id"] == 1
    assert isinstance(datos["historial"], list)
    assert datos["total_solicitudes"] == len(datos["historial"])


# PRUEBA 15: Consultar saldo
def test_consultar_saldo():
    respuesta = client.get("/vacaciones/empleado/1/saldo")

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["empleado_id"] == 1
    assert "dias_anuales" in datos
    assert "dias_utilizados" in datos
    assert "dias_pendientes" in datos
    assert "dias_disponibles" in datos

    assert datos["dias_disponibles"] == max(
        0,
        datos["dias_anuales"] - datos["dias_utilizados"],
    )


# PRUEBA 16: Saldo de empleado inexistente
def test_saldo_empleado_inexistente():
    respuesta = client.get("/vacaciones/empleado/999999/saldo")

    assert respuesta.status_code == 404


# PRUEBA 17: Historial de empleado inexistente
def test_historial_empleado_inexistente():
    respuesta = client.get("/vacaciones/empleado/999999/historial")

    assert respuesta.status_code == 404


# PRUEBA 18: Registrar un empleado
def test_registrar_empleado():
    datos = {
        "nombre": "Laura",
        "apellido": "Gomez",
        "correo": "laura.prueba@example.com",
        "puesto": "Analista",
        "departamento": "Recursos Humanos",
        "anios_antiguedad": 2,
    }

    respuesta = client.post(
        "/api/v1/empleados",
        json=datos,
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert resultado["mensaje"] == (
        "Empleado registrado correctamente"
    )
    assert resultado["empleado"]["nombre"] == "Laura"
    assert resultado["empleado"]["apellido"] == "Gomez"
    assert resultado["empleado"]["anios_antiguedad"] == 2


# PRUEBA 19: Consultar empleado recien registrado
def test_consultar_empleado_registrado():
    datos = {
        "nombre": "Mario",
        "apellido": "Lopez",
        "correo": "mario.prueba@example.com",
        "puesto": "Desarrollador",
        "departamento": "Tecnologia",
        "anios_antiguedad": 1,
    }

    creacion = client.post(
        "/api/v1/empleados",
        json=datos,
    )

    assert creacion.status_code == 200

    empleado_id = creacion.json()["empleado"]["id"]

    respuesta = client.get(
        f"/api/v1/empleados/{empleado_id}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Mario"
    assert respuesta.json()["correo"] == datos["correo"]


# PRUEBA 20: Registrar solicitud de vacaciones
def test_registrar_solicitud_vacaciones():
    empleado = {
        "nombre": "Sofia",
        "apellido": "Martinez",
        "correo": "sofia.prueba@example.com",
        "puesto": "Administradora",
        "departamento": "Administracion",
        "anios_antiguedad": 3,
    }

    creacion = client.post(
        "/api/v1/empleados",
        json=empleado,
    )

    assert creacion.status_code == 200

    empleado_id = creacion.json()["empleado"]["id"]

    solicitud = {
        "empleado_id": empleado_id,
        "fecha_inicio": "2027-04-05",
        "fecha_fin": "2027-04-07",
        "motivo": "Prueba automatica de TalentCore",
    }

    respuesta = client.post(
        "/vacaciones/",
        json=solicitud,
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert resultado["mensaje"] == (
        "Solicitud registrada correctamente"
    )
    assert resultado["solicitud"]["empleado_id"] == empleado_id
    assert resultado["solicitud"]["estado"] == "Pendiente"
    assert resultado["solicitud"]["dias_solicitados"] == 3
