from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from enums import EstadoRequerimiento, TipoSolicitud
from registros import Comentario
from eventos import Evento
from urgencias import Urgencia
from servicios import Servicio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usuarios import Usuario, Solicitante, Tecnico, Operador


class Requerimiento(ABC):
    """
    Clase base abstracta para requerimientos del sistema.
    
    Attributes:
        id: Identificador único
        descripcion: Descripción del requerimiento
        solicitante: Usuario que creó el requerimiento
        estado: Estado actual del requerimiento
        tecnico_asignado: Técnico asignado (opcional)
        fecha_creacion: Timestamp de creación
        fecha_resolucion: Timestamp de resolución (opcional)
        comentarios: Lista de comentarios
        eventos: Lista de eventos
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
        """Agrega un comentario inmutable al requerimiento."""
        comentario = Comentario(texto, autor)
        self.comentarios.append(comentario)
        return comentario
    
    def agregar_evento(self, evento: Evento) -> None:
        """Agrega un evento al historial."""
        self.eventos.append(evento)
    
    def asignar_tecnico(self, tecnico: 'Tecnico') -> None:
        """Asigna un técnico al requerimiento."""
        self.tecnico_asignado = tecnico
        self.estado = EstadoRequerimiento.EN_PROCESO
    
    def resolver(self, solucion: str) -> None:
        """Marca el requerimiento como resuelto."""
        self.estado = EstadoRequerimiento.RESUELTO
        self.fecha_resolucion = datetime.now()
    
    def reabrir(self) -> None:
        """Reabre un requerimiento resuelto."""
        if self.estado == EstadoRequerimiento.RESUELTO:
            self.estado = EstadoRequerimiento.REABIERTO
            self.fecha_resolucion = None
    
    def derivar(self, nuevo_tecnico: 'Tecnico') -> None:
        """Deriva el requerimiento a otro técnico."""
        self.tecnico_asignado = nuevo_tecnico
    
    @abstractmethod
    def calcular_prioridad(self) -> int:
        """Calcula la prioridad del requerimiento (cada hijo lo implementa)."""
        pass
    
    def __str__(self) -> str:
        return f"Requerimiento #{self.id}: {self.descripcion[:50]}... (Prioridad: {self.calcular_prioridad()})"


class Incidente(Requerimiento):
    """
    Requerimiento por problemas en servicios existentes.
    Usa Strategy Pattern para urgencias.
    
    Attributes:
        urgencia: Estrategia de urgencia (Crítica/Importante/Menor)
        servicio: Servicio afectado (opcional)
    """
    
    def __init__(self, descripcion: str, solicitante: 'Solicitante', urgencia: Urgencia, servicio: Optional[Servicio] = None) -> None:
        super().__init__(descripcion, solicitante)
        self.urgencia: Urgencia = urgencia
        self.servicio: Optional[Servicio] = servicio
    
    def calcular_prioridad(self) -> int:
        """Delega el cálculo a la estrategia de urgencia."""
        return self.urgencia.calcular_prioridad()
    
    def cambiar_urgencia(self, nueva_urgencia: Urgencia) -> None:
        """Cambia la estrategia de urgencia en runtime."""
        self.urgencia = nueva_urgencia


class Solicitud(Requerimiento):
    """
    Requerimiento para alta o baja de servicios.
    Prioridad fija.
    
    Attributes:
        tipo_solicitud: Alta o baja de servicio
        servicio: Servicio solicitado
    """
    
    def __init__(self, descripcion: str, solicitante: 'Solicitante', tipo_solicitud: TipoSolicitud, servicio: Servicio) -> None:
        super().__init__(descripcion, solicitante)
        self.tipo_solicitud: TipoSolicitud = tipo_solicitud
        self.servicio: Servicio = servicio
    
    def calcular_prioridad(self) -> int:
        """Las solicitudes tienen prioridad fija."""
        return 5