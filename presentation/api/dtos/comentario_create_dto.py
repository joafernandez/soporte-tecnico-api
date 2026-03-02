from pydantic import BaseModel

class ComentarioCreateDTO(BaseModel):
    autor_email: str
    texto: str
    