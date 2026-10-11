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
                m_real = MascotaDAO.obtener_por_microchip(mc)
                if m_real:
                    m_real.fechaUltimaVacuna = fecha
                    MascotaDAO.actualizar(m_real)
                    print("Mascota actualizada exitosamente manteniendo su especie.")
                else:
                    print("Error: No se encontró una mascota con ese microchip.")
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
                c = Cliente(rut, nombre, correo, tel, None, deuda)
                if ClienteDAO.insertar(c):
                    print(f"Cliente guardado con ID {c.idCliente}.")
                else:
                    print("No se pudo guardar el cliente. Verifique que el RUT no esté registrado.")
            except (ValueError, TypeError) as e:
                print(f"Error de validación: {e}")
                
        elif opc == '6':
            print("\n--- Agendar Atención ---")
            rut = input("RUT del Cliente: ")
            mc = pedir_microchip()
            
            # Buscar al cliente y mascota REALES en la BD
            c = ClienteDAO.obtener_por_rut(rut)
            if not c:
                print("Error: Cliente no encontrado en la base de datos.")
                continue
                
            m = MascotaDAO.obtener_por_microchip(mc)
            if not m:
                print("Error: Mascota no encontrada en la base de datos.")
                continue
            
            try:
                # Usamos id 0, la base de datos asignará el verdadero ID
                atencion = Atencion(0, datetime.now(), dolar_actual, veterinario, m, c)
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
