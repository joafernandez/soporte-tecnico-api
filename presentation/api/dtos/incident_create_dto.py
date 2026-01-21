from pydantic import BaseModel

class IncidenteCreateDTO(BaseModel):
    descripcion: str
    urgencia: str
    servicio: str
    solicitante_email: str
