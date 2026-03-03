from pymongo import MongoClient
from pymongo.database import Database


class ConexionMongo:
    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        nombre_base: str = "mesa_ayuda"
    ) -> None:
        self._cliente = MongoClient(uri)
        self._base_datos = self._cliente[nombre_base]

    def obtener_base_datos(self) -> Database:
        return self._base_datos
    