from enum import Enum

class EstadoRequerimiento(Enum):
    """estados posibles de un requerimiento"""
    ABIERTO = "abierto"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"
    REABIERTO = "reabierto"


class TipoEvento(Enum):
    """tipos de eventos del sistema"""
    CREACION = "creacion"
    ASIGNACION = "asignacion"
    DERIVACION = "derivacion"
    RESOLUCION = "resolucion"
    REAPERTURA = "reapertura"
    CAMBIO_ESTADO = "cambio_estado"


class TipoSolicitud(Enum):
    """tipos de solicitud de servici"""
    ALTA_SERVICIO = "alta_servicio"
    BAJA_SERVICIO = "baja_servicio"