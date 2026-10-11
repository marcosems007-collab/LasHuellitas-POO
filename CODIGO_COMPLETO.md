# C�digo Completo - Las Huellitas POO

## Archivo: main.py

``python
from model.veterinario import Veterinario
from model.cliente import Cliente
from model.perro import Perro
from model.gato import Gato
from model.animal_exotico import AnimalExotico
from model.atencion import Atencion
from model.excepciones import ClienteMorosoError, MascotaNoAptaCirugiaError
from datetime import datetime

from dao.database import crear_tablas
from dao.cliente_dao import ClienteDAO
from dao.mascota_dao import MascotaDAO
from dao.atencion_dao import AtencionDAO
from service.indicador_api import obtener_valor_dolar

def mostrar_menu():
    print("\n=== CLÍNICA VETERINARIA HUELLITAS ===")
    print("1. Crear Mascota")
    print("2. Listar Mascotas")
    print("3. Modificar Mascota")
    print("4. Eliminar Mascota")
    print("5. Crear Cliente")
    print("6. Agendar Atención (con Validación de Deuda y Cirugía)")
    print("7. Ver Detalle Atención")
    print("0. Salir")
    opcion = input("Ingrese una opción: ")
    return opcion

def pedir_microchip():
    while True:
        mc = input("Ingrese número de microchip (15 dígitos): ")
        if len(mc) == 15 and mc.isdigit():
            return mc
        print("Error: El microchip debe tener exactamente 15 dígitos numéricos.")

def main():
    crear_tablas()
    dolar_actual = obtener_valor_dolar()
    veterinario = Veterinario("11223344-5", "Dr. Juan Pérez", "juan@huellitas.cl", "987654321", 101, "jperez", "pass")
    
    while True:
        opc = mostrar_menu()
        if opc == '0':
            print("Saliendo del sistema...")
            break
            
        elif opc == '1':
            print("\n--- Crear Mascota ---")
            mc = pedir_microchip()
            tipo = input("Tipo (Perro/Gato/Exotico): ").strip().lower()
            fecha_str = input("Fecha última vacuna (YYYY-MM-DD): ")
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                if tipo == "perro":
                    masc = Perro(mc, fecha)
                elif tipo == "gato":
                    masc = Gato(mc, fecha)
                elif tipo == "exotico":
                    masc = AnimalExotico(mc, fecha)
                else:
                    print("Tipo no válido.")
                    continue
                MascotaDAO.insertar(masc)
                print("Mascota guardada correctamente.")
            except ValueError as e:
                print(f"Error: {e}")
                
        elif opc == '2':
            print("\n--- Listar Mascotas ---")
            mascotas = MascotaDAO.obtener_todos()
            if not mascotas:
                print("No hay mascotas registradas.")
            for m in mascotas:
                print(f"Microchip: {m[0]}, Tipo: {m[1]}, Última Vacuna: {m[2]}")
                
        elif opc == '3':
            print("\n--- Modificar Mascota ---")
            mc = pedir_microchip()
            fecha_str = input("Nueva fecha última vacuna (YYYY-MM-DD): ")
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                # Necesitamos un objeto para actualizar. Aquí forzamos perro para el dao, el DAO solo usa microchip y fecha
                m_temp = Perro(mc, fecha) 
                MascotaDAO.actualizar(m_temp)
                print("Mascota actualizada.")
            except ValueError as e:
                print(f"Error: {e}")
                
        elif opc == '4':
            print("\n--- Eliminar Mascota ---")
            mc = pedir_microchip()
            MascotaDAO.eliminar(mc)
            print("Mascota eliminada.")
            
        elif opc == '5':
            print("\n--- Crear Cliente ---")
            rut = input("RUT: ")
            nombre = input("Nombre: ")
            correo = input("Correo: ")
            tel = input("Teléfono: ")
            try:
                deuda = int(input("Días de deuda (0 si no tiene): "))
                c = Cliente(rut, nombre, correo, tel, 999, deuda) # ID simulado, base de datos lo auto incrementa o usa el dado
                ClienteDAO.insertar(c)
                print("Cliente guardado.")
            except ValueError as e:
                print(f"Error de validación: {e}")
                
        elif opc == '6':
            print("\n--- Agendar Atención ---")
            rut = input("RUT del Cliente: ")
            mc = pedir_microchip()
            
            # Simulamos buscar al cliente y la mascota en la BD para instanciar (Para el proyecto, usaremos datos fijos o los recien ingresados)
            # En la vida real aquí haríamos un ClienteDAO.obtener_por_rut(rut)
            deuda = int(input("¿Cuántos días de deuda tiene el cliente en sistema? (Simulación de búsqueda): "))
            c = Cliente(rut, "Cliente Generico", "correo@mail.cl", "99999999", 1, deuda)
            
            fecha_vac_str = input("¿Fecha de última vacuna de la mascota? (YYYY-MM-DD) (Simulación de búsqueda): ")
            try:
                fecha_vac = datetime.strptime(fecha_vac_str, "%Y-%m-%d")
                m = Perro(mc, fecha_vac) # Perro por defecto para probar atencion
                
                atencion = Atencion(1, datetime.now(), dolar_actual, veterinario, m, c)
                atencion.diagnostico = input("Ingrese diagnóstico: ")
                
                print("Agregar procedimientos:")
                while True:
                    proc_nom = input("Nombre procedimiento (o 'fin' para terminar): ")
                    if proc_nom.lower() == 'fin': break
                    es_cirugia = input("¿Es cirugía? (s/n): ").lower() == 's'
                    costo = input("Costo: ")
                    try:
                        atencion.agregarProcedimiento(1, proc_nom, es_cirugia, float(costo))
                    except MascotaNoAptaCirugiaError as e:
                        print(f"⚠️ Error de Regla de Negocio: {e}")
                    except ValueError:
                        print("Costo inválido.")
                        
                print("Agregar medicamentos:")
                while True:
                    med_nom = input("Nombre medicamento (o 'fin' para terminar): ")
                    if med_nom.lower() == 'fin': break
                    usd = input("Precio en USD: ")
                    try:
                        atencion.agregarMedicamento(1, med_nom, float(usd), 0.20)
                    except ValueError:
                        print("Precio inválido.")
                
                total = atencion.procesarAtencion()
                atencion.total = total # Asignar el total a la atención para guardarla
                id_at = AtencionDAO.insertar(atencion)
                if id_at:
                    print(f"✅ Atención agendada y guardada exitosamente con ID {id_at}.")
                
            except ClienteMorosoError as e:
                print(f"⚠️ Error de Regla de Negocio: {e}")
            except ValueError as e:
                print(f"Error: {e}")
                
        elif opc == '7':
            print("\n--- Ver Detalle Atención ---")
            try:
                id_at = int(input("Ingrese ID de la Atención: "))
                data = AtencionDAO.obtener_atencion_con_detalles(id_at)
                if data:
                    print(f"Atención: {data['cabecera']}")
                    print("Detalles:")
                    for d in data['detalles']:
                        print(f" - {d}")
                else:
                    print("No se encontró la atención.")
            except ValueError:
                print("ID inválido.")
        elif opc == '99':
            print("Opción de prueba detectada. Retornando al menú...")
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
``

## Archivo: dao\atencion_dao.py

``python
import sqlite3
from dao.database import conectar

class AtencionDAO:
    @staticmethod
    def insertar(atencion):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Iniciar transacción para cabecera y detalles
            cursor.execute("BEGIN TRANSACTION;")
            
            cursor.execute("""
                INSERT INTO atencion (fecha_hora, diagnostico, total, rut_cliente, microchip_mascota)
                VALUES (?, ?, ?, ?, ?)
            """, (str(atencion.fechaHora), atencion.diagnostico, atencion.total, atencion.cliente.rut, atencion.mascota.numeroMicrochip))
            
            id_atencion = cursor.lastrowid
            
            # Insertar líneas de detalle (Procedimientos)
            for proc in atencion.procedimientos:
                cursor.execute("""
                    INSERT INTO detalle_atencion (id_atencion, descripcion, costo)
                    VALUES (?, ?, ?)
                """, (id_atencion, f"Procedimiento: {proc.nombre}", proc.costo))

            # Insertar líneas de detalle (Medicamentos)
            for med in atencion.medicamentos:
                costo_clp = med.calcularPrecioCLP(atencion.tipoCambioDolar)
                cursor.execute("""
                    INSERT INTO detalle_atencion (id_atencion, descripcion, costo)
                    VALUES (?, ?, ?)
                """, (id_atencion, f"Medicamento: {med.nombre}", costo_clp))
                
            conexion.commit()
            return id_atencion
        except sqlite3.Error as e:
            if "conexion" in locals() and conexion:
                conexion.rollback()
            print(f"Error SQLite al insertar atención (Transacción cancelada): {e}")
            return None
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()

    @staticmethod
    def obtener_atencion_con_detalles(id_atencion):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_atencion, fecha_hora, diagnostico, total, rut_cliente, microchip_mascota
                FROM atencion WHERE id_atencion = ?
            """, (id_atencion,))
            
            cabecera = cursor.fetchone()
            if not cabecera:
                return None
                
            cursor.execute("""
                SELECT id_detalle, descripcion, costo
                FROM detalle_atencion WHERE id_atencion = ?
            """, (id_atencion,))
            
            detalles = cursor.fetchall()
            
            return {
                "cabecera": cabecera,
                "detalles": detalles
            }
        except sqlite3.Error as e:
            print(f"Error SQLite al obtener atención: {e}")
            return None
        finally:
            if "conexion" in locals() and conexion:
                conexion.close()
``

## Archivo: dao\cliente_dao.py

``python
import sqlite3
from dao.database import conectar
from model.cliente import Cliente

class ClienteDAO:
    @staticmethod
    def insertar(cliente):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO cliente (id_cliente, rut, nombre, correo, telefono, dias_deuda)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cliente.idCliente, cliente.rut, cliente.nombre, cliente.correo, cliente.telefono, cliente.diasDeuda))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error SQLite al insertar cliente: {e}")
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

``

## Archivo: dao\database.py

``python
import sqlite3

def conectar():
    return sqlite3.connect("las_huellitas.db")

def crear_tablas():
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                id_cliente INTEGER PRIMARY KEY,
                rut TEXT NOT NULL,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL,
                telefono TEXT,
                dias_deuda INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mascota (
                numero_microchip TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                fecha_ultima_vacuna TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atencion (
                id_atencion INTEGER PRIMARY KEY,
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
                id_atencion INTEGER,
                descripcion TEXT,
                costo REAL
            )
        """)
        conexion.commit()
    except sqlite3.Error as e:
        print(f"Error al crear tablas: {e}")
    finally:
        if "conexion" in locals() and conexion:
            conexion.close()

``

## Archivo: dao\mascota_dao.py

``python
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

``

## Archivo: dao\__init__.py

``python

``

## Archivo: model\animal_exotico.py

``python
from model.mascota import Mascota

class AnimalExotico(Mascota):
    def obtenerDuracion(self) -> str:
        return "30 min"

    def obtenerTarifa(self) -> int:
        return 40000
``

## Archivo: model\asistente.py

``python
from model.empleado import Empleado

class Asistente(Empleado):
    def obtenerRol(self) -> str:
        return "Asistente"
        
    def agendarHora(self, cliente, fechaHora):
        print(f"Hora agendada para el cliente {cliente.nombre} en {fechaHora}")
        
    def registrarPago(self, cliente, monto: float):
        print(f"Pago de ${monto} registrado para el cliente {cliente.nombre}")
``

## Archivo: model\atencion.py

``python
from model.procedimiento import Procedimiento
from model.medicamento_importado import MedicamentoImportado
from model.excepciones import MascotaNoAptaCirugiaError, ClienteMorosoError
from datetime import datetime

class Atencion:
    def __init__(self, idAtencion: int, fechaHora: datetime, tipoCambioDolar: float, veterinario, mascota, cliente):
        self.idAtencion = idAtencion
        self.fechaHora = fechaHora
        self.diagnostico = ""
        self.tipoCambioDolar = float(tipoCambioDolar)
        self.veterinario = veterinario
        self.mascota = mascota
        self.cliente = cliente
        self.procedimientos = []
        self.medicamentos = []

    def agregarProcedimiento(self, idProcedimiento: int, nombre: str, esCirugia: bool, costo: float):
        if esCirugia and not self.mascota.estaAptaParaCirugia():
            raise MascotaNoAptaCirugiaError("La mascota no está apta para cirugía.")
        procedimiento = Procedimiento(idProcedimiento, nombre, esCirugia, float(costo))
        self.procedimientos.append(procedimiento)

    def agregarMedicamento(self, idMedicamento: int, nombre: str, precioUSD: float, margenGanancia: float):
        medicamento = MedicamentoImportado(idMedicamento, nombre, float(precioUSD), float(margenGanancia))
        self.medicamentos.append(medicamento)

    def procesarAtencion(self) -> float:
        if self.cliente.estaMoroso():
            raise ClienteMorosoError(f"El cliente {self.cliente.nombre} presenta morosidad.")
        
        print("=== DESGLOSE DE LA ATENCIÓN ===")
        print(f"ID Atención: {self.idAtencion} | Fecha: {self.fechaHora}")
        print(f"Veterinario: {self.veterinario.nombre} | Cliente: {self.cliente.nombre}")
        print(f"Mascota Microchip: {self.mascota.numeroMicrochip}")
        print(f"Diagnóstico: {self.diagnostico}")
        
        total = float(self.mascota.obtenerTarifa())
        print(f"Tarifa base por consulta: ${total}")
        
        if self.procedimientos:
            print("Procedimientos:")
            for proc in self.procedimientos:
                print(f" - {proc.nombre} (Cirugía: {'Sí' if proc.esCirugia else 'No'}): ${proc.costo}")
                total += proc.costo
                
        if self.medicamentos:
            print("Medicamentos prescritos (Cálculo Dinámico con API):")
            for med in self.medicamentos:
                precio_clp = med.calcularPrecioCLP(self.tipoCambioDolar)
                print(f" - {med.nombre}:")
                print(f"   * Precio Original USD: ${med.precioUSD}")
                print(f"   * Valor Dólar API: ${self.tipoCambioDolar}")
                print(f"   * PRECIO FINAL CLP (+{med.margenGanancia*100}% margen): ${precio_clp:.2f}")
                total += precio_clp
                
        print(f"TOTAL A PAGAR: ${total:.2f}")
        print("===============================\n")
        return total
``

## Archivo: model\cliente.py

``python
from model.persona import Persona

class Cliente(Persona):
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str, idCliente: int, diasDeuda: int):
        self._diasDeuda = 0
        self._idCliente = 0
        super().__init__(rut, nombre, correo, telefono)
        self.idCliente = idCliente
        self.diasDeuda = diasDeuda

    def obtenerRol(self) -> str: return "Cliente"

    @property
    def idCliente(self): return self._idCliente
    @idCliente.setter
    def idCliente(self, valor):
        if not isinstance(valor, int) or valor <= 0: raise TypeError("idCliente debe ser entero positivo.")
        self._idCliente = valor

    @property
    def diasDeuda(self) -> int: return self._diasDeuda
    @diasDeuda.setter
    def diasDeuda(self, valor: int):
        v = int(valor)
        if v < 0: raise ValueError("Los días de deuda no pueden ser negativos.")
        self._diasDeuda = v

    def estaMoroso(self) -> bool: return self._diasDeuda > 30
``

## Archivo: model\empleado.py

``python
from model.persona import Persona
from abc import ABC

class Empleado(Persona, ABC):
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str, idEmpleado: int, usuario: str, contrasena: str):
        super().__init__(rut, nombre, correo, telefono)
        self.idEmpleado = idEmpleado
        self.usuario = usuario
        self.contrasena = contrasena
``

## Archivo: model\excepciones.py

``python
class ClienteMorosoError(Exception):
    pass

class MascotaNoAptaCirugiaError(Exception):
    pass
``

## Archivo: model\gato.py

``python
from model.mascota import Mascota

class Gato(Mascota):
    def obtenerDuracion(self) -> str:
        return "15 min"

    def obtenerTarifa(self) -> int:
        return 20000
``

## Archivo: model\mascota.py

``python
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class Mascota(ABC):
    def __init__(self, numeroMicrochip: str, fechaUltimaVacuna: datetime):
        self.numeroMicrochip = numeroMicrochip
        self.fechaUltimaVacuna = fechaUltimaVacuna

    @property
    def numeroMicrochip(self) -> str:
        return self._numeroMicrochip

    @numeroMicrochip.setter
    def numeroMicrochip(self, valor: str):
        valor_str = str(valor)
        if len(valor_str) != 15 or not valor_str.isdigit():
            raise ValueError("El número de microchip debe tener exactamente 15 dígitos numéricos.")
        self._numeroMicrochip = valor_str

    @abstractmethod
    def obtenerDuracion(self) -> str:
        pass

    @abstractmethod
    def obtenerTarifa(self) -> int:
        pass

    def estaAptaParaCirugia(self) -> bool:
        limite = datetime.now() - timedelta(days=365)
        return self.fechaUltimaVacuna >= limite
``

## Archivo: model\medicamento_importado.py

``python
class MedicamentoImportado:
    def __init__(self, idMedicamento: int, nombre: str, precioUSD: float, margenGanancia: float):
        self.idMedicamento = idMedicamento
        self.nombre = nombre
        self.precioUSD = precioUSD
        self.margenGanancia = margenGanancia

    @property
    def idMedicamento(self): return self._idMedicamento
    @idMedicamento.setter
    def idMedicamento(self, valor):
        if not isinstance(valor, int) or valor <= 0: raise TypeError("idMedicamento debe ser entero positivo.")
        self._idMedicamento = valor

    @property
    def precioUSD(self): return self._precioUSD
    @precioUSD.setter
    def precioUSD(self, valor):
        v = float(valor)
        if v < 0: raise ValueError("El precio USD no puede ser negativo.")
        self._precioUSD = v

    @property
    def margenGanancia(self): return self._margenGanancia
    @margenGanancia.setter
    def margenGanancia(self, valor):
        v = float(valor)
        if v < 0: raise ValueError("El margen no puede ser negativo.")
        self._margenGanancia = v

    def calcularPrecioCLP(self, tipoCambioDolar: float) -> float:
        return self.precioUSD * tipoCambioDolar * (1 + self.margenGanancia)
``

## Archivo: model\perro.py

``python
from model.mascota import Mascota

class Perro(Mascota):
    def obtenerDuracion(self) -> str:
        return "20 min"

    def obtenerTarifa(self) -> int:
        return 25000
``

## Archivo: model\persona.py

``python
from abc import ABC, abstractmethod
import re

class Persona(ABC):
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str):
        self._rut = None
        self._correo = None
        self._telefono = None
        
        self.rut = rut
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def rut(self) -> str: return self._rut
    @rut.setter
    def rut(self, valor: str):
        if not re.match(r"^\d{7,8}-[\dkK]$", str(valor)):
            raise ValueError(f"Formato de RUT inválido: {valor}")
        self._rut = valor

    @property
    def correo(self) -> str: return self._correo
    @correo.setter
    def correo(self, valor: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", str(valor)):
            raise ValueError(f"Formato de correo inválido: {valor}")
        self._correo = valor

    @property
    def telefono(self) -> str: return self._telefono
    @telefono.setter
    def telefono(self, valor: str):
        if not str(valor).isdigit() or len(str(valor)) < 8:
            raise ValueError("Formato de teléfono inválido (debe tener al menos 8 dígitos).")
        self._telefono = valor
        
    @abstractmethod
    def obtenerRol(self) -> str: pass
``

## Archivo: model\procedimiento.py

``python
class Procedimiento:
    def __init__(self, idProcedimiento: int, nombre: str, esCirugia: bool, costo: float):
        self.idProcedimiento = idProcedimiento
        self.nombre = nombre
        self.esCirugia = esCirugia
        self.costo = costo

    @property
    def idProcedimiento(self): return self._idProcedimiento
    @idProcedimiento.setter
    def idProcedimiento(self, valor):
        if not isinstance(valor, int) or valor <= 0: raise TypeError("idProcedimiento debe ser entero positivo.")
        self._idProcedimiento = valor

    @property
    def costo(self): return self._costo
    @costo.setter
    def costo(self, valor):
        v = float(valor)
        if v < 0: raise ValueError("El costo no puede ser negativo.")
        self._costo = v
``

## Archivo: model\veterinario.py

``python
from model.empleado import Empleado

class Veterinario(Empleado):
    def obtenerRol(self) -> str:
        return "Veterinario"
        
    def registrarDiagnostico(self, atencion, diagnostico: str):
        atencion.diagnostico = diagnostico
        
    def prescribirMedicamento(self, atencion, idMedicamento: int, nombre: str, precioUSD: float, margenGanancia: float):
        atencion.agregarMedicamento(idMedicamento, nombre, precioUSD, margenGanancia)
``

## Archivo: model\__init__.py

``python
``

## Archivo: service\indicador_api.py

``python
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

def obtener_valor_dolar() -> float:
    url = "https://mindicador.cl/api/dolar"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data["serie"][0]["valor"])
    except Timeout:
        print("?? Timeout API D�lar. Usando referencial 900.0")
        return 900.0
    except ConnectionError:
        print("?? ConnectionError API D�lar. Usando referencial 900.0")
        return 900.0
    except (ValueError, KeyError, RequestException) as e:
        print(f"?? Error API D�lar ({e}). Usando referencial 900.0")
        return 900.0

``

## Archivo: service\__init__.py

``python

``

