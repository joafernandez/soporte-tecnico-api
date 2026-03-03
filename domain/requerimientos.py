from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from domain.enums import EstadoRequerimiento, TipoSolicitud
from domain.registros import Comentario
from domain.eventos import Evento
from domain.urgencias import Urgencia
from domain.servicios import Servicio

if TYPE_CHECKING:
    from domain.usuarios import Usuario, Solicitante, Tecnico, Operador


class Requerimiento(ABC):
    """
    clase base abstracta 
    
    """
    
    _contador_id: int = 0
    
    def __init__(self, descripcion: str, solicitante: 'Solicitante') -> None:
        Requerimiento._contador_id += 1
        self.id: int = Requerimiento._contador_id
        self.descripcion: str = descripcion
        self.solicitante: 'Solicitante' = solicitante
        self.estado: EstadoRequerimiento = EstadoRequerimiento.ABIERTO
        self.tecnico_asignado: Optional['Tecnico'] = None
        self.fecha_creacion: datetime = datetime.now()
        self.fecha_resolucion: Optional[datetime] = None
        self.comentarios: List[Comentario] = []
        self.eventos: List[Evento] = []
    
    def agregar_comentario(self, texto: str, autor: 'Usuario') -> Comentario:
        """agrega un comentario """
        comentario = Comentario(texto, autor)
        self.comentarios.append(comentario)
        return comentario
    
    def agregar_evento(self, evento: Evento) -> None:
        """agrega un evento al historial"""
        self.eventos.append(evento)
    
    def asignar_tecnico(self, tecnico: 'Tecnico') -> None:
        """asigna un técnico al requerimiento"""
        self.tecnico_asignado = tecnico
        self.estado = EstadoRequerimiento.EN_PROCESO
    
    def resolver(self, solucion: str) -> None:
        """marca el requerimiento como resuelto"""
        self.estado = EstadoRequerimiento.RESUELTO
        self.fecha_resolucion = datetime.now()
    
    def reabrir(self) -> None:
        """reabre un requerimiento resuelto"""
        if self.estado == EstadoRequerimiento.RESUELTO:
            self.estado = EstadoRequerimiento.REABIERTO
            self.fecha_resolucion = None
    
    def derivar(self, nuevo_tecnico: 'Tecnico') -> None:
        """deriva el requerimiento a otro tec"""
        self.tecnico_asignado = nuevo_tecnico
    
    @abstractmethod
    def calcular_prioridad(self) -> int:
        """calcula la prioridad del requerimiento (cada hijo lo implementa)"""
        pass
    
    def __str__(self) -> str:
        return f"Requerimiento #{self.id}: {self.descripcion[:50]}... (Prioridad: {self.calcular_prioridad()})"


class Incidente(Requerimiento):
    """
    requerimiento por problemas en servicios existentes
    usa Strategy Pattern  para definir la urgencia :)  -----> LLAMA A CLASE URGENCIA  !!!
    
   
         estrategia de urgencia (crítica/importante/menor)
    """
    
    def __init__(self, descripcion: str, solicitante: 'Solicitante', urgencia: Urgencia, servicio: Optional[Servicio] = None) -> None:
        super().__init__(descripcion, solicitante)
        self.urgencia: Urgencia = urgencia
        self.servicio: Optional[Servicio] = servicio
    
    def calcular_prioridad(self) -> int:
        """delega el calculo a la estrategia de urgencia"""
        return self.urgencia.calcular_prioridad()
    
    def cambiar_urgencia(self, nueva_urgencia: Urgencia) -> None:
        """cambia la estrategia de urgencia en runtime"""
        self.urgencia = nueva_urgencia


class Solicitud(Requerimiento):
    """
    REQ para alta o baja de servicios
    prioridad fija no calcula 
    
   
    """
    
    def __init__(self, descripcion: str, solicitante: 'Solicitante', tipo_solicitud: TipoSolicitud, servicio: Servicio) -> None:
        super().__init__(descripcion, solicitante)
        self.tipo_solicitud: TipoSolicitud = tipo_solicitud
        self.servicio: Servicio = servicio
    
    def calcular_prioridad(self) -> int:
        """las solicitudes tienen prioridad fija"""
        return 5