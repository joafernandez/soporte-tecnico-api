from pydantic import BaseModel

class DerivarTecnicoDTO(BaseModel):
    tecnico_origen_email: str
    tecnico_destino_email: str
    autor_email: str
    
    
    
    