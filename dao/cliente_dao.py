import sqlite3
from dao.database import conectar
from model.cliente import Cliente

class ClienteDAO:
    @staticmethod
    def insertar(cliente):
        conexion = None
        try:
            conexion = conectar()
            cursor = conexion.execute("""
                INSERT OR IGNORE INTO cliente (rut, nombre, correo, telefono, dias_deuda)
                VALUES (?, ?, ?, ?, ?)
            """, (cliente.rut, cliente.nombre, cliente.correo, cliente.telefono, cliente.diasDeuda))
            if cursor.rowcount == 0:
                conexion.rollback()
                return False
            id_cliente = cursor.lastrowid
            conexion.commit()
            cliente.idCliente = id_cliente
            return True
        except sqlite3.Error as e:
            if conexion:
                conexion.rollback()
            print(f"Error SQLite al insertar cliente: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_por_rut(rut):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_cliente, rut, nombre, correo, telefono, dias_deuda FROM cliente WHERE rut = ?", (rut,))
            row = cursor.fetchone()
            if row:
                return Cliente(row[1], row[2], row[3], row[4], row[0], row[5])
            return None
        except sqlite3.Error as e:
            print(f"Error SQLite al buscar cliente: {e}")
            return None
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def obtener_todos():
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM cliente")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error SQLite al leer clientes: {e}")
            return []
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def actualizar(cliente):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE cliente SET rut = ?, nombre = ?, correo = ?, telefono = ?, dias_deuda = ?
                WHERE id_cliente = ?
            """, (cliente.rut, cliente.nombre, cliente.correo, cliente.telefono, cliente.diasDeuda, cliente.idCliente))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error SQLite al actualizar cliente: {e}")
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def eliminar(id_cliente):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM cliente WHERE id_cliente = ?", (id_cliente,))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error SQLite al eliminar cliente: {e}")
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

