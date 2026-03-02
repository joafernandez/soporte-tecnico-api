from fastapi import APIRouter, Depends, HTTPException
from presentation.api.dtos.comentario_create_dto import ComentarioCreateDTO

from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema
from presentation.api.dtos.solicitud_create_dto import SolicitudCreateDTO

from domain.usuarios import Solicitante
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


@router.post("/{solicitud_id}/comentarios")
def agregar_comentario_solicitud(
    solicitud_id: int,
    dto: ComentarioCreateDTO,
    sistema: SistemaAyuda = Depends(get_sistema),
):
    autor = sistema._buscar_usuario_por_email(dto.autor_email)
    if not autor:
        raise HTTPException(status_code=404, detail=f"No existe usuario con email {dto.autor_email}")

    doc_existente = sistema.repositorio_solicitudes.buscar_por_id(solicitud_id)
    if not doc_existente:
        raise HTTPException(status_code=404, detail=f"No existe solicitud con id {solicitud_id}")

    comentario_doc = {
        "texto": dto.texto,
        "autor_email": autor.email,
        "autor_nombre": autor.nombre,
        "fecha": __import__("datetime").datetime.now().isoformat(),
    }

    sistema.repositorio_solicitudes.collection.update_one(
        {"id": solicitud_id},
        {"$push": {"comentarios": comentario_doc}}
    )

    return {"ok": True, "solicitud_id": solicitud_id, "comentario": comentario_doc}


@router.get("/")
def listar_solicitudes(sistema: SistemaAyuda = Depends(get_sistema)):
    return sistema.repositorio_solicitudes.listar()


@router.get("/{solicitud_id}")
def ver_solicitud(solicitud_id: int, sistema: SistemaAyuda = Depends(get_sistema)):
    doc = sistema.repositorio_solicitudes.buscar_por_id(solicitud_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe solicitud con id {solicitud_id}")
    return doc