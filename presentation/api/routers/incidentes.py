from fastapi import APIRouter, Depends, HTTPException
from presentation.api.dtos.comentario_create_dto import ComentarioCreateDTO

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
    solicitante = sistema._buscar_usuario_por_email(dto.solicitante_email)
    if not solicitante:
        raise HTTPException(status_code=404, detail="Solicitante no encontrado")

    if not isinstance(solicitante, Solicitante):
        raise HTTPException(status_code=400, detail="El usuario no es solicitante")

    mapa_urgencias = {
        "critica": UrgenciaCritica(),
        "importante": UrgenciaImportante(),
        "menor": UrgenciaMenor(),
    }

    urgencia = mapa_urgencias.get(dto.urgencia.lower())
    if not urgencia:
        raise HTTPException(status_code=400, detail="Urgencia inválida (critica/importante/menor)")

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
        "estado": getattr(incidente.estado, "value", str(incidente.estado)),
        "prioridad": incidente.calcular_prioridad()
    }


@router.post("/{incidente_id}/comentarios")
def agregar_comentario(
    incidente_id: int,
    dto: ComentarioCreateDTO,
    sistema: SistemaAyuda = Depends(get_sistema),
):
    autor = sistema._buscar_usuario_por_email(dto.autor_email)
    if not autor:
        raise HTTPException(status_code=404, detail=f"No existe usuario con email {dto.autor_email}")

    comentario_doc = {
        "texto": dto.texto,
        "autor_email": autor.email,
        "autor_nombre": autor.nombre,
        "fecha": __import__("datetime").datetime.now().isoformat(),
    }

    doc_existente = sistema.repositorio_incidentes.buscar_por_id(incidente_id)
    if not doc_existente:
        raise HTTPException(status_code=404, detail=f"No existe incidente con id {incidente_id}")

    sistema.repositorio_incidentes.agregar_comentario_por_id(incidente_id, comentario_doc)

    return {"ok": True, "incidente_id": incidente_id, "comentario": comentario_doc}


@router.get("/")
def listar_incidentes(sistema: SistemaAyuda = Depends(get_sistema)):
    return sistema.repositorio_incidentes.listar()


@router.get("/{incidente_id}")
def ver_incidente(incidente_id: int, sistema: SistemaAyuda = Depends(get_sistema)):
    doc = sistema.repositorio_incidentes.buscar_por_id(incidente_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe incidente con id {incidente_id}")
    return doc

