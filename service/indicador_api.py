import json
import math
from urllib.error import URLError
from urllib.request import urlopen

URL_DOLAR = "https://mindicador.cl/api/dolar"
VALOR_RESPALDO = 900.0


def obtener_valor_dolar_info() -> tuple[float, bool]:
    """Devuelve (valor, es_respaldo); el respaldo nunca se presenta como dato actual."""
    try:
        with urlopen(URL_DOLAR, timeout=5) as response:
            datos = json.load(response)
        valor = float(datos["serie"][0]["valor"])
        if not math.isfinite(valor) or valor <= 0:
            raise ValueError("La API entregó un valor de dólar inválido.")
        return valor, False
    except (URLError, TimeoutError, ValueError, KeyError, TypeError, IndexError) as e:
        print(f"No se pudo obtener el dólar actual ({e}). Se usará el valor de respaldo ${VALOR_RESPALDO:.1f}; no corresponde al valor actual.")
        return VALOR_RESPALDO, True


def obtener_valor_dolar() -> float:
    """Compatibilidad con código que solo necesita el importe."""
    return obtener_valor_dolar_info()[0]
