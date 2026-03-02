from fastapi import APIRouter, Depends, HTTPException

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


@router.get("/")
def listar_usuarios(sistema: SistemaAyuda = Depends(get_sistema)):
    return sistema.repositorio_usuarios.listar()


@router.get("/{email}")
def ver_usuario_por_email(email: str, sistema: SistemaAyuda = Depends(get_sistema)):
    doc = sistema.repositorio_usuarios.buscar_por_email(email)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No existe usuario con email {email}")
    return doc

