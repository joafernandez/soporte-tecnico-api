from pydantic import BaseModel
from datetime import datetime


class NotificacionRespuestaDTO(BaseModel):
    id: str
    supervisor_email: str
    texto: str
    autor_email: str
    autor_nombre: str
    fecha: datetime
    tipo_evento: str
    requerimiento_id: int
    leida: bool
    
    
    