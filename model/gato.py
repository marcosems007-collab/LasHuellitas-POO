from model.mascota import Mascota

class Gato(Mascota):
    def __init__(self, numeroMicrochip, fechaUltimaVacuna, nombre="Mascota"):
        super().__init__(numeroMicrochip, fechaUltimaVacuna, nombre)

    def obtenerDuracion(self) -> str:
        return "15 min"

    def obtenerTarifa(self) -> int:
        return 20000
