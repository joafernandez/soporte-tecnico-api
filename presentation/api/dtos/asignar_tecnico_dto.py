from pydantic import BaseModel

class AsignarTecnicoDTO(BaseModel):
    operador_email: str
    tecnico_email: str
    