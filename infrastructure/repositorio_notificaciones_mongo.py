from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from infrastructure.conexion_mongo import ConexionMongo


class RepositorioNotificacionesMongo:
    def __init__(self) -> None:
        db = ConexionMongo().obtener_base_datos()
        self._col = db["NOTIFICACIONES"]

    def crear(self, notificacion: Dict[str, Any]) -> None:
        self._col.insert_one(notificacion)

    def crear_desde_dominio(self, supervisor_email: str, mensaje: str, autor, tipo_evento: str = "notificacion",
                            requerimiento_id: Optional[int] = None) -> None:
        doc = {
            "id": str(uuid4()),
            "supervisor_email": supervisor_email,
            "texto": mensaje,
            "autor_email": autor.email,
            "autor_nombre": autor.nombre,
            "fecha": datetime.now(),
            "tipo_evento": tipo_evento,
            "requerimiento_id": requerimiento_id,
            "leida": False
        }
        self.crear(doc)

    def listar_por_supervisor(self, supervisor_email: str, solo_no_leidas: bool = False) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {"supervisor_email": supervisor_email}
        if solo_no_leidas:
            filtro["leida"] = False
        return list(self._col.find(filtro, {"_id": 0}).sort("fecha", -1))

    def marcar_leida(self, supervisor_email: str, notificacion_id: str) -> bool:
        res = self._col.update_one(
            {"id": notificacion_id, "supervisor_email": supervisor_email},
            {"$set": {"leida": True}}
        )
        return res.matched_count == 1
    
    
    