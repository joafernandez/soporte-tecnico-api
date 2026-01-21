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

