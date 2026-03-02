from pydantic import BaseModel

class ReabrirIncidenteDTO(BaseModel):
    autor_email: str
    motivo: str
    
    