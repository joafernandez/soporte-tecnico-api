from abc import ABC, abstractmethod


class Urgencia(ABC):  #me llaman en la clase requrimeintos
    """
    interfaz para el patrón Strategy de urgencias
    define el contrato para calcular prioridad
    """
    
    @abstractmethod
    def calcular_prioridad(self) -> int:
        """calcula el valor de prioridad del requerimiento"""
        pass
    
    @abstractmethod
    def get_nombre(self) -> str:
        """retorna el nombre de la urgencia"""
        pass


class UrgenciaCritica(Urgencia):
    """
    si la urgencia es crítica - máxima prioridad
    para problemas graves que requieren atencion  inmediata
    """
    
    def calcular_prioridad(self) -> int:
        """retorna prioridad max"""
        return 10
    
    def get_nombre(self) -> str:
        """retorna nombre de la urgencia"""
        return "Crítica"


class UrgenciaImportante(Urgencia):
    """
    urgencia importante - prioridad media
    para problemas que afectan el servicio
    """
    
    def calcular_prioridad(self) -> int:
        """retorna prioridad media"""
        return 7
    
    def get_nombre(self) -> str:
        """retorna nombre de la urgencia"""
        return "Importante"


class UrgenciaMenor(Urgencia):
    """
    urgencia menor - baja prioridad
     para problemas menores que no afectan tanto el servicio
    """
    
    def calcular_prioridad(self) -> int:
        """retorna prioridad baja"""
        return 3
    
    def get_nombre(self) -> str:
        """retorna nombre de la urgencia"""
        return "Menor"