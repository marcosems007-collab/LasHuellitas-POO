import sqlite3
from datetime import datetime
from dao.database import conectar
from model.perro import Perro
from model.gato import Gato
from model.animal_exotico import AnimalExotico


class MascotaDAO:
    @staticmethod
    def insertar(mascota):
        conexion = conectar()
        try:
            conexion.execute("""
                INSERT INTO mascota (numero_microchip, tipo, fecha_ultima_vacuna, nombre)
                VALUES (?, ?, ?, ?)
            """, (mascota.numeroMicrochip, mascota.__class__.__name__, mascota.fechaUltimaVacuna.isoformat(), mascota.nombre))
            conexion.commit()
            return True
        except sqlite3.Error as e:
            conexion.rollback()
            print(f"Error SQLite al guardar mascota: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def _crear_mascota(row):
        mc, tipo, fecha, nombre = row
        fecha_vacuna = datetime.fromisoformat(fecha)
        clases = {"Perro": Perro, "Gato": Gato, "AnimalExotico": AnimalExotico}
        clase = clases.get(tipo)
        return clase(mc, fecha_vacuna, nombre) if clase else None

    @staticmethod
    def obtener_por_microchip(numero_microchip):
        conexion = conectar()
        try:
            row = conexion.execute("SELECT numero_microchip, tipo, fecha_ultima_vacuna, nombre FROM mascota WHERE numero_microchip = ?", (numero_microchip,)).fetchone()
            return MascotaDAO._crear_mascota(row) if row else None
        except (sqlite3.Error, ValueError) as e:
            print(f"Error al buscar mascota: {e}")
            return None
        finally:
            conexion.close()

    @staticmethod
    def obtener_todos():
        conexion = conectar()
        try:
            rows = conexion.execute("SELECT numero_microchip, tipo, fecha_ultima_vacuna, nombre FROM mascota ORDER BY nombre").fetchall()
            return [MascotaDAO._crear_mascota(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error SQLite al leer mascotas: {e}")
            return []
        finally:
            conexion.close()

    @staticmethod
    def actualizar(mascota):
        conexion = conectar()
        try:
            cursor = conexion.execute("""
                UPDATE mascota SET tipo = ?, fecha_ultima_vacuna = ?, nombre = ?
                WHERE numero_microchip = ?
            """, (mascota.__class__.__name__, mascota.fechaUltimaVacuna.isoformat(), mascota.nombre, mascota.numeroMicrochip))
            conexion.commit()
            return cursor.rowcount == 1
        except sqlite3.Error as e:
            conexion.rollback()
            print(f"Error al actualizar mascota: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def eliminar(numero_microchip):
        conexion = conectar()
        try:
            cursor = conexion.execute("DELETE FROM mascota WHERE numero_microchip = ?", (numero_microchip,))
            conexion.commit()
            return cursor.rowcount == 1
        except sqlite3.Error as e:
            conexion.rollback()
            print(f"Error al eliminar mascota: {e}")
            return False
        finally:
            conexion.close()
