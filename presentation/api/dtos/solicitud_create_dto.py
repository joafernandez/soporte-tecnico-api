from pydantic import BaseModel


class SolicitudCreateDTO(BaseModel):
    descripcion: str
    tipo_solicitud: str   # alta o baja
    servicio: str
    solicitante_email: str
    