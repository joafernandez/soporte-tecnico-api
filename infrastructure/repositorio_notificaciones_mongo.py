from typing import Any, Dict, List
from pymongo.database import Database


class RepositorioNotificacionesMongo:
    def __init__(self, db: Database) -> None:
        self._col = db["notificaciones"]

    def crear(self, notificacion: Dict[str, Any]) -> None:
        self._col.insert_one(notificacion)

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
    
    