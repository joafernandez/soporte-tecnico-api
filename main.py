"""
Ejemplo de uso del Sistema de Mesa de Ayuda.
Demuestra todos los patrones y funcionalidades.
"""

from application.sistema import SistemaAyuda
from domain.urgencias import UrgenciaCritica, UrgenciaImportante, UrgenciaMenor
from domain.enums import TipoSolicitud


def main():
    """Función principal de demostración."""
    
    # ==================== INICIALIZACIÓN ====================
    print("=" * 60)
    print("SISTEMA DE MESA DE AYUDA - COOPERATIVA COMUNICARLOS")
    print("=" * 60)
    
    sistema = SistemaAyuda()
    
    # ==================== REGISTRO DE USUARIOS ====================
    print("\n[1] REGISTRANDO USUARIOS...")
    
    # Solicitantes (cualquier email)
    solicitante1 = sistema.registrar_usuario("solicitante", "Juan Pérez", "juan@gmail.com", "password123")
    solicitante2 = sistema.registrar_usuario("solicitante", "María González", "maria@hotmail.com", "password456")
    print(f"✓ {solicitante1}")
    print(f"✓ {solicitante2}")
    
    # Operadores (@comunicarlos.com.ar)
    operador1 = sistema.registrar_usuario("operador", "Carlos Ruiz", "carlos@comunicarlos.com.ar", "op123")
    print(f"✓ {operador1}")
    
    # Técnicos (@comunicarlos.com.ar)
    tecnico1 = sistema.registrar_usuario("tecnico", "Laura Díaz", "laura@comunicarlos.com.ar", "tec123")
    tecnico2 = sistema.registrar_usuario("tecnico", "Pedro Fernández", "pedro@comunicarlos.com.ar", "tec456")
    print(f"✓ {tecnico1}")
    print(f"✓ {tecnico2}")
    
    # Supervisor (@comunicarlos.com.ar)
    supervisor1 = sistema.registrar_usuario("supervisor", "Ana Martínez", "ana@comunicarlos.com.ar", "sup123")
    print(f"✓ {supervisor1}")
    
    # ==================== CONFIGURAR OBSERVER PATTERN ====================
    print("\n[2] CONFIGURANDO SUPERVISIÓN (Observer Pattern)...")
    
    sistema.asignar_supervisor(supervisor1, operador1)
    sistema.asignar_supervisor(supervisor1, tecnico1)
    sistema.asignar_supervisor(supervisor1, tecnico2)
    print(f"✓ {supervisor1.nombre} supervisa a:")
    for empleado in supervisor1.supervisados:
        print(f"  - {empleado.nombre}")
    
    # ==================== AUTENTICACIÓN ====================
    print("\n[3] AUTENTICACIÓN...")
    
    usuario_autenticado = sistema.autenticar("juan@gmail.com", "password123")
    if usuario_autenticado:
        print(f"✓ Login exitoso: {usuario_autenticado.nombre}")
        print(f"  Último acceso: {usuario_autenticado.ultimo_acceso}")
    
    # ==================== CREAR INCIDENTES (Strategy Pattern) ====================
    print("\n[4] CREANDO INCIDENTES (Strategy Pattern)...")
    
    servicios = sistema.listar_servicios()
    servicio_internet = servicios[1]  # Internet Banda Ancha
    servicio_telefonia = servicios[0]  # Telefonía Celular
    
    # Incidente CRÍTICO
    incidente1 = sistema.crear_incidente(
        solicitante1,
        "Sin conexión a internet desde hace 3 horas, afecta trabajo remoto",
        UrgenciaCritica(),
        servicio_internet
    )
    print(f"✓ {incidente1}")
    print(f"  Urgencia: Crítica - Prioridad: {incidente1.calcular_prioridad()}")
    
    # Incidente IMPORTANTE
    incidente2 = sistema.crear_incidente(
        solicitante2,
        "Velocidad de internet muy lenta, no puedo hacer videollamadas",
        UrgenciaImportante(),
        servicio_internet
    )
    print(f"✓ {incidente2}")
    print(f"  Urgencia: Importante - Prioridad: {incidente2.calcular_prioridad()}")
    
    # Incidente MENOR
    incidente3 = sistema.crear_incidente(
        solicitante1,
        "El teléfono tiene interferencias ocasionales",
        UrgenciaMenor(),
        servicio_telefonia
    )
    print(f"✓ {incidente3}")
    print(f"  Urgencia: Menor - Prioridad: {incidente3.calcular_prioridad()}")
    
    # ==================== CREAR SOLICITUDES ====================
    print("\n[5] CREANDO SOLICITUDES...")
    
    servicio_tv = servicios[2]  # Televisión
    
    solicitud1 = sistema.crear_solicitud(
        solicitante2,
        "Quiero dar de alta el servicio de televisión",
        TipoSolicitud.ALTA_SERVICIO,
        servicio_tv
    )
    print(f"✓ {solicitud1}")
    print(f"  Tipo: Alta de servicio - Prioridad: {solicitud1.calcular_prioridad()}")
    
    # ==================== ASIGNAR TÉCNICOS ====================
    print("\n[6] ASIGNANDO TÉCNICOS (Operador)...")
    
    sistema.asignar_tecnico(incidente1, tecnico1, operador1)
    print(f"✓ Incidente #{incidente1.id} asignado a {tecnico1.nombre}")
    print(f"  Estado: {incidente1.estado.value}")
    
    sistema.asignar_tecnico(incidente2, tecnico2, operador1)
    print(f"✓ Incidente #{incidente2.id} asignado a {tecnico2.nombre}")
    
    # ==================== VERIFICAR NOTIFICACIONES (Observer) ====================
    print("\n[7] NOTIFICACIONES DEL SUPERVISOR (Observer Pattern)...")
    
    notificaciones = supervisor1.notificaciones_no_leidas()
    print(f"✓ {supervisor1.nombre} tiene {len(notificaciones)} notificaciones:")
    for notif in notificaciones:
        print(f"  [{notif.fecha.strftime('%H:%M:%S')}] {notif.texto}")
    
    # ==================== AGREGAR COMENTARIOS ====================
    print("\n[8] AGREGANDO COMENTARIOS...")
    
    comentario1 = sistema.agregar_comentario(
        incidente1,
        tecnico1,
        "Revisando la conexión del módem, parece un problema de configuración"
    )
    print(f"✓ Comentario agregado: {comentario1}")
    
    comentario2 = sistema.agregar_comentario(
        incidente1,
        solicitante1,
        "¿Cuánto tiempo estimado de resolución?"
    )
    print(f"✓ Comentario agregado: {comentario2}")
    
    # ==================== DERIVAR REQUERIMIENTO ====================
    print("\n[9] DERIVANDO REQUERIMIENTO (Técnico)...")
    
    sistema.derivar_requerimiento(incidente2, tecnico2, tecnico1)
    print(f"✓ Incidente #{incidente2.id} derivado de {tecnico2.nombre} a {tecnico1.nombre}")
    print(f"  Técnico asignado actual: {incidente2.tecnico_asignado.nombre}")
    
    # ==================== RESOLVER REQUERIMIENTO ====================
    print("\n[10] RESOLVIENDO REQUERIMIENTO (Técnico)...")
    
    sistema.resolver_requerimiento(
        incidente1,
        tecnico1,
        "Módem reconfigurado y señal estabilizada. Problema resuelto."
    )
    print(f"✓ Incidente #{incidente1.id} resuelto")
    print(f"  Estado: {incidente1.estado.value}")
    print(f"  Fecha resolución: {incidente1.fecha_resolucion.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ==================== REABRIR REQUERIMIENTO ====================
    print("\n[11] REABRIENDO REQUERIMIENTO (Solicitante)...")
    
    sistema.reabrir_requerimiento(
        incidente1,
        operador1,
        "El problema volvió a ocurrir después de 2 horas"
    )
    print(f"✓ Incidente #{incidente1.id} reabierto")
    print(f"  Estado: {incidente1.estado.value}")
    
    # ==================== HISTORIAL DE EVENTOS (Factory Pattern) ====================
    print("\n[12] HISTORIAL DE EVENTOS (Factory Pattern)...")
    
    print(f"✓ Incidente #{incidente1.id} tiene {len(incidente1.eventos)} eventos:")
    for evento in incidente1.eventos:
        print(f"  [{evento.tipo.value}] {evento}")
    
    # ==================== LISTAR REQUERIMIENTOS POR USUARIO ====================
    print("\n[13] LISTADO DE REQUERIMIENTOS...")
    
    # Solicitante ve solo los suyos
    req_solicitante = sistema.listar_requerimientos(solicitante1)
    print(f"✓ {solicitante1.nombre} ve {len(req_solicitante)} requerimientos:")
    for req in req_solicitante:
        print(f"  - Req #{req.id}: {req.estado.value} (Prioridad: {req.calcular_prioridad()})")
    
    # Operador ve todos
    req_operador = sistema.listar_requerimientos(operador1)
    print(f"✓ {operador1.nombre} ve {len(req_operador)} requerimientos:")
    for req in req_operador:
        print(f"  - Req #{req.id}: {req.estado.value} (Prioridad: {req.calcular_prioridad()})")
    
    # Técnico ve solo los asignados
    req_tecnico = sistema.listar_requerimientos(tecnico1)
    print(f"✓ {tecnico1.nombre} ve {len(req_tecnico)} requerimientos:")
    for req in req_tecnico:
        print(f"  - Req #{req.id}: {req.estado.value} (Prioridad: {req.calcular_prioridad()})")
    
    # ==================== CAMBIO DE URGENCIA EN RUNTIME (Strategy) ====================
    print("\n[14] CAMBIO DE URGENCIA EN RUNTIME (Strategy Pattern)...")
    
    print(f"✓ Incidente #{incidente3.id}:")
    print(f"  Urgencia inicial: {incidente3.urgencia.get_nombre()} - Prioridad: {incidente3.calcular_prioridad()}")
    
    incidente3.cambiar_urgencia(UrgenciaCritica())
    print(f"  Urgencia actualizada: {incidente3.urgencia.get_nombre()} - Prioridad: {incidente3.calcular_prioridad()}")
    
    # ==================== NOTIFICACIONES FINALES ====================
    print("\n[15] NOTIFICACIONES FINALES DEL SUPERVISOR...")
    
    notificaciones_finales = supervisor1.notificaciones_no_leidas()
    print(f"✓ {supervisor1.nombre} tiene {len(notificaciones_finales)} notificaciones totales:")
    for i, notif in enumerate(notificaciones_finales, 1):
        print(f"  {i}. [{notif.fecha.strftime('%H:%M:%S')}] {notif.texto}")
    
    # Marcar todas como leídas
    for notif in notificaciones_finales:
        notif.marcar_como_leida()
    
    print(f"\n✓ Todas las notificaciones marcadas como leídas")
    print(f"  Notificaciones pendientes: {len(supervisor1.notificaciones_no_leidas())}")
    
    # ==================== RESUMEN FINAL ====================
    print("\n" + "=" * 60)
    print("RESUMEN DEL SISTEMA")
    print("=" * 60)
    print(f"Usuarios registrados: {len(sistema.usuarios)}")
    print(f"  - Solicitantes: {len([u for u in sistema.usuarios if u.__class__.__name__ == 'Solicitante'])}")
    print(f"  - Operadores: {len([u for u in sistema.usuarios if u.__class__.__name__ == 'Operador'])}")
    print(f"  - Técnicos: {len([u for u in sistema.usuarios if u.__class__.__name__ == 'Tecnico'])}")
    print(f"  - Supervisores: {len([u for u in sistema.usuarios if u.__class__.__name__ == 'Supervisor'])}")
    print(f"\nRequerimientos totales: {len(sistema.requerimientos)}")
    print(f"  - Incidentes: {len([r for r in sistema.requerimientos if r.__class__.__name__ == 'Incidente'])}")
    print(f"  - Solicitudes: {len([r for r in sistema.requerimientos if r.__class__.__name__ == 'Solicitud'])}")
    print(f"\nServicios disponibles: {len(sistema.listar_servicios())}")
    
    print("\n" + "=" * 60)
    print("PATRONES IMPLEMENTADOS:")
    print("=" * 60)
    print("✓ Strategy Pattern: Urgencias (Crítica/Importante/Menor)")
    print("✓ Observer Pattern: Supervisor recibe notificaciones")
    print("✓ Factory Pattern: EventoFactory crea eventos")
    print("✓ Facade Pattern: SistemaAyuda coordina todo")
    print("✓ Herencia: Usuario (4), Requerimiento (2), Registro (3)")
    print("✓ Composición: Requerimiento HAS-A Comentarios/Eventos")
    print("=" * 60)


if __name__ == "__main__":
    main()