import os
import sqlite3
from pathlib import Path


RUTA_BASE = Path(__file__).resolve().parents[1]


def conectar():
    """Conecta a la base configurada o al archivo local de la aplicación."""
    # La BD no depende de la carpeta desde la que se invoque `python main.py`.
    ruta = os.environ.get("HUELLITAS_DB_PATH", str(RUTA_BASE / "las_huellitas.db"))
    return sqlite3.connect(ruta)


def crear_tablas():
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL,
                telefono TEXT,
                dias_deuda INTEGER NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mascota (
                numero_microchip TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                fecha_ultima_vacuna TEXT NOT NULL,
                nombre TEXT NOT NULL DEFAULT 'Mascota'
            )
        """)
        columnas = {fila[1] for fila in cursor.execute("PRAGMA table_info(mascota)")}
        if "nombre" not in columnas:
            cursor.execute("ALTER TABLE mascota ADD COLUMN nombre TEXT NOT NULL DEFAULT 'Mascota'")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atencion (
                id_atencion INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                diagnostico TEXT,
                total REAL,
                rut_cliente TEXT,
                microchip_mascota TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_atencion (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_atencion INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                costo REAL NOT NULL,
                FOREIGN KEY (id_atencion) REFERENCES atencion(id_atencion)
            )
        """)
        conexion.commit()
    finally:
        conexion.close()
