from fastapi import APIRouter, Depends, HTTPException
from application.sistema import SistemaAyuda
from presentation.api.dependencias import get_sistema

router = APIRouter(prefix="/requerimientos", tags=["Requerimientos"])


@router.get("/")
def listar_requerimientos_por_rol(email: str, sistema: SistemaAyuda = Depends(get_sistema)):
    # 1) validar usuario
    usuario = sistema._buscar_usuario_por_email(email)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2) traer TODO desde Mongo
    incidentes = sistema.repositorio_incidentes.listar()
    solicitudes = sistema.repositorio_solicitudes.listar()
    todos = incidentes + solicitudes

    # 3) filtrar por rol (en base al tipo de usuario)
    tipo = usuario.__class__.__name__.lower()  # solicitante/operador/tecnico/supervisor

    if tipo == "solicitante":
        return [r for r in todos if r.get("solicitante_email") == email]

    if tipo == "tecnico":
        return [r for r in todos if r.get("tecnico_asignado_email") == email]

    if tipo in ("operador", "supervisor"):
        return todos

    return []
