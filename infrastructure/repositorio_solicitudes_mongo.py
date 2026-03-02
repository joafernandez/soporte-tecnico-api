from infrastructure.conexion_mongo import ConexionMongo

class RepositorioSolicitudesMongo:

    def __init__(self):
        conexion = ConexionMongo()
        self.collection = conexion.obtener_base_datos()["solicitudes"]

    def guardar(self, solicitud):
        doc = {
            "id": solicitud.id,
            "descripcion": solicitud.descripcion,
            "tipo_solicitud": solicitud.tipo_solicitud.value,
            "servicio": solicitud.servicio.nombre,
            "solicitante_email": solicitud.solicitante.email
        }
        self.collection.insert_one(doc)
