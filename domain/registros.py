from abc import ABC
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usuarios import Usuario


class Registro(ABC):
    """
    clase base abstracta para todo registro auditable del sistema.
    
    attributes:
        texto: Contenido del registro
        autor: Usuario que creó el registro
        fecha: Timestamp de creación automático
    """
    
    def __init__(self, texto: str, autor: 'Usuario') -> None:
        self.texto: str = texto
        self.autor: 'Usuario' = autor
        self.fecha: datetime = datetime.now()
    
    def __str__(self) -> str:
        return f"[{self.fecha.strftime('%Y-%m-%d %H:%M:%S')}] {self.autor.nombre}: {self.texto}"


class Comentario(Registro):
    """
    comentario en un requerimiento
    Hereda de Registro sin atributos adicionales
    
    LO DEJO IGUAL PARA FUTURO !!!!!!!!!!
    """
    pass


class Notificacion(Registro):
    """
    notificación enviada a un supervisor (Observer Pattern)
    
    Atributos:
        leida: Indica si la notificación fue vista
    """
    
    def __init__(self, texto: str, autor: 'Usuario') -> None:
        super().__init__(texto, autor)
        self.leida: bool = False
    
    def marcar_como_leida(self) -> None:
        """Marca la notificación como leída."""
        self.leida = True