from domain.usuarios import Solicitante, Tecnico
from domain.requerimientos import Incidente, Solicitud
from domain.urgencias import UrgenciaCritica, UrgenciaImportante
from domain.enums import EstadoRequerimiento, TipoSolicitud
from domain.servicios import Servicio


def test_incidente_estado_inicial_y_prioridad():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Se cortó internet", sol, UrgenciaCritica(), None)

    assert inc.estado == EstadoRequerimiento.ABIERTO
    assert inc.tecnico_asignado is None
    assert inc.calcular_prioridad() == 10


def test_solicitud_prioridad_fija_5():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    serv = Servicio("Internet Banda Ancha", "desc")
    req = Solicitud("Alta servicio", sol, TipoSolicitud.ALTA_SERVICIO, serv)

    assert req.calcular_prioridad() == 5


def test_asignar_tecnico_pasa_a_en_proceso():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaImportante(), None)
    tec = Tecnico("Tec 1", "tec1@comunicarlos.com.ar", "1234")

    inc.asignar_tecnico(tec)

    assert inc.tecnico_asignado == tec
    assert inc.estado == EstadoRequerimiento.EN_PROCESO


def test_resolver_setea_estado_y_fecha_resolucion():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaImportante(), None)

    inc.resolver("Ok")

    assert inc.estado == EstadoRequerimiento.RESUELTO
    assert inc.fecha_resolucion is not None


def test_reabrir_solo_si_estaba_resuelto():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaImportante(), None)

    # Si no está RESUELTO, no cambia
    inc.reabrir()
    assert inc.estado == EstadoRequerimiento.ABIERTO

    # Si está RESUELTO, pasa a REABIERTO y borra fecha_resolucion
    inc.resolver("Ok")
    inc.reabrir()
    assert inc.estado == EstadoRequerimiento.REABIERTO
    assert inc.fecha_resolucion is None


def test_derivar_cambia_tecnico_asignado():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaImportante(), None)
    tec1 = Tecnico("Tec 1", "tec1@comunicarlos.com.ar", "1234")
    tec2 = Tecnico("Tec 2", "tec2@comunicarlos.com.ar", "1234")

    inc.asignar_tecnico(tec1)
    inc.derivar(tec2)

    assert inc.tecnico_asignado == tec2


def test_agregar_comentario_suma_uno():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaImportante(), None)

    inc.agregar_comentario("Comentario", sol)

    assert len(inc.comentarios) == 1
    assert inc.comentarios[0].texto == "Comentario"
    assert inc.comentarios[0].autor.email == "joa@test.com"
    
    