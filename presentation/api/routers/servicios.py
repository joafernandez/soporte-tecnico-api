from fastapi import APIRouter, Depends
from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema

router = APIRouter(prefix="/servicios", tags=["Servicios"])

@router.get("/")
def listar_servicios(sistema: SistemaAyuda = Depends(get_sistema)):
    return [{"nombre": s.nombre, "descripcion": s.descripcion} for s in sistema.servicios]

