import pytest
from domain.usuarios import Solicitante, Operador, Tecnico, Supervisor


def test_solicitante_permisos():
    u = Solicitante("Joa", "joa@test.com", "1234")
    assert u.puede_crear_requerimiento() is True
    assert u.puede_asignar_tecnico() is False


def test_operador_email_debe_ser_comunicarlos():
    with pytest.raises(ValueError):
        Operador("Op", "op@gmail.com", "1234")

    ok = Operador("Op 2", "op2@comunicarlos.com.ar", "1234")
    assert ok.puede_asignar_tecnico() is True
    assert ok.puede_crear_requerimiento() is False


def test_tecnico_email_debe_ser_comunicarlos():
    with pytest.raises(ValueError):
        Tecnico("Tec", "tec@gmail.com", "1234")

    ok = Tecnico("Tec 1", "tec1@comunicarlos.com.ar", "1234")
    assert ok.puede_asignar_tecnico() is False
    assert ok.puede_crear_requerimiento() is False


def test_supervisor_email_debe_ser_comunicarlos():
    with pytest.raises(ValueError):
        Supervisor("Sup", "sup@gmail.com", "1234")

    ok = Supervisor("Sup 1", "sup1@comunicarlos.com.ar", "1234")
    assert ok.puede_asignar_tecnico() is False
    assert ok.puede_crear_requerimiento() is False
    
    