from infrastructure.conexion_mongo import ConexionMongo


class RepositorioSolicitudesMongo:
    def __init__(self):
        conexion = ConexionMongo()
        self.collection = conexion.obtener_base_datos()["solicitudes"]

    # ==================== CREATE / UPSERT ====================

    def guardar(self, solicitud) -> None:
        doc = {
            "id": solicitud.id,
            "descripcion": solicitud.descripcion,
            "tipo_solicitud": solicitud.tipo_solicitud.value,
            "servicio": solicitud.servicio.nombre,
            "solicitante_email": solicitud.solicitante.email,
            "comentarios": [
                {
                    "texto": c.texto,
                    "autor_email": c.autor.email,
                    "autor_nombre": c.autor.nombre,
                    "fecha": c.fecha.isoformat(),
                }
                for c in solicitud.comentarios
            ],
            "eventos": [
                {
                    "texto": e.texto,
                    "autor_email": e.autor.email,
                    "autor_nombre": e.autor.nombre,
                    "fecha": e.fecha.isoformat(),
                    "tipo": str(e.tipo),
                }
                for e in solicitud.eventos
            ],
        }
        self.collection.update_one({"id": solicitud.id}, {"$set": doc}, upsert=True)

    # ==================== UPDATE ====================

    def actualizar(self, solicitud) -> None:
        self.collection.update_one(
            {"id": solicitud.id},
            {"$set": {
                "descripcion": solicitud.descripcion,
                "tipo_solicitud": solicitud.tipo_solicitud.value,
                "servicio": solicitud.servicio.nombre,
                "solicitante_email": solicitud.solicitante.email,
                "comentarios": [
                    {
                        "texto": c.texto,
                        "autor_email": c.autor.email,
                        "autor_nombre": c.autor.nombre,
                        "fecha": c.fecha.isoformat(),
                    }
                    for c in solicitud.comentarios
                ],
                "eventos": [
                    {
                        "texto": e.texto,
                        "autor_email": e.autor.email,
                        "autor_nombre": e.autor.nombre,
                        "fecha": e.fecha.isoformat(),
                        "tipo": str(e.tipo),
                    }
                    for e in solicitud.eventos
                ],
            }}
        )

    # ==================== READ (GET) ====================

    def buscar_por_id(self, solicitud_id: int):
        return self.collection.find_one({"id": solicitud_id}, {"_id": 0})

    def listar(self):
        return list(self.collection.find({}, {"_id": 0}).sort("id", 1))
    