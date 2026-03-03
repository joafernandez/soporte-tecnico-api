from typing import List
from fastapi import APIRouter, Depends, Query

from presentation.api.dtos.notificacion_respuesta_dto import NotificacionRespuestaDTO
from presentation.api.dtos.notificacion_marcar_leida_dto import NotificacionMarcarLeidaDTO
from presentation.api.dependencias import get_sistema

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("/", response_model=List[NotificacionRespuestaDTO])
def listar_notificaciones(
    supervisor_email: str = Query(...),
    solo_no_leidas: bool = Query(False),
    sistema=Depends(get_sistema)
):
    return sistema.listar_notificaciones(supervisor_email, solo_no_leidas)


@router.post("/marcar-leida")
def marcar_leida(dto: NotificacionMarcarLeidaDTO, sistema=Depends(get_sistema)):
    ok = sistema.marcar_notificacion_leida(dto.supervisor_email, dto.id)
    return {"ok": ok}

