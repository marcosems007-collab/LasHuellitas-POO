from model.mascota import Mascota

class Perro(Mascota):
    def __init__(self, numeroMicrochip, fechaUltimaVacuna, nombre="Mascota"):
        super().__init__(numeroMicrochip, fechaUltimaVacuna, nombre)

    def obtenerDuracion(self) -> str:
        return "20 min"

    def obtenerTarifa(self) -> int:
        return 25000
