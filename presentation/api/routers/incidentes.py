from fastapi import APIRouter, Depends, HTTPException
from presentation.api.dtos.comentario_create_dto import ComentarioCreateDTO

from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema
from presentation.api.dtos.incident_create_dto import IncidenteCreateDTO

from domain.usuarios import Solicitante
from domain.urgencias import UrgenciaCritica, UrgenciaImportante, UrgenciaMenor
from presentation.api.dtos.asignar_tecnico_dto import AsignarTecnicoDTO
from presentation.api.dtos.derivar_tecnico_dto import DerivarTecnicoDTO
from presentation.api.dtos.resolver_incidente_dto import ResolverIncidenteDTO
from presentation.api.dtos.reabrir_incidente_dto import ReabrirIncidenteDTO


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

from domain.usuarios import Operador, Tecnico
from domain.eventos import EventoFactory


@router.post("/{incidente_id}/asignar-tecnico")
def asignar_tecnico_incidente(
    incidente_id: int,
    dto: AsignarTecnicoDTO,
    sistema: SistemaAyuda = Depends(get_sistema),
):
    # Validar existencia del incidente en Mongo
    doc = sistema.repositorio_incidentes.buscar_por_id(incidente_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe incidente con id {incidente_id}")

    # Traer operador y técnico desde Mongo (reconstruye objetos del dominio)
    operador = sistema._buscar_usuario_por_email(dto.operador_email)
    if not operador:
        raise HTTPException(status_code=404, detail="Operador no encontrado")
    if not isinstance(operador, Operador):
        raise HTTPException(status_code=400, detail="El usuario no es operador")

    tecnico = sistema._buscar_usuario_por_email(dto.tecnico_email)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    if not isinstance(tecnico, Tecnico):
        raise HTTPException(status_code=400, detail="El usuario no es técnico")

    # Construir evento y persistir directo en Mongo
    evento_doc = {
        "texto": f"Requerimiento #{incidente_id} asignado a {tecnico.nombre}",
        "autor_email": operador.email,
        "autor_nombre": operador.nombre,
        "fecha": __import__('datetime').datetime.now().isoformat(),
        "tipo": "TipoEvento.ASIGNACION",
    }

    sistema.repositorio_incidentes.coleccion.update_one(
        {"id": incidente_id},
        {"$set": {"tecnico_asignado_email": tecnico.email, "estado": "en_proceso"},
         "$push": {"eventos": evento_doc}}
    )

    return {"ok": True, "incidente_id": incidente_id, "tecnico_email": tecnico.email, "evento": evento_doc}
@router.post("/{incidente_id}/derivar")
def derivar_incidente(
    incidente_id: int,
    dto: DerivarTecnicoDTO,
    sistema: SistemaAyuda = Depends(get_sistema),
):
    doc = sistema.repositorio_incidentes.buscar_por_id(incidente_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"No existe incidente con id {incidente_id}")

    tecnico_asignado = doc.get("tecnico_asignado_email")
    if tecnico_asignado is None:
        raise HTTPException(status_code=400, detail="El incidente no tiene técnico asignado aún")

    if tecnico_asignado != dto.tecnico_origen_email:
        raise HTTPException(status_code=400, detail="El incidente no está asignado al técnico origen")

    tecnico_origen = sistema._buscar_usuario_por_email(dto.tecnico_origen_email)
    if tecnico_origen is None:
        raise HTTPException(status_code=404, detail="Técnico origen no encontrado")

    tecnico_destino = sistema._buscar_usuario_por_email(dto.tecnico_destino_email)
    if tecnico_destino is None:
        raise HTTPException(status_code=404, detail="Técnico destino no encontrado")

    autor = sistema._buscar_usuario_por_email(dto.autor_email)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    evento_doc = {
        "texto": f"Requerimiento #{incidente_id} derivado de {tecnico_origen.nombre} a {tecnico_destino.nombre}",
        "autor_email": autor.email,
        "autor_nombre": autor.nombre,
        "fecha": __import__('datetime').datetime.now().isoformat(),
        "tipo": "TipoEvento.DERIVACION",
    }

    sistema.repositorio_incidentes.coleccion.update_one(
        {"id": incidente_id},
        {"$set": {"tecnico_asignado_email": tecnico_destino.email},
         "$push": {"eventos": evento_doc}}
    )

    return {"ok": True, "incidente_id": incidente_id, "tecnico_destino_email": tecnico_destino.email}


@router.post("/{incidente_id}/resolver")
def resolver_incidente(
    incidente_id: int,
    dto: ResolverIncidenteDTO,
    sistema: SistemaAyuda = Depends(get_sistema),
):
    doc = sistema.repositorio_incidentes.buscar_por_id(incidente_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe incidente con id {incidente_id}")

    # validar técnico
    tecnico = sistema._buscar_usuario_por_email(dto.tecnico_email)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    # debe ser el técnico asignado
    if doc.get("tecnico_asignado_email") != dto.tecnico_email:
        raise HTTPException(status_code=400, detail="El incidente no está asignado a ese técnico")

    # evento + comentario solución
    evento_doc = {
        "texto": f"Requerimiento #{incidente_id} resuelto: {dto.solucion}",
        "autor_email": tecnico.email,
        "autor_nombre": tecnico.nombre,
        "fecha": __import__('datetime').datetime.now().isoformat(),
        "tipo": "TipoEvento.RESOLUCION",
    }
    comentario_doc = {
        "texto": f"Solución: {dto.solucion}",
        "autor_email": tecnico.email,
        "autor_nombre": tecnico.nombre,
        "fecha": __import__('datetime').datetime.now().isoformat(),
    }

    sistema.repositorio_incidentes.coleccion.update_one(
        {"id": incidente_id},
        {"$set": {"estado": "resuelto"},
         "$push": {"eventos": evento_doc, "comentarios": comentario_doc}}
    )

    return {"ok": True, "incidente_id": incidente_id}


@router.post("/{incidente_id}/reabrir")
def reabrir_incidente(
    incidente_id: int,
    dto: ReabrirIncidenteDTO,
    sistema: SistemaAyuda = Depends(get_sistema),
):
    doc = sistema.repositorio_incidentes.buscar_por_id(incidente_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe incidente con id {incidente_id}")

    # Solo si está resuelto
    if doc.get("estado") != "resuelto":
        raise HTTPException(status_code=400, detail="El incidente no está resuelto, no se puede reabrir")

    autor = sistema._buscar_usuario_por_email(dto.autor_email)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    evento_doc = {
        "texto": f"Requerimiento #{incidente_id} reabierto: {dto.motivo}",
        "autor_email": autor.email,
        "autor_nombre": autor.nombre,
        "fecha": __import__('datetime').datetime.now().isoformat(),
        "tipo": "TipoEvento.REAPERTURA",
    }
    comentario_doc = {
        "texto": f"Reabierto: {dto.motivo}",
        "autor_email": autor.email,
        "autor_nombre": autor.nombre,
        "fecha": __import__('datetime').datetime.now().isoformat(),
    }

    sistema.repositorio_incidentes.coleccion.update_one(
        {"id": incidente_id},
        {"$set": {"estado": "reabierto"},
         "$push": {"eventos": evento_doc, "comentarios": comentario_doc}}
    )

    return {"ok": True, "incidente_id": incidente_id}




