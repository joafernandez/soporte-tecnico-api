from pydantic import BaseModel

class ReabrirSolicitudDTO(BaseModel):
    autor_email: str
    motivo: str
    