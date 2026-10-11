# Clínica Veterinaria Las Huellitas — Evaluación Sumativa N°3

## 1. Integrantes y negocio

**Negocio asignado:** Clínica Veterinaria Las Huellitas

| N° | Apellido Paterno | Apellido Materno | Nombres |
|----|-----------------|-----------------|---------|
| 1 | Montenegro | Soto | Marcos Esteban |
| 2 | Marín | — | Matias Sebastian |

**Sección:** 114-2B-F1 · **Módulo:** Programación Orientada a Objeto Seguro (TI3V21)

---

## 2. Cómo instalar y ejecutar el programa

**Requisito:** Python 3.10 o posterior. SQLite viene incluido con Python; no se necesita instalar nada adicional para la base de datos.

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/MarcosMontenegroProgram/LasHuellitas-POO.git
cd LasHuellitas-POO
```

### Paso 2 — Crear y activar un entorno virtual (recomendado)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4 — Ejecutar el programa

```bash
python main.py
```

Al iniciarse, el programa crea automáticamente el archivo `las_huellitas.db` en la carpeta del proyecto si no existe. Las tablas se crean solas; **no hay que configurar nada manualmente**. Si existe una base de datos anterior sin la columna `nombre` en `mascota`, la migración la agrega sin borrar datos.

Para salir del programa ingrese `0` en el menú.

### Paso 5 — Ejecutar las pruebas de aceptación (opcional)

```bash
python tests/run_acceptance.py
```

El guion cubre los casos P01–P19 de la guía de pruebas usando bases de datos temporales y no modifica la base de datos real del usuario.

---

## 3. Decisiones de seguridad

### Prevención de inyección SQL

Todas las consultas que reciben datos del usuario usan parámetros posicionales `?` de la API de `sqlite3`. Ninguna consulta se construye concatenando texto ingresado por el usuario.

**Ejemplo en `dao/mascota_dao.py`:**
```python
conexion.execute(
    "SELECT numero_microchip, tipo, fecha_ultima_vacuna, nombre "
    "FROM mascota WHERE numero_microchip = ?",
    (numero_microchip,)
)
```

### Entradas que se validan

| Dato | Dónde se valida | Regla |
|------|----------------|-------|
| Número de microchip | Setter `Mascota.numeroMicrochip` | Exactamente 15 dígitos numéricos ASCII |
| Nombre de mascota | Setter `Mascota.nombre` | No puede estar vacío ni ser solo espacios |
| RUT | Setter `Persona.rut` | Formato `NNNNNNN-D` (7 u 8 dígitos + dígito verificador) |
| Correo | Setter `Persona.correo` | Debe contener `@` y dominio |
| Teléfono | Setter `Persona.telefono` | Solo dígitos, mínimo 8 caracteres |
| Días de deuda | Setter `Cliente.diasDeuda` | Entero no negativo |
| Costos y precios | `pedir_numero()` en `main.py` y setters | Número finito no negativo; letras son rechazadas |

### Atomicidad de transacciones

La cabecera de una atención y todas sus líneas de detalle (procedimientos y medicamentos) se insertan dentro de una misma transacción (`BEGIN` / `COMMIT`). Si falla cualquier inserción de detalle, se ejecuta `rollback()` y la base de datos no queda con registros huérfanos.

### Reglas de negocio como segunda capa de seguridad

- El `AtencionDAO.insertar()` revalida morosidad y aptitud para cirugía **antes de abrir la transacción**, de modo que el rechazo ocurre aunque se llame al DAO directamente sin pasar por el menú.

---

## 4. Uso de inteligencia artificial

Durante el desarrollo se usó **Claude (Anthropic)** como apoyo para revisar, depurar y mejorar partes del código.

### Ejemplo concreto: guardado transaccional en `dao/atencion_dao.py`

La IA sugirió usar `cursor.executemany()` para insertar todas las líneas de detalle en una sola llamada dentro de la transacción, en lugar de un `for` con `cursor.execute()` repetido.

**Código sugerido por la IA (simplificado):**
```python
cursor.executemany(
    "INSERT INTO detalle_atencion (id_atencion, descripcion, costo) VALUES (?, ?, ?)",
    [(id_atencion, desc, costo) for desc, costo in lineas]
)
```

**Decisión adoptada:** se adoptó porque reduce el número de llamadas a SQLite y mantiene la atomicidad de forma más limpia. Se mantuvo el bloque `try / except / rollback` que ya teníamos para garantizar que, si falla cualquier inserción, se cancela toda la transacción.

**Lo que se descartó:** la IA también propuso usar `requests` para consumir la API del dólar. Se descartó porque `urllib` (librería estándar de Python) cumple el mismo propósito sin agregar dependencias externas, lo que simplifica la instalación en un computador nuevo.

**Lo que se modificó:** la función de la API fue ajustada para devolver una tupla `(valor, es_respaldo)` en vez de solo el valor, de modo que el programa puede indicar explícitamente al usuario si el tipo de cambio mostrado proviene de mindicador.cl o es un valor de respaldo por falta de conexión.
