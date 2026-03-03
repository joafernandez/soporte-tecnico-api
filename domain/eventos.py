from domain.registros import Registro
from domain.enums import TipoEvento
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usuarios import Usuario
    from requerimientos import Requerimiento


class Evento(Registro):
    """
    evento del sistema con tipo específico.
    
    atributo
        tipo: Tipo de evento (enum)
    """
    
    def __init__(self, texto: str, autor: 'Usuario', tipo: TipoEvento) -> None:
        super().__init__(texto, autor)
        self.tipo: TipoEvento = tipo


class EventoFactory:
    """
    voy a usar factory para crear eventos de forma centralizada
    Patrón: Factory Method
    """
    
    @staticmethod
    def crear_evento_creacion(requerimiento: 'Requerimiento', autor: 'Usuario') -> Evento:
        """crea evento de creación de requerimiento"""
        texto = f"Requerimiento #{requerimiento.id} creado"
        return Evento(texto, autor, TipoEvento.CREACION)
    
    @staticmethod
    def crear_evento_asignacion(requerimiento: 'Requerimiento', tecnico: 'Usuario', operador: 'Usuario') -> Evento:
        """crea evento de asignación a técnico"""
        texto = f"Requerimiento #{requerimiento.id} asignado a {tecnico.nombre}"
        return Evento(texto, operador, TipoEvento.ASIGNACION)
    
    @staticmethod
    def crear_evento_derivacion(requerimiento: 'Requerimiento', tecnico_origen: 'Usuario', tecnico_destino: 'Usuario') -> Evento:
        """crea evento de derivación entre técnicos"""
        texto = f"Requerimiento #{requerimiento.id} derivado de {tecnico_origen.nombre} a {tecnico_destino.nombre}"
        return Evento(texto, tecnico_origen, TipoEvento.DERIVACION)
    
    @staticmethod
    def crear_evento_resolucion(requerimiento: 'Requerimiento', tecnico: 'Usuario', solucion: str) -> Evento:
        """crea evento de resolución"""
        texto = f"Requerimiento #{requerimiento.id} resuelto: {solucion}"
        return Evento(texto, tecnico, TipoEvento.RESOLUCION)
    
    @staticmethod
    def crear_evento_reapertura(requerimiento: 'Requerimiento', solicitante: 'Usuario', motivo: str) -> Evento:
        """crea evento de reapertura"""
        texto = f"Requerimiento #{requerimiento.id} reabierto: {motivo}"
        return Evento(texto, solicitante, TipoEvento.REAPERTURA)
    
    @staticmethod
    def crear_evento_cambio_estado(requerimiento: 'Requerimiento', autor: 'Usuario', estado_anterior: str, estado_nuevo: str) -> Evento:
        """crea evento de cambio de estado"""
        texto = f"Requerimiento #{requerimiento.id} cambió de {estado_anterior} a {estado_nuevo}"
        return Evento(texto, autor, TipoEvento.CAMBIO_ESTADO)