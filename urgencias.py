from abc import ABC, abstractmethod


class Urgencia(ABC):
    """
    Interfaz para el patrón Strategy de urgencias.
    Define el contrato para calcular prioridad.
    """
    
    @abstractmethod
    def calcular_prioridad(self) -> int:
        """Calcula el valor de prioridad del requerimiento."""
        pass
    
    @abstractmethod
    def get_nombre(self) -> str:
        """Retorna el nombre de la urgencia."""
        pass


class UrgenciaCritica(Urgencia):
    """
    Urgencia crítica - máxima prioridad.
    Para problemas graves que requieren atención inmediata.
    """
    
    def calcular_prioridad(self) -> int:
        """Retorna prioridad máxima."""
        return 10
    
    def get_nombre(self) -> str:
        """Retorna nombre de la urgencia."""
        return "Crítica"


class UrgenciaImportante(Urgencia):
    """
    Urgencia importante - prioridad media.
    Para problemas significativos que afectan el servicio.
    """
    
    def calcular_prioridad(self) -> int:
        """Retorna prioridad media."""
        return 7
    
    def get_nombre(self) -> str:
        """Retorna nombre de la urgencia."""
        return "Importante"


class UrgenciaMenor(Urgencia):
    """
    Urgencia menor - baja prioridad.
    Para problemas menores que no afectan significativamente el servicio.
    """
    
    def calcular_prioridad(self) -> int:
        """Retorna prioridad baja."""
        return 3
    
    def get_nombre(self) -> str:
        """Retorna nombre de la urgencia."""
        return "Menor"