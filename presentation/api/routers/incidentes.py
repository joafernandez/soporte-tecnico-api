from fastapi import APIRouter, Depends, HTTPException

from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema
from presentation.api.dtos.incident_create_dto import IncidenteCreateDTO

from domain.usuarios import Solicitante
from domain.urgencias import UrgenciaCritica, UrgenciaImportante, UrgenciaMenor

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])


@router.post("/")
def crear_incidente(
    dto: IncidenteCreateDTO,
    sistema: SistemaAyuda = Depends(get_sistema)
):
    # ✅ buscar solicitante por email (trae de Mongo si hace falta)
    solicitante = sistema._buscar_usuario_por_email(dto.solicitante_email)
    if not solicitante:
        raise HTTPException(status_code=404, detail="Solicitante no encontrado")

    if not isinstance(solicitante, Solicitante):
        raise HTTPException(status_code=400, detail="El usuario no es solicitante")

    # mapear urgencia
    mapa_urgencias = {
        "critica": UrgenciaCritica(),
        "importante": UrgenciaImportante(),
        "menor": UrgenciaMenor(),
    }

    urgencia = mapa_urgencias.get(dto.urgencia.lower())
    if not urgencia:
        raise HTTPException(status_code=400, detail="Urgencia inválida (critica/importante/menor)")

    # buscar servicio por nombre (esto está perfecto como lo tenías)
    servicio = next((s for s in sistema.servicios if s.nombre == dto.servicio), None)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    incidente = sistema.crear_incidente(
        solicitante=solicitante,
        descripcion=dto.descripcion,
        urgencia=urgencia,
        servicio=servicio
    )

    return {
        "id": incidente.id,
        "estado": incidente.estado.value,
        "prioridad": incidente.calcular_prioridad()
    }
