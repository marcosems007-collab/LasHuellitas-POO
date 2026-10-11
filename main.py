from datetime import datetime
import math

from dao.atencion_dao import AtencionDAO
from dao.cliente_dao import ClienteDAO
from dao.database import crear_tablas
from dao.mascota_dao import MascotaDAO
from model.animal_exotico import AnimalExotico
from model.atencion import Atencion
from model.cliente import Cliente
from model.excepciones import ClienteMorosoError, MascotaNoAptaCirugiaError
from model.gato import Gato
from model.perro import Perro
from model.veterinario import Veterinario
from service.indicador_api import obtener_valor_dolar_info


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
    return input("Ingrese una opción: ").strip()


def pedir_microchip():
    while True:
        mc = input("Ingrese número de microchip (15 dígitos): ").strip()
        try:
            # El propio setter del modelo es la validación definitiva.
            Perro(mc, datetime.now(), "Validación")
            return mc
        except ValueError as e:
            print(f"Error: {e}")


def pedir_numero(prompt, conversion=float, minimo=0):
    while True:
        try:
            valor = conversion(input(prompt).strip())
            if isinstance(valor, float) and not math.isfinite(valor):
                raise ValueError("El número debe ser finito.")
            if valor < minimo:
                raise ValueError(f"El valor debe ser igual o superior a {minimo}.")
            return valor
        except ValueError as e:
            print(f"Número inválido: {e}. Intente nuevamente.")


def _tipo_mascota(tipo, microchip, fecha, nombre):
    clases = {"perro": Perro, "gato": Gato, "ave": AnimalExotico, "exotico": AnimalExotico, "animal exotico": AnimalExotico}
    clase = clases.get(tipo.strip().lower())
    if not clase:
        raise ValueError("Tipo no válido. Use Perro, Gato o Ave/Exótico.")
    return clase(microchip, fecha, nombre)


def crear_mascota():
    print("\n--- Crear Mascota ---")
    mc = pedir_microchip()
    nombre = input("Nombre de la mascota: ").strip()
    tipo = input("Tipo (Perro/Gato/Ave o Exotico): ")
    fecha_str = input("Fecha última vacuna (YYYY-MM-DD): ").strip()
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        masc = _tipo_mascota(tipo, mc, fecha, nombre)
        print(f"Consulta {masc.obtenerDuracion()} | Tarifa: ${masc.obtenerTarifa():,}")
        if MascotaDAO.insertar(masc):
            print("Mascota guardada correctamente.")
        else:
            print("No se pudo guardar la mascota. Verifique si el microchip ya existe.")
    except ValueError as e:
        print(f"Error: {e}")


def modificar_mascota():
    print("\n--- Modificar Mascota ---")
    mc = pedir_microchip()
    mascota = MascotaDAO.obtener_por_microchip(mc)
    if not mascota:
        print("Error: No se encontró una mascota con ese microchip.")
        return
    nombre = input(f"Nuevo nombre [{mascota.nombre}]: ").strip() or mascota.nombre
    fecha_str = input(f"Nueva fecha última vacuna YYYY-MM-DD [{mascota.fechaUltimaVacuna:%Y-%m-%d}]: ").strip()
    try:
        mascota.nombre = nombre
        if fecha_str:
            mascota.fechaUltimaVacuna = datetime.strptime(fecha_str, "%Y-%m-%d")
        if MascotaDAO.actualizar(mascota):
            print("Mascota actualizada exitosamente.")
        else:
            print("No se pudo actualizar la mascota.")
    except ValueError as e:
        print(f"Error: {e}")


def crear_cliente():
    print("\n--- Crear Cliente ---")
    rut = input("RUT: ").strip()
    nombre = input("Nombre: ").strip()
    correo = input("Correo: ").strip()
    tel = input("Teléfono: ").strip()
    deuda = pedir_numero("Días de deuda (0 si no tiene): ", int, 0)
    try:
        c = Cliente(rut, nombre, correo, tel, None, deuda)
        if ClienteDAO.insertar(c):
            print(f"Cliente guardado con ID {c.idCliente}.")
        else:
            print("No se pudo guardar el cliente. Verifique que el RUT no esté registrado.")
    except (ValueError, TypeError) as e:
        print(f"Error de validación: {e}")


def agendar_atencion(veterinario, dolar, dolar_respaldo):
    print("\n--- Agendar Atención ---")
    rut = input("RUT del Cliente: ").strip()
    mc = pedir_microchip()
    c = ClienteDAO.obtener_por_rut(rut)
    if not c:
        print("Error: Cliente no encontrado en la base de datos.")
        return
    m = MascotaDAO.obtener_por_microchip(mc)
    if not m:
        print("Error: Mascota no encontrada en la base de datos.")
        return
    if c.estaMoroso():
        print(f"Atención rechazada: el cliente {c.nombre} tiene una deuda impaga de más de 30 días.")
        return

    atencion = Atencion(0, datetime.now(), dolar, veterinario, m, c, dolar_respaldo)
    atencion.diagnostico = input("Ingrese diagnóstico: ").strip()
    print(f"Mascota: {m.nombre} ({m.__class__.__name__}) | Consulta: {m.obtenerDuracion()} | Tarifa: ${m.obtenerTarifa():,}")
    print("Agregar procedimientos (por ejemplo, Vacuna y Desparasitación):")
    while True:
        proc_nom = input("Nombre procedimiento (o 'fin' para terminar): ").strip()
        if proc_nom.lower() == "fin":
            break
        es_cirugia = input("¿Es cirugía? (s/n): ").strip().lower() == "s"
        costo = pedir_numero("Costo: ", float, 0)
        try:
            atencion.agregarProcedimiento(1, proc_nom, es_cirugia, costo)
            print(f"Procedimiento agregado: {proc_nom}.")
        except MascotaNoAptaCirugiaError as e:
            print(f"Cirugía rechazada: {e} No se agregó a la atención.")
        except (ValueError, TypeError) as e:
            print(f"No se agregó el procedimiento: {e}")

    print("Agregar medicamentos (opcional):")
    while True:
        med_nom = input("Nombre medicamento (o 'fin' para terminar): ").strip()
        if med_nom.lower() == "fin":
            break
        usd = pedir_numero("Precio en USD: ", float, 0)
        try:
            atencion.agregarMedicamento(1, med_nom, usd, 0.20)
        except (ValueError, TypeError) as e:
            print(f"No se agregó el medicamento: {e}")
    try:
        atencion.total = atencion.procesarAtencion()
        id_at = AtencionDAO.insertar(atencion)
        if id_at:
            print(f"Atención guardada correctamente con ID {id_at}.")
        else:
            print("No se pudo guardar la atención.")
    except ClienteMorosoError as e:
        print(f"Atención rechazada: {e}")
    except MascotaNoAptaCirugiaError as e:
        print(f"Cirugía rechazada: {e}")


def main():
    crear_tablas()
    dolar_actual, dolar_respaldo = obtener_valor_dolar_info()
    veterinario = Veterinario("11223344-5", "Dr. Juan Pérez", "juan@huellitas.cl", "987654321", 101, "jperez", "pass")
    while True:
        try:
            opc = mostrar_menu()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo del sistema...")
            break
        try:
            if opc == "0":
                print("Saliendo del sistema...")
                break
            elif opc == "1":
                crear_mascota()
            elif opc == "2":
                print("\n--- Listar Mascotas ---")
                mascotas = MascotaDAO.obtener_todos()
                if not mascotas:
                    print("No hay mascotas registradas.")
                for m in mascotas:
                    print(f"Nombre: {m.nombre}, Microchip: {m.numeroMicrochip}, Tipo: {m.__class__.__name__}, Última Vacuna: {m.fechaUltimaVacuna:%Y-%m-%d}")
            elif opc == "3":
                modificar_mascota()
            elif opc == "4":
                mc = pedir_microchip()
                print("Mascota eliminada." if MascotaDAO.eliminar(mc) else "No se encontró esa mascota.")
            elif opc == "5":
                crear_cliente()
            elif opc == "6":
                agendar_atencion(veterinario, dolar_actual, dolar_respaldo)
            elif opc == "7":
                id_at = pedir_numero("Ingrese ID de la Atención: ", int, 1)
                data = AtencionDAO.obtener_atencion_con_detalles(id_at)
                if data:
                    print(f"Atención: {data['cabecera']}")
                    print("Detalles:")
                    if not data["detalles"]:
                        print(" - Sin líneas de detalle")
                    for d in data["detalles"]:
                        print(f" - {d[1]}: ${d[2]:,.2f}")
                else:
                    print("No se encontró la atención.")
            elif opc == "99":
                print("Opción de prueba detectada. Retornando al menú...")
            else:
                print("Opción no válida. Intente de nuevo.")
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrumpida. Saliendo del sistema...")
            break


if __name__ == "__main__":
    main()
