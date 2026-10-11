"""Guion reproducible de aceptación para P01-P19 y reglas transaccionales."""
import contextlib
import gc
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import main
from dao.atencion_dao import AtencionDAO
from dao.cliente_dao import ClienteDAO
from dao.database import conectar, crear_tablas
from dao import database as database_module
from dao.mascota_dao import MascotaDAO
from model.atencion import Atencion
from model.cliente import Cliente
from model.excepciones import ClienteMorosoError, MascotaNoAptaCirugiaError
from model.perro import Perro
from model.veterinario import Veterinario
from service import indicador_api


passed = []
failed = []


def session(lines, rate=(1000.0, False)):
    output = io.StringIO()
    answers = iter(lines)
    def read_answer(_=""):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError
    with patch("builtins.input", side_effect=read_answer), \
         patch.object(main, "obtener_valor_dolar_info", return_value=rate), \
         contextlib.redirect_stdout(output):
        main.main()
    return output.getvalue()


def in_database(test, initialize=True):
    with tempfile.TemporaryDirectory(prefix="huellitas-", dir=ROOT) as temp:
        old = os.environ.get("HUELLITAS_DB_PATH")
        os.environ["HUELLITAS_DB_PATH"] = str(Path(temp) / "test.db")
        try:
            if initialize:
                crear_tablas()
            result = test()
            gc.collect()
            return result
        finally:
            if old is None:
                os.environ.pop("HUELLITAS_DB_PATH", None)
            else:
                os.environ["HUELLITAS_DB_PATH"] = old


def check(case, fn):
    try:
        fn()
        passed.append(case)
        print(f"PASS {case}")
    except Exception as exc:
        failed.append((case, repr(exc)))
        print(f"FAIL {case}: {exc}")


def check_output(case, inputs, expected):
    def run():
        out = session(inputs)
        assert expected in out, f"No se encontró {expected!r} en la salida"
    check(case, lambda: in_database(run))


def create_pet_inputs(chip, name="Firulais", kind="Perro", vaccine="2026-10-01"):
    return ["1", chip, name, kind, vaccine]


def customer_inputs(rut="12345678-9", debt="0"):
    return ["5", rut, "Cliente Prueba", "prueba@example.cl", "987654321", debt]


def test_p01():
    out = session(["0"])
    assert "CLÍNICA VETERINARIA HUELLITAS" in out and "Saliendo del sistema" in out


check("P01", lambda: in_database(test_p01))
check_output("P02", create_pet_inputs("985112003456789") + ["0"], "Mascota guardada correctamente")


def test_p03():
    out = session(create_pet_inputs("985112003456789") + ["2", "0"])
    assert "Nombre: Firulais" in out and "985112003456789" in out


check("P03", lambda: in_database(test_p03))


def test_p04():
    out = session(create_pet_inputs("985112003456789") + ["3", "985112003456789", "Firulais Jr.", "", "2", "0"])
    assert "Mascota actualizada exitosamente" in out and "Nombre: Firulais Jr." in out


check("P04", lambda: in_database(test_p04))


def test_p05():
    env = os.environ.copy()
    code = "import main; main.obtener_valor_dolar_info=lambda: (1000.0, False); main.main()"
    first = subprocess.run([sys.executable, "-c", code], input="\n".join(create_pet_inputs("985112003456789") + ["0"]) + "\n", cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    second = subprocess.run([sys.executable, "-c", code], input="2\n0\n", cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    assert "Mascota guardada correctamente" in first.stdout and "Nombre: Firulais" in second.stdout


check("P05", lambda: in_database(test_p05))


def test_p06():
    out = session(create_pet_inputs("985112003456789") + ["4", "985112003456789", "2", "0"])
    assert "Mascota eliminada" in out and "No hay mascotas registradas" in out


check("P06", lambda: in_database(test_p06))


def test_p07():
    pet = Perro("985112003456789", datetime.now(), "Firulais")
    assert pet.numeroMicrochip == "985112003456789"
    assert MascotaDAO.insertar(pet)


check("P07", lambda: in_database(test_p07))


def test_p08():
    out = session(["1", "98511200345"] + create_pet_inputs("985112003456789")[1:] + ["0"])
    assert "exactamente 15 dígitos" in out and "Mascota guardada correctamente" in out


check("P08", lambda: in_database(test_p08))


check_output("P09", create_pet_inputs("985112003456789") + ["0"], "Consulta 20 min | Tarifa: $25,000")
check_output("P10", create_pet_inputs("985112003456789", "Michi", "Gato") + ["0"], "Consulta 15 min | Tarifa: $20,000")
check_output("P11", create_pet_inputs("985112003456789", "Loro", "Ave") + ["0"], "Consulta 30 min | Tarifa: $40,000")


def setup_owner_and_pet(debt=0, vaccine="2026-10-01"):
    pet = Perro("985112003456789", datetime.strptime(vaccine, "%Y-%m-%d"), "Firulais")
    assert MascotaDAO.insertar(pet)
    owner = Cliente("12345678-9", "Cliente Prueba", "prueba@example.cl", "987654321", None, debt)
    assert ClienteDAO.insertar(owner)


def attention_inputs(*procedure_lines, medication_lines=("fin",)):
    values = ["6", "12345678-9", "985112003456789", "Control general"]
    values.extend(procedure_lines)
    values.extend(medication_lines)
    return values


def test_p12_p13():
    setup_owner_and_pet()
    out = session(attention_inputs("Vacuna", "n", "100", "Desparasitación", "n", "150", "fin") + ["7", "1", "0"])
    assert "Atención guardada correctamente con ID 1" in out
    assert "Procedimiento: Vacuna" in out and "Procedimiento: Desparasitación" in out
    assert len(AtencionDAO.obtener_atencion_con_detalles(1)["detalles"]) == 2


check("P12-P13", lambda: in_database(test_p12_p13))


def test_p14():
    setup_owner_and_pet(vaccine="2024-01-01")
    out = session(attention_inputs("Cirugía", "s", "500", "fin") + ["fin", "0"])
    details = AtencionDAO.obtener_atencion_con_detalles(1)["detalles"]
    assert "Cirugía rechazada" in out and all("Cirugía" not in row[1] for row in details)


check("P14", lambda: in_database(test_p14))


def test_p15():
    setup_owner_and_pet(debt=31)
    out = session(["6", "12345678-9", "985112003456789", "0"])
    connection = conectar()
    try:
        count = connection.execute("SELECT count(*) FROM atencion").fetchone()[0]
    finally:
        connection.close()
    assert "más de 30 días" in out and count == 0


check("P15", lambda: in_database(test_p15))


def test_p16():
    response = io.BytesIO(json.dumps({"serie": [{"valor": 987.65}]}).encode("utf-8"))
    with patch.object(indicador_api, "urlopen", return_value=response) as get:
        value, fallback = indicador_api.obtener_valor_dolar_info()
    assert value == 987.65 and not fallback
    get.assert_called_once_with(indicador_api.URL_DOLAR, timeout=5)
    setup_owner_and_pet()
    out = session(attention_inputs("fin", medication_lines=("Antibiótico", "10", "fin", "0")), rate=(987.65, False))
    assert "valor obtenido de mindicador.cl" in out and "$11851.80" in out


check("P16", lambda: in_database(test_p16))


def test_p17():
    from urllib.error import URLError
    for error in (URLError("sin red"), TimeoutError("lento")):
        with patch.object(indicador_api, "urlopen", side_effect=error):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                value, fallback = indicador_api.obtener_valor_dolar_info()
        assert value == 900.0 and fallback and "valor de respaldo" in output.getvalue()

    invalid_response = io.BytesIO(b'{"serie": []}')
    with patch.object(indicador_api, "urlopen", return_value=invalid_response):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            value, fallback = indicador_api.obtener_valor_dolar_info()
    assert value == 900.0 and fallback and "valor de respaldo" in output.getvalue()
    setup_owner_and_pet()
    out = session(attention_inputs("fin", medication_lines=("Antibiótico", "10", "fin", "0")), rate=(900.0, True))
    assert "Tipo de cambio (valor de respaldo)" in out and "TOTAL A PAGAR" in out


check("P17", lambda: in_database(test_p17))
check_output("P18", ["99", "0"], "Opción de prueba detectada")


def test_menu_edge_cases():
    out = session(["xyz", "2", "3", "985112003456789", "4", "985112003456789", "7", "abc", "1", "0"])
    assert "Opción no válida" in out
    assert "No hay mascotas registradas" in out
    assert "No se encontró una mascota" in out
    assert "No se encontró esa mascota" in out
    assert "Número inválido" in out


check("Menú: opciones inválidas y registros inexistentes", lambda: in_database(test_menu_edge_cases))


def test_interrupted_action():
    out = session(["1"])
    assert "Entrada interrumpida. Saliendo del sistema" in out


check("Menú: salida limpia al interrumpir una operación", lambda: in_database(test_interrupted_action))


def test_p19():
    setup_owner_and_pet()
    out = session(attention_inputs("Vacuna", "n", "abc", "100", "fin") + ["fin", "0"])
    assert "Número inválido" in out and "Atención guardada correctamente" in out


check("P19", lambda: in_database(test_p19))


def test_migration_and_rollback():
    db = Path(os.environ["HUELLITAS_DB_PATH"])
    connection = sqlite3.connect(db)
    connection.execute("CREATE TABLE mascota (numero_microchip TEXT PRIMARY KEY, tipo TEXT NOT NULL, fecha_ultima_vacuna TEXT NOT NULL)")
    connection.execute("INSERT INTO mascota VALUES (?, ?, ?)", ("985112003456789", "Perro", "2026-10-01"))
    connection.commit()
    connection.close()
    crear_tablas()
    assert MascotaDAO.obtener_por_microchip("985112003456789").nombre == "Mascota"
    MascotaDAO.eliminar("985112003456789")

    setup_owner_and_pet()
    connection = conectar()
    connection.execute("CREATE TRIGGER falla_detalle BEFORE INSERT ON detalle_atencion BEGIN SELECT RAISE(ABORT, 'fallo inyectado'); END")
    connection.commit()
    connection.close()
    owner = ClienteDAO.obtener_por_rut("12345678-9")
    pet = MascotaDAO.obtener_por_microchip("985112003456789")
    vet = Veterinario("11223344-5", "Dr. Juan Pérez", "juan@huellitas.cl", "987654321", 101, "jperez", "pass")
    atencion = Atencion(0, datetime.now(), 1000, vet, pet, owner)
    atencion.total = 25000
    atencion.agregarProcedimiento(1, "Vacuna", False, 10)
    assert AtencionDAO.insertar(atencion) is None
    connection = conectar()
    try:
        assert connection.execute("SELECT count(*) FROM atencion").fetchone()[0] == 0
        assert connection.execute("SELECT count(*) FROM detalle_atencion").fetchone()[0] == 0
    finally:
        connection.close()


check("Migración y rollback", lambda: in_database(test_migration_and_rollback, initialize=False))


def test_direct_rules():
    setup_owner_and_pet(debt=31, vaccine="2024-01-01")
    owner = ClienteDAO.obtener_por_rut("12345678-9")
    pet = MascotaDAO.obtener_por_microchip("985112003456789")
    vet = Veterinario("11223344-5", "Dr. Juan Pérez", "juan@huellitas.cl", "987654321", 101, "jperez", "pass")
    att = Atencion(0, datetime.now(), 1000, vet, pet, owner)
    try:
        AtencionDAO.insertar(att)
        raise AssertionError("Se aceptó una atención morosa")
    except ClienteMorosoError:
        pass
    owner.diasDeuda = 0
    try:
        att.agregarProcedimiento(1, "Cirugía", True, 100)
        raise AssertionError("Se aceptó cirugía con vacunas vencidas")
    except MascotaNoAptaCirugiaError:
        pass


check("Reglas directas modelo/DAO", lambda: in_database(test_direct_rules))


def test_client_ids_restart_at_first_available_number():
    connection = conectar()
    try:
        for client_id, rut in ((99, "11111111-1"), (999, "22222222-2"), (1000, "33333333-3")):
            connection.execute(
                "INSERT INTO cliente (id_cliente, rut, nombre, correo, telefono, dias_deuda) VALUES (?, ?, ?, ?, ?, ?)",
                (client_id, rut, "Cliente existente", "existente@example.cl", "987654321", 0),
            )
        connection.commit()
    finally:
        connection.close()

    first = Cliente("44444444-4", "Primero", "primero@example.cl", "987654321", None, 0)
    second = Cliente("55555555-5", "Segundo", "segundo@example.cl", "987654321", None, 0)
    assert ClienteDAO.insertar(first) == 1
    assert ClienteDAO.insertar(second) == 2
    ClienteDAO.eliminar(2)

    replacement = Cliente("66666666-6", "Reemplazo", "reemplazo@example.cl", "987654321", None, 0)
    assert ClienteDAO.insertar(replacement) == 2


check("IDs de clientes: empieza en 1, consecutivo y sin salto por secuencia vieja", lambda: in_database(test_client_ids_restart_at_first_available_number))


def test_database_location_is_independent_of_cwd():
    old_env = os.environ.pop("HUELLITAS_DB_PATH", None)
    try:
        with tempfile.TemporaryDirectory(prefix="huellitas-app-", dir=ROOT) as app_dir, \
             tempfile.TemporaryDirectory(prefix="huellitas-cwd-", dir=ROOT) as other_cwd:
            old_cwd = os.getcwd()
            try:
                with patch.object(database_module, "RUTA_BASE", Path(app_dir)):
                    os.chdir(other_cwd)
                    crear_tablas()
                assert (Path(app_dir) / "las_huellitas.db").is_file()
                assert not (Path(other_cwd) / "las_huellitas.db").exists()
            finally:
                os.chdir(old_cwd)
    finally:
        if old_env is not None:
            os.environ["HUELLITAS_DB_PATH"] = old_env


check("La base de datos mantiene su ubicación al ejecutar desde otra carpeta", test_database_location_is_independent_of_cwd)

print(f"\nResultado: {len(passed)} aprobados; {len(failed)} fallidos.")
if failed:
    sys.exit(1)
