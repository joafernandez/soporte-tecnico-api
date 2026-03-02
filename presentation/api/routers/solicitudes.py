from fastapi import APIRouter, Depends, HTTPException

from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema
from presentation.api.dtos.solicitud_create_dto import SolicitudCreateDTO

from domain.usuarios import Solicitante
from domain.requerimientos import Solicitud
from domain.enums import TipoSolicitud

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post("/")
def crear_solicitud(
    dto: SolicitudCreateDTO,
    sistema: SistemaAyuda = Depends(get_sistema)
):
    solicitante = sistema._buscar_usuario_por_email(dto.solicitante_email)
    if not solicitante:
        raise HTTPException(status_code=404, detail="Solicitante no encontrado")

    if not isinstance(solicitante, Solicitante):
        raise HTTPException(status_code=400, detail="El usuario no es solicitante")

    servicio = next((s for s in sistema.servicios if s.nombre == dto.servicio), None)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    try:
        tipo = TipoSolicitud[dto.tipo_solicitud.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Tipo de solicitud inválido")

    solicitud = sistema.crear_solicitud(
        solicitante=solicitante,
        descripcion=dto.descripcion,
        tipo_solicitud=tipo,
        servicio=servicio
    )
    
    
    return {
    "id": solicitud.id,
    "estado": getattr(solicitud.estado, "value", str(solicitud.estado)),
    "tipo": getattr(solicitud.tipo_solicitud, "value", str(solicitud.tipo_solicitud))
}

 #me quede aca no anduvo error 500 ya cambie el return 
 