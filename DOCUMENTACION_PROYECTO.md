# Documentación Técnica y Funcional: Clínica Veterinaria Las Huellitas (POO)

## 📅 Fechas del Proyecto
* **Fecha de Inicio (Evaluación 3):** Martes 6 de octubre de 2026
* **Fecha de Término (Entrega):** Martes 13 de octubre de 2026

## 🎯 ¿Para qué sirve este proyecto?
Este proyecto es un **Sistema de Gestión de Software Orientado a Objetos** diseñado para la Clínica Veterinaria "Las Huellitas". Su objetivo principal es automatizar y digitalizar la administración del negocio, permitiendo:
1. Registrar clientes y llevar un control de sus estados de morosidad.
2. Ingresar mascotas separadas por sus tipos específicos (Perros, Gatos, Exóticos), manejando información crítica como su fecha de última vacuna y su número de microchip.
3. Registrar atenciones médicas (consultas, cirugías y venta de medicamentos), calculando automáticamente las tarifas y convirtiendo valores de medicamentos extranjeros de USD a Pesos Chilenos (CLP) usando el valor real del dólar del día.

---

## ⚙️ Explicación Detallada: ¿Cómo funciona cada aspecto del código?

### 1. El Modelo de Datos (Paradigma Orientado a Objetos) - Carpeta `model/`
El corazón del sistema es la POO. Todo es un objeto.
* **Herencia y Polimorfismo (`mascota.py`, `perro.py`, `gato.py`, `animal_exotico.py`):** Existe una clase "Padre" o abstracta llamada `Mascota`. De ella heredan `Perro`, `Gato` y `AnimalExotico`. Cada una sobrescribe (polimorfismo) los métodos `obtenerTarifa()` y `obtenerDuracion()` para que cobren valores distintos y tomen tiempos distintos según el tipo de animal.
* **Encapsulamiento y Validaciones (Setters):** Las clases como `Mascota` o `Persona` no permiten guardar cualquier dato. Mediante decoradores como `@property` y `@rut.setter` o `@numeroMicrochip.setter`, el código intercepta la información antes de guardarla. Por ejemplo, si intentas guardar un microchip de 14 dígitos, el *setter* levanta un `ValueError` bloqueando la acción por seguridad.
* **Reglas de Negocio (`atencion.py` y `excepciones.py`):** El sistema crea sus propios errores lógicos. Si un cliente debe dinero por más de 30 días, lanza un `ClienteMorosoError`. Si agendamos cirugía a una mascota con vacunas vencidas (más de 1 año), lanza `MascotaNoAptaCirugiaError`.

### 2. Capa de Persistencia (Base de Datos SQLite) - Carpeta `dao/`
El sistema no borra sus datos al cerrarse, los guarda permanentemente usando el patrón DAO (Data Access Object).
* **`database.py`:** Se encarga de conectarse a un archivo local llamado `las_huellitas.db`. Si las tablas no existen, las crea automáticamente (`CREATE TABLE IF NOT EXISTS`).
* **Operaciones CRUD:** Clases como `ClienteDAO` y `MascotaDAO` inyectan los objetos del programa en la base de datos de manera segura usando consultas parametrizadas (con el símbolo `?`), lo cual previene ataques de Inyección SQL.
* **Transacciones (`atencion_dao.py`):** Para guardar una Atención médica, se utiliza el comando `BEGIN TRANSACTION`. Esto permite que se guarde la cabecera (la atención general) y luego múltiples detalles (los procedimientos y medicamentos). Si un medicamento falla en guardarse, la transacción completa se cancela (`rollback`), impidiendo que queden datos "a medias" o huérfanos.

### 3. Consumo de Servicios Externos (API) - Carpeta `service/`
* **`indicador_api.py`:** Utiliza la librería oficial `requests` para conectarse a la URL pública `https://mindicador.cl/api/dolar`. Obtiene el precio del dólar del día actual. Si el internet falla, o la página tarda más de 5 segundos en responder, el sistema atrapa el error (`Timeout` o `ConnectionError`) y utiliza un valor referencial (ej: 900.0) para evitar que el programa colapse.

### 4. La Interfaz de Usuario (El Controlador) - Archivo `main.py`
* Actúa como el puente entre el usuario y la lógica. Despliega un menú interactivo (`while True`) que permite al usuario probar todas las funcionalidades (P01 al P19 de la rúbrica). 
* Maneja los bloques `try...except`, de modo que si el modelo de datos arroja un error (como un RUT mal escrito o una deuda inválida), `main.py` atrapa ese error, se lo muestra amigablemente al usuario en pantalla y vuelve al menú principal sin que la aplicación se "caiga".
