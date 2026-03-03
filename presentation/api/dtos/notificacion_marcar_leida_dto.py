from pydantic import BaseModel

class NotificacionMarcarLeidaDTO(BaseModel):
    id: str
    supervisor_email: str
    