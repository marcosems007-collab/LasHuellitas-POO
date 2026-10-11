import sqlite3
from dao.database import conectar
from model.excepciones import ClienteMorosoError, MascotaNoAptaCirugiaError


class AtencionDAO:
    @staticmethod
    def insertar(atencion):
        # Revalidar al persistir protege también a quienes usan el DAO directamente.
        if atencion.cliente.estaMoroso():
            raise ClienteMorosoError(f"El cliente {atencion.cliente.nombre} presenta morosidad superior a 30 días.")
        if any(p.esCirugia for p in atencion.procedimientos) and not atencion.mascota.estaAptaParaCirugia():
            raise MascotaNoAptaCirugiaError("La cirugía requiere vacunas vigentes (últimos 365 días).")

        conexion = conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("BEGIN")
            cursor.execute("""
                INSERT INTO atencion (fecha_hora, diagnostico, total, rut_cliente, microchip_mascota)
                VALUES (?, ?, ?, ?, ?)
            """, (atencion.fechaHora.isoformat(), atencion.diagnostico, atencion.total, atencion.cliente.rut, atencion.mascota.numeroMicrochip))
            id_atencion = cursor.lastrowid
            lineas = [(f"Procedimiento: {p.nombre}", p.costo) for p in atencion.procedimientos]
            lineas.extend((f"Medicamento: {m.nombre}", m.calcularPrecioCLP(atencion.tipoCambioDolar)) for m in atencion.medicamentos)
            cursor.executemany("INSERT INTO detalle_atencion (id_atencion, descripcion, costo) VALUES (?, ?, ?)", [(id_atencion, descripcion, costo) for descripcion, costo in lineas])
            conexion.commit()
            return id_atencion
        except Exception as e:
            conexion.rollback()
            if isinstance(e, sqlite3.Error):
                print(f"Error SQLite al insertar atención (transacción cancelada): {e}")
                return None
            raise
        finally:
            conexion.close()

    @staticmethod
    def obtener_atencion_con_detalles(id_atencion):
        conexion = conectar()
        try:
            cabecera = conexion.execute("SELECT id_atencion, fecha_hora, diagnostico, total, rut_cliente, microchip_mascota FROM atencion WHERE id_atencion = ?", (id_atencion,)).fetchone()
            if not cabecera:
                return None
            detalles = conexion.execute("SELECT id_detalle, descripcion, costo FROM detalle_atencion WHERE id_atencion = ? ORDER BY id_detalle", (id_atencion,)).fetchall()
            return {"cabecera": cabecera, "detalles": detalles}
        except sqlite3.Error as e:
            print(f"Error SQLite al obtener atención: {e}")
            return None
        finally:
            conexion.close()
