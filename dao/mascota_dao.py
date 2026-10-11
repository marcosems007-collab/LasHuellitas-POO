import sqlite3
from dao.database import conectar

class MascotaDAO:
    @staticmethod
    def insertar(mascota):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            tipo = mascota.__class__.__name__
            cursor.execute("""
                INSERT OR IGNORE INTO mascota (numero_microchip, tipo, fecha_ultima_vacuna)
                VALUES (?, ?, ?)
            """, (mascota.numeroMicrochip, tipo, mascota.fechaUltimaVacuna.isoformat()))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error SQLite al insertar mascota: {e}")
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def obtener_por_microchip(numero_microchip):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT numero_microchip, tipo, fecha_ultima_vacuna FROM mascota WHERE numero_microchip = ?", (numero_microchip,))
            row = cursor.fetchone()
            if not row:
                return None
                
            mc, tipo, fecha_str = row
            from datetime import datetime
            fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S") if 'T' in fecha_str else datetime.strptime(fecha_str, "%Y-%m-%d")
            
            if tipo == 'Perro':
                from model.perro import Perro
                return Perro(mc, fecha)
            elif tipo == 'Gato':
                from model.gato import Gato
                return Gato(mc, fecha)
            elif tipo == 'AnimalExotico':
                from model.animal_exotico import AnimalExotico
                return AnimalExotico(mc, fecha)
            return None
        except sqlite3.Error as e:
            print(f"Error SQLite al buscar mascota: {e}")
            return None
        except Exception as e:
            print(f"Error parseando mascota: {e}")
            return None
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def obtener_todos():
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM mascota")
            return cursor.fetchall()
        except sqlite3.Error:
            return []
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def actualizar(mascota):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            tipo = mascota.__class__.__name__
            cursor.execute("""
                UPDATE mascota SET tipo = ?, fecha_ultima_vacuna = ?
                WHERE numero_microchip = ?
            """, (tipo, mascota.fechaUltimaVacuna.isoformat(), mascota.numeroMicrochip))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al actualizar mascota: {e}")
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def eliminar(numero_microchip):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM mascota WHERE numero_microchip = ?", (numero_microchip,))
            conexion.commit()
        except sqlite3.Error:
            pass
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

