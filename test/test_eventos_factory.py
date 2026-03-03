from domain.usuarios import Solicitante, Operador, Tecnico
from domain.requerimientos import Incidente
from domain.urgencias import UrgenciaCritica
from domain.eventos import EventoFactory
from domain.enums import TipoEvento


def test_evento_creacion():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaCritica(), None)

    ev = EventoFactory.crear_evento_creacion(inc, sol)

    assert ev.tipo == TipoEvento.CREACION
    assert f"#{inc.id}" in ev.texto
    assert ev.autor.email == "joa@test.com"


def test_evento_asignacion():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    op = Operador("Op 2", "op2@comunicarlos.com.ar", "1234")
    tec = Tecnico("Tec 1", "tec1@comunicarlos.com.ar", "1234")
    inc = Incidente("Incidente", sol, UrgenciaCritica(), None)

    ev = EventoFactory.crear_evento_asignacion(inc, tec, op)

    assert ev.tipo == TipoEvento.ASIGNACION
    assert "asignado" in ev.texto.lower()
    assert ev.autor.email == "op2@comunicarlos.com.ar"


def test_evento_derivacion():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    tec1 = Tecnico("Tec 1", "tec1@comunicarlos.com.ar", "1234")
    tec2 = Tecnico("Tec 2", "tec2@comunicarlos.com.ar", "1234")
    inc = Incidente("Incidente", sol, UrgenciaCritica(), None)

    ev = EventoFactory.crear_evento_derivacion(inc, tec1, tec2)

    assert ev.tipo == TipoEvento.DERIVACION
    assert tec1.nombre in ev.texto
    assert tec2.nombre in ev.texto
    assert ev.autor.email == "tec1@comunicarlos.com.ar"


def test_evento_resolucion():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    tec = Tecnico("Tec 1", "tec1@comunicarlos.com.ar", "1234")
    inc = Incidente("Incidente", sol, UrgenciaCritica(), None)

    ev = EventoFactory.crear_evento_resolucion(inc, tec, "Se reinició el módem")

    assert ev.tipo == TipoEvento.RESOLUCION
    assert "resuelto" in ev.texto.lower()
    assert ev.autor.email == "tec1@comunicarlos.com.ar"


def test_evento_reapertura():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaCritica(), None)

    ev = EventoFactory.crear_evento_reapertura(inc, sol, "Volvió a fallar")

    assert ev.tipo == TipoEvento.REAPERTURA
    assert "reabierto" in ev.texto.lower()
    assert ev.autor.email == "joa@test.com"


def test_evento_cambio_estado():
    sol = Solicitante("Joa", "joa@test.com", "1234")
    inc = Incidente("Incidente", sol, UrgenciaCritica(), None)

    ev = EventoFactory.crear_evento_cambio_estado(inc, sol, "abierto", "en_proceso")

    assert ev.tipo == TipoEvento.CAMBIO_ESTADO
    assert "cambió" in ev.texto.lower()
    assert ev.autor.email == "joa@test.com"
    
    