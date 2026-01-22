from infrastructure.conexion_mongo import ConexionMongo

class RepositorioUsuariosMongo:
    def __init__(self):
        conexion = ConexionMongo()
        self.coleccion = conexion.obtener_base_datos()["usuarios"]

    def guardar(self, usuario):
        documento = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "tipo": usuario.tipo
        }
        self.coleccion.insert_one(documento)

    def buscar_por_email(self, email):
        return self.coleccion.find_one({"email": email})
