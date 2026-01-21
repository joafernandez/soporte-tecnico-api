from pydantic import BaseModel, EmailStr


class SolicitanteCreateDTO(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    