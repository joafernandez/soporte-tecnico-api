from infrastructure.conexion_mongo import ConexionMongo

class RepositorioUsuariosMongo:
    def __init__(self):
        conexion = ConexionMongo()
        self.coleccion = conexion.obtener_base_datos()["usuarios"]

    def guardar(self, tipo_usuario: str, usuario, password: str) -> None:
        """
        Guarda un usuario del dominio en Mongo.
        Guardamos también password para poder autenticar.
        """
        documento = {
            "id": usuario.id,
            "tipo_usuario": tipo_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "password": password
        }
        self.coleccion.insert_one(documento)

    def buscar_por_email(self, email: str):
        return self.coleccion.find_one({"email": email})
