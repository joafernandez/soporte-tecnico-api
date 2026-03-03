from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema
from presentation.api.dtos.solicitante_create_dto import SolicitanteCreateDTO

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/solicitantes")
def crear_solicitante(
    dto: SolicitanteCreateDTO,
    sistema: SistemaAyuda = Depends(get_sistema)
):
    try:
        usuario = sistema.registrar_usuario(
            "solicitante",
            dto.nombre,
            dto.email,
            dto.password
        )
        return {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "tipo": "solicitante"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/supervisores")
def crear_supervisor(
    dto: SolicitanteCreateDTO,
    sistema: SistemaAyuda = Depends(get_sistema)
):
    try:
        usuario = sistema.registrar_usuario(
            "supervisor",
            dto.nombre,
            dto.email,
            dto.password
        )
        return {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "tipo": "supervisor"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class AsignarSupervisorDTO(BaseModel):
    supervisor_email: str
    empleado_email: str


@router.post("/supervisores/asignar")
def asignar_supervisor(
    dto: AsignarSupervisorDTO,
    sistema: SistemaAyuda = Depends(get_sistema)
):
    sup = sistema._buscar_usuario_por_email(dto.supervisor_email)
    emp = sistema._buscar_usuario_por_email(dto.empleado_email)

    if not sup or not emp:
        raise HTTPException(status_code=404, detail="Supervisor o empleado no existe")

    sistema.asignar_supervisor(sup, emp)
    return {"ok": True}


@router.get("/")
def listar_usuarios(sistema: SistemaAyuda = Depends(get_sistema)):
    return sistema.repositorio_usuarios.listar()


@router.get("/{email}")
def ver_usuario_por_email(email: str, sistema: SistemaAyuda = Depends(get_sistema)):
    doc = sistema.repositorio_usuarios.buscar_por_email(email)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe usuario con email {email}")
    return doc


