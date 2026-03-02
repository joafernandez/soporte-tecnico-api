from infrastructure.conexion_mongo import ConexionMongo


class RepositorioIncidentesMongo:
    def __init__(self):
        conexion = ConexionMongo()
        self.coleccion = conexion.obtener_base_datos()["incidentes"]

    # ==================== CREATE / UPSERT ====================

    def guardar(self, incidente) -> None:
        documento = {
            "id": incidente.id,
            "descripcion": incidente.descripcion,
            "urgencia": incidente.urgencia.get_nombre(),
            "servicio": incidente.servicio.nombre if incidente.servicio else None,
            "solicitante_email": incidente.solicitante.email,
            "comentarios": [
                {
                    "texto": c.texto,
                    "autor_email": c.autor.email,
                    "autor_nombre": c.autor.nombre,
                    "fecha": c.fecha.isoformat(),
                }
                for c in incidente.comentarios
            ],
            "eventos": [
                {
                    "texto": e.texto,
                    "autor_email": e.autor.email,
                    "autor_nombre": e.autor.nombre,
                    "fecha": e.fecha.isoformat(),
                    "tipo": str(e.tipo),
                }
                for e in incidente.eventos
            ],
        }
        self.coleccion.update_one({"id": incidente.id}, {"$set": documento}, upsert=True)

    # ==================== UPDATE ====================

    def actualizar(self, incidente) -> None:
        self.coleccion.update_one(
            {"id": incidente.id},
            {"$set": {
                "descripcion": incidente.descripcion,
                "urgencia": incidente.urgencia.get_nombre(),
                "servicio": incidente.servicio.nombre if incidente.servicio else None,
                "solicitante_email": incidente.solicitante.email,
                "comentarios": [
                    {
                        "texto": c.texto,
                        "autor_email": c.autor.email,
                        "autor_nombre": c.autor.nombre,
                        "fecha": c.fecha.isoformat(),
                    }
                    for c in incidente.comentarios
                ],
                "eventos": [
                    {
                        "texto": e.texto,
                        "autor_email": e.autor.email,
                        "autor_nombre": e.autor.nombre,
                        "fecha": e.fecha.isoformat(),
                        "tipo": str(e.tipo),
                    }
                    for e in incidente.eventos
                ],
            }}
        )

    def agregar_comentario_por_id(self, incidente_id: int, comentario_doc: dict) -> None:
        self.coleccion.update_one(
            {"id": incidente_id},
            {"$push": {"comentarios": comentario_doc}}
        )

    # ==================== READ (GET) ====================

    def buscar_por_id(self, incidente_id: int):
        return self.coleccion.find_one({"id": incidente_id}, {"_id": 0})

    def listar(self):
        return list(self.coleccion.find({}, {"_id": 0}).sort("id", 1))
    