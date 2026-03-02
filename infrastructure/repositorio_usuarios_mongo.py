from infrastructure.conexion_mongo import ConexionMongo


class RepositorioUsuariosMongo:
    def __init__(self):
        conexion = ConexionMongo()
        self.coleccion = conexion.obtener_base_datos()["usuarios"]

    def guardar(self, tipo_usuario: str, usuario, password: str) -> None:
        documento = {
            "tipo_usuario": tipo_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "password": password
        }
        self.coleccion.update_one({"email": usuario.email}, {"$set": documento}, upsert=True)

    # ✅ PARA EL SISTEMA (con password)
    def buscar_por_email_interno(self, email: str):
        return self.coleccion.find_one({"email": email}, {"_id": 0})

    # ✅ PARA LA API (sin password)
    def buscar_por_email(self, email: str):
        return self.coleccion.find_one({"email": email}, {"_id": 0, "password": 0})

    def listar(self):
        return list(self.coleccion.find({}, {"_id": 0, "password": 0}).sort("email", 1))