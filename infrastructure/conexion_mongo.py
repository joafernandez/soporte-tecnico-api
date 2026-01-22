from pymongo import MongoClient

class ConexionMongo:
    def __init__(self):
        self.cliente = MongoClient("mongodb://localhost:27017")
        self.base_datos = self.cliente["mesa_ayuda"]

    def obtener_base_datos(self):
        return self.base_datos
