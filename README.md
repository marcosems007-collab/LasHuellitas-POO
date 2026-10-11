# Clínica Veterinaria Las Huellitas (POO) — Evaluación Sumativa N°3

## 1. Integrantes y negocio

**Negocio asignado:** Clínica Veterinaria Huellitas · **Integrante 1:** Marcos Montenegro Soto · **Integrante 2:** Matias Sebastian Marin

**Fechas del proyecto:** inicio, martes 6 de octubre de 2026; entrega, martes 13 de octubre de 2026.

### ¿Para qué sirve este proyecto?

Es un sistema de gestión para la Clínica Veterinaria Huellitas, desarrollado con programación orientada a objetos. Permite registrar clientes y sus días de deuda, mantener los datos de mascotas (nombre, tipo, microchip y fecha de última vacuna) y registrar consultas, procedimientos y medicamentos. Los datos se guardan en SQLite para que sigan disponibles cuando se cierra y vuelve a abrir el programa. El precio de medicamentos importados se calcula en pesos chilenos con el dólar de mindicador.cl.

### Alcance funcional

| Tipo de mascota | Duración de consulta | Tarifa definida en el proyecto |
| --- | ---: | ---: |
| Perro | 20 minutos | $25.000 CLP |
| Gato | 15 minutos | $20.000 CLP |
| Ave o animal exótico | 30 minutos | $40.000 CLP |

La cirugía requiere que la última vacuna esté dentro de los 365 días anteriores. El sistema rechaza una atención si el cliente tiene una deuda impaga de más de 30 días. Una consulta puede guardar varias líneas de procedimiento y medicamento en una sola atención.

Hay dos datos pendientes de confirmar por el equipo: la rúbrica indica la sección **114-2B-F1** y la guía de pruebas indica **114-2A-F2**. El README previo lista a Marcos Montenegro Soto y Matias Sebastian Marin, mientras la guía menciona a Sergio Marguirott Hernández. Se conservaron los integrantes existentes en el README; el equipo debe confirmar la sección y la nómina definitiva.

## 2. Instalación, ejecución y uso paso a paso

Se requiere Python **3.10 o posterior**. SQLite viene incluido con Python. Se necesita Internet para obtener el tipo de cambio actual; si no está disponible, el programa informa que usará el valor de respaldo de $900 CLP por dólar.

1. Instale Python desde [python.org](https://www.python.org/downloads/) y habilite Python en PATH.
2. Abra una terminal y clone el repositorio:

   ```bash
   git clone https://github.com/MarcosMontenegroProgram/LasHuellitas-POO.git
   cd LasHuellitas-POO
   ```

3. Cree y active un entorno virtual (recomendado):

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS o Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Instale las dependencias indicadas por el proyecto:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Ejecute la aplicación:

   ```bash
   python main.py
   ```

Al iniciar, el programa crea `las_huellitas.db` junto a `main.py` si aún no existe; así, la ubicación de los datos no cambia aunque se ejecute desde otra carpeta o terminal. También puede definir `HUELLITAS_DB_PATH` para elegir otra ruta de base de datos. Si encuentra una base anterior sin el campo de nombre de mascota, añade el campo con el valor inicial `Mascota` y conserva los registros existentes. Para salir de la aplicación, ingrese `0` en el menú.

### ¿Cómo se usa el programa?

1. **Crear mascotas:** elija `1` e ingrese microchip de 15 dígitos, nombre, tipo y fecha de última vacuna con el formato `AAAA-MM-DD`. El programa guarda el registro y muestra la duración y tarifa de consulta.
2. **Consultar y mantener mascotas:** `2` lista los registros; `3` permite cambiar nombre y fecha de vacuna buscando por microchip; `4` elimina el registro seleccionado por microchip.
3. **Registrar clientes:** elija `5` e ingrese RUT, nombre, correo, teléfono y días de deuda. SQLite asigna el ID automáticamente.
4. **Agendar una atención:** elija `6`, indique el RUT del cliente y el microchip de su mascota, y escriba el diagnóstico. Agregue procedimientos uno por uno; para cada procedimiento indique si es cirugía y su costo. Escriba `fin` para terminar esa lista. Luego puede agregar medicamentos indicando su precio en USD; escriba `fin` para cerrar la lista y guardar la atención.
5. **Revisar una atención:** elija `7` e ingrese su ID para ver la cabecera y todas las líneas de detalle guardadas.

En una atención, si una cirugía no cumple la regla de vacunas, se informa el motivo y esa cirugía no se agrega. Si el cliente tiene más de 30 días de deuda, la atención se rechaza antes de guardarse. El medicamento importado se convierte a CLP con un margen del 20% aplicado por el flujo de la aplicación.

Para repetir la verificación automatizada de los casos P01–P19:

```bash
python tests/run_acceptance.py
```

El guion usa bases SQLite temporales, verifica los flujos del menú y no lee ni modifica la base de datos normal del usuario.

### ¿Cómo está organizado el código?

- **`main.py`:** presenta el menú, solicita datos y conecta la interfaz con las reglas de negocio y la persistencia.
- **`model/`:** contiene las clases del dominio. `Mascota` valida el microchip; `Perro`, `Gato` y `AnimalExotico` implementan sus propias tarifas y duraciones. `Atencion` calcula el total y aplica reglas de negocio.
- **`dao/`:** contiene el acceso a SQLite. `database.py` crea y migra el esquema; los DAO de clientes y mascotas implementan las operaciones de persistencia. `AtencionDAO` guarda una atención y sus detalles en una sola transacción.
- **`service/indicador_api.py`:** consulta `https://mindicador.cl/api/dolar` usando `urllib` de la biblioteca estándar y un timeout de cinco segundos. Si hay un error, demora excesiva o respuesta inválida, comunica el uso del respaldo y no lo presenta como valor actual.

El flujo de ejecución es: `main.py` presenta el menú → el usuario ingresa datos → los modelos validan y aplican las reglas → los DAO leen o escriben en SQLite → la interfaz confirma el resultado o explica el error y vuelve al menú.

## 3. Decisiones de seguridad

- **Prevención de inyección SQL:** las consultas SQLite que reciben datos usan parámetros `?`; los datos de usuario no se concatenan en las sentencias SQL.
- **Validación de entradas:** el setter de `Mascota.numeroMicrochip` acepta exactamente 15 dígitos numéricos ASCII. La interfaz maneja entradas no numéricas y permite volver a ingresarlas sin cerrar el programa. Los precios y costos deben ser finitos y no negativos.
- **Reglas de negocio:** la aptitud para cirugía se valida contra la fecha de última vacuna y se comprueba de nuevo al guardar. La morosidad de más de 30 días impide registrar la atención antes de insertar su cabecera.
- **Atomicidad:** la cabecera y las líneas de detalle de una atención se guardan dentro de la misma transacción. Si falla una línea, se revierte la transacción completa.
- **Persistencia segura:** la migración de `nombre` agrega una columna con valor predeterminado y no borra la base ni sus datos previos.
- **Servicio externo:** la petición de dólar tiene timeout y valida que la respuesta contenga un valor numérico válido. Ante una falla, el usuario recibe un mensaje explícito sobre el respaldo.

## 4. Uso de Inteligencia Artificial (IA)

Durante el desarrollo se usó Google Gemini como apoyo para revisar y modificar partes del código. Un ejemplo adoptado y ajustado fue el guardado transaccional de `Atencion` y sus detalles en `dao/atencion_dao.py`: se prepara la lista de líneas y se inserta junto con la cabecera dentro de una transacción. Se mantuvo el `rollback` cuando falla una inserción. La razón técnica es evitar que la base de datos conserve una atención incompleta sin sus detalles. También se usó IA como apoyo para implementar las validaciones encapsuladas del microchip y reconstruir desde SQLite el tipo concreto de mascota.

