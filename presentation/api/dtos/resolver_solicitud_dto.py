from pydantic import BaseModel

class ResolverSolicitudDTO(BaseModel):
    tecnico_email: str
    solucion: str
    