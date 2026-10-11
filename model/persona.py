from abc import ABC, abstractmethod
import re

class Persona(ABC):
    def __init__(self, rut: str, nombre: str, correo: str, telefono: str):
        self._rut = None
        self._correo = None
        self._telefono = None
        
        self.rut = rut
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def rut(self) -> str: return self._rut
    @rut.setter
    def rut(self, valor: str):
        if not re.match(r"^\d{7,8}-[\dkK]$", str(valor)):
            raise ValueError(f"Formato de RUT inválido: {valor}")
        self._rut = valor

    @property
    def correo(self) -> str: return self._correo
    @correo.setter
    def correo(self, valor: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", str(valor)):
            raise ValueError(f"Formato de correo inválido: {valor}")
        self._correo = valor

    @property
    def telefono(self) -> str: return self._telefono
    @telefono.setter
    def telefono(self, valor: str):
        if not str(valor).isdigit() or len(str(valor)) < 8:
            raise ValueError("Formato de teléfono inválido (debe tener al menos 8 dígitos).")
        self._telefono = valor
        
    @abstractmethod
    def obtenerRol(self) -> str: pass
