from model.persona import Persona


class Cliente(Persona):
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str, idCliente: int | None, diasDeuda: int):
        self._diasDeuda = 0
        self._idCliente = 0
        super().__init__(rut, nombre, correo, telefono)
        # Un cliente nuevo aún no tiene ID; SQLite se lo asigna al insertarlo.
        if idCliente is not None and idCliente != 0:
            self.idCliente = idCliente
        self.diasDeuda = diasDeuda

    def obtenerRol(self) -> str: return "Cliente"

    @property
    def idCliente(self): return self._idCliente

    @idCliente.setter
    def idCliente(self, valor):
        if type(valor) is not int or valor <= 0:
            raise TypeError("idCliente debe ser entero positivo.")
        self._idCliente = valor

    @property
    def diasDeuda(self) -> int: return self._diasDeuda

    @diasDeuda.setter
    def diasDeuda(self, valor: int):
        v = int(valor)
        if v < 0: raise ValueError("Los días de deuda no pueden ser negativos.")
        self._diasDeuda = v

    def estaMoroso(self) -> bool: return self._diasDeuda > 30
