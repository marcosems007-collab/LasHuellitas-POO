import math


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
        if not math.isfinite(v) or v < 0: raise ValueError("El costo debe ser un número finito no negativo.")
        self._costo = v
