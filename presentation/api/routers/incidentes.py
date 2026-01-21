from fastapi import APIRouter, HTTPException

from application.sistema import SistemaAyuda
from domain.urgencias import UrgenciaCritica, UrgenciaImportante, UrgenciaMenor
from presentation.api.dtos.incident_create_dto import IncidenteCreateDTO

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])

# Instancia única (por ahora, en memoria)
sistema = SistemaAyuda()


@router.post("/")
def crear_incidente(dto: IncidenteCreateDTO):
    # buscar solicitante por email
    solicitante = next((u for u in sistema.usuarios if u.email == dto.solicitante_email), None)
    if not solicitante:
        raise HTTPException(status_code=404, detail="Solicitante no encontrado")

    # mapear urgencia
    mapa_urgencias = {
        "critica": UrgenciaCritica(),
        "importante": UrgenciaImportante(),
        "menor": UrgenciaMenor(),
    }
    urgencia = mapa_urgencias.get(dto.urgencia.lower())
    if not urgencia:
        raise HTTPException(status_code=400, detail="Urgencia inválida (critica/importante/menor)")

    # buscar servicio por nombre
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
