import math


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
        if not math.isfinite(v) or v < 0: raise ValueError("El precio USD debe ser un número finito no negativo.")
        self._precioUSD = v

    @property
    def margenGanancia(self): return self._margenGanancia
    @margenGanancia.setter
    def margenGanancia(self, valor):
        v = float(valor)
        if not math.isfinite(v) or v < 0: raise ValueError("El margen debe ser un número finito no negativo.")
        self._margenGanancia = v

    def calcularPrecioCLP(self, tipoCambioDolar: float) -> float:
        return self.precioUSD * tipoCambioDolar * (1 + self.margenGanancia)
