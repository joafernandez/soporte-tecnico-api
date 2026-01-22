from infrastructure.conexion_mongo import ConexionMongo

class RepositorioIncidentesMongo:
    def __init__(self):
        conexion = ConexionMongo()
        self.coleccion = conexion.obtener_base_datos()["incidentes"]

    def guardar(self, incidente) -> None:
        documento = {
            "id": incidente.id,
            "descripcion": incidente.descripcion,
            "urgencia": str(incidente.urgencia),
            "servicio": incidente.servicio.nombre if incidente.servicio else None,
            "solicitante_email": incidente.solicitante.email
        }
        self.coleccion.insert_one(documento)
