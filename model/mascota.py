from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class Mascota(ABC):
    def __init__(self, numeroMicrochip: str, fechaUltimaVacuna: datetime, nombre: str = ""):
        self.numeroMicrochip = numeroMicrochip
        self.fechaUltimaVacuna = fechaUltimaVacuna
        self.nombre = nombre

    @property
    def numeroMicrochip(self) -> str:
        return self._numeroMicrochip

    @numeroMicrochip.setter
    def numeroMicrochip(self, valor: str):
        valor_str = str(valor)
        if len(valor_str) != 15 or not valor_str.isascii() or not valor_str.isdigit():
            raise ValueError("El número de microchip debe tener exactamente 15 dígitos numéricos.")
        self._numeroMicrochip = valor_str

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        nombre = str(valor).strip()
        if not nombre:
            raise ValueError("El nombre de la mascota es obligatorio.")
        self._nombre = nombre

    @abstractmethod
    def obtenerDuracion(self) -> str:
        pass

    @abstractmethod
    def obtenerTarifa(self) -> int:
        pass

    def estaAptaParaCirugia(self) -> bool:
        limite = datetime.now() - timedelta(days=365)
        return self.fechaUltimaVacuna >= limite
