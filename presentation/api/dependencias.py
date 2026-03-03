from application.sistema import SistemaAyuda

# Instancia ÚNICA del sistema (estado compartido entre requests)
_sistema = SistemaAyuda()

def get_sistema() -> SistemaAyuda:
    return _sistema




