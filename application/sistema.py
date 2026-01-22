from typing import List, Optional

from infrastructure.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from infrastructure.repositorio_incidentes_mongo import RepositorioIncidentesMongo

from domain.usuarios import Usuario, Solicitante, Operador, Tecnico, Supervisor
from domain.requerimientos import Requerimiento, Incidente, Solicitud
from domain.servicios import Servicio
from domain.urgencias import Urgencia
from domain.eventos import EventoFactory
from domain.registros import Notificacion, Comentario
from domain.enums import TipoSolicitud


class SistemaAyuda:
    """
    Facade principal del sistema Mesa de Ayuda.
    Coordina todas las operaciones y patrones.

    Patrón: Facade
    """

    def __init__(self) -> None:
        # Listas en memoria (las dejamos porque el resto del sistema hoy trabaja con objetos del dominio)
        self.usuarios: List[Usuario] = []
        self.requerimientos: List[Requerimiento] = []
        self.servicios: List[Servicio] = []
        self._inicializar_servicios()

        # ✅ Repositorio Mongo para usuarios
        self.repositorio_usuarios = RepositorioUsuariosMongo()
        self.repositorio_incidentes = RepositorioIncidentesMongo()

    def _inicializar_servicios(self) -> None:
        """Crea los 3 servicios de la cooperativa."""
        self.servicios.append(Servicio("Telefonía Celular", "Servicio de telefonía móvil"))
        self.servicios.append(Servicio("Internet Banda Ancha", "Servicio de internet de alta velocidad"))
        self.servicios.append(Servicio("Televisión", "Servicio de televisión por cable"))

    # ==================== GESTIÓN DE USUARIOS ====================

    def registrar_usuario(self, tipo_usuario: str, nombre: str, email: str, password: str) -> Usuario:
        """Registra un nuevo usuario en el sistema."""
        if self._email_existe(email):
            raise ValueError(f"El email {email} ya está registrado")

        usuario: Optional[Usuario] = None

        if tipo_usuario == "solicitante":
            usuario = Solicitante(nombre, email, password)
        elif tipo_usuario == "operador":
            usuario = Operador(nombre, email, password)
        elif tipo_usuario == "tecnico":
            usuario = Tecnico(nombre, email, password)
        elif tipo_usuario == "supervisor":
            usuario = Supervisor(nombre, email, password)
        else:
            raise ValueError(f"Tipo de usuario inválido: {tipo_usuario}")

        # ✅ Guardar en Mongo (persistencia real)
        self.repositorio_usuarios.guardar(tipo_usuario, usuario, password)

        # ✅ Mantener también en memoria (para que el resto del sistema siga funcionando como hasta ahora)
        self.usuarios.append(usuario)

        return usuario

    def autenticar(self, email: str, password: str) -> Optional[Usuario]:
        """Autentica un usuario y actualiza su último acceso."""
        usuario = self._buscar_usuario_por_email(email)

        if usuario and usuario.verificar_password(password):
            usuario.actualizar_ultimo_acceso()
            return usuario

        return None

    def _email_existe(self, email: str) -> bool:
        """Verifica si un email ya está registrado (Mongo)."""
        doc = self.repositorio_usuarios.buscar_por_email(email)
        return doc is not None

    def _buscar_usuario_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca un usuario por email.
        Primero mira en memoria (si ya lo usamos en esta ejecución).
        Si no está, lo trae desde Mongo y reconstruye el objeto del dominio.
        """
        # 1) Cache en memoria
        usuario_mem = next((u for u in self.usuarios if u.email == email), None)
        if usuario_mem:
            return usuario_mem

        # 2) Mongo
        doc = self.repositorio_usuarios.buscar_por_email(email)
        if not doc:
            return None

        tipo_usuario = doc.get("tipo_usuario")
        nombre = doc.get("nombre")
        email_doc = doc.get("email")
        password_doc = doc.get("password")

        usuario: Optional[Usuario] = None

        if tipo_usuario == "solicitante":
            usuario = Solicitante(nombre, email_doc, password_doc)
        elif tipo_usuario == "operador":
            usuario = Operador(nombre, email_doc, password_doc)
        elif tipo_usuario == "tecnico":
            usuario = Tecnico(nombre, email_doc, password_doc)
        elif tipo_usuario == "supervisor":
            usuario = Supervisor(nombre, email_doc, password_doc)
        else:
            return None

        # guardo en memoria para reutilizar
        self.usuarios.append(usuario)
        return usuario

    # ==================== GESTIÓN DE REQUERIMIENTOS ====================
    def crear_incidente(
    self,
    solicitante: Solicitante,
    descripcion: str,
    urgencia: Urgencia,
    servicio: Optional[Servicio] = None
) -> Incidente:
     """Crea un incidente con urgencia específica."""
     if not isinstance(solicitante, Solicitante):
        raise ValueError("Solo los solicitantes pueden crear requerimientos")

     incidente = Incidente(descripcion, solicitante, urgencia, servicio)

    # 🔹 Guardar en memoria (como antes)
     self.requerimientos.append(incidente)

    # 🔹 Guardar en Mongo (persistencia real)
     self.repositorio_incidentes.guardar(incidente)

    # Crear evento de creación usando Factory
     evento = EventoFactory.crear_evento_creacion(incidente, solicitante)
     incidente.agregar_evento(evento)

     return incidente


    def crear_solicitud(
        self,
        solicitante: Solicitante,
        descripcion: str,
        tipo_solicitud: TipoSolicitud,
        servicio: Servicio
    ) -> Solicitud:
        """Crea una solicitud de alta/baja de servicio."""
        if not isinstance(solicitante, Solicitante):
            raise ValueError("Solo los solicitantes pueden crear requerimientos")

        solicitud = Solicitud(descripcion, solicitante, tipo_solicitud, servicio)
        self.requerimientos.append(solicitud)

        # Crear evento de creación usando Factory
        evento = EventoFactory.crear_evento_creacion(solicitud, solicitante)
        solicitud.agregar_evento(evento)

        return solicitud

    def asignar_tecnico(self, requerimiento: Requerimiento, tecnico: Tecnico, operador: Operador) -> None:
        """Asigna un técnico a un requerimiento."""
        if not isinstance(operador, Operador):
            raise ValueError("Solo los operadores pueden asignar técnicos")

        if not isinstance(tecnico, Tecnico):
            raise ValueError("Solo se puede asignar a técnicos")

        requerimiento.asignar_tecnico(tecnico)

        # Crear evento de asignación usando Factory
        evento = EventoFactory.crear_evento_asignacion(requerimiento, tecnico, operador)
        requerimiento.agregar_evento(evento)

        # Notificar supervisores (Observer Pattern)
        self._notificar_supervisores(
            operador,
            f"Operador {operador.nombre} asignó req #{requerimiento.id} a {tecnico.nombre}"
        )

    def derivar_requerimiento(self, requerimiento: Requerimiento, tecnico_origen: Tecnico, tecnico_destino: Tecnico) -> None:
        """Deriva un requerimiento a otro técnico."""
        if not isinstance(tecnico_origen, Tecnico):
            raise ValueError("Solo los técnicos pueden derivar requerimientos")

        if requerimiento.tecnico_asignado != tecnico_origen:
            raise ValueError("Solo el técnico asignado puede derivar el requerimiento")

        requerimiento.derivar(tecnico_destino)

        # Crear evento de derivación usando Factory
        evento = EventoFactory.crear_evento_derivacion(requerimiento, tecnico_origen, tecnico_destino)
        requerimiento.agregar_evento(evento)

        # Notificar supervisores (Observer Pattern)
        self._notificar_supervisores(
            tecnico_origen,
            f"Técnico {tecnico_origen.nombre} derivó req #{requerimiento.id} a {tecnico_destino.nombre}"
        )

    def resolver_requerimiento(self, requerimiento: Requerimiento, tecnico: Tecnico, solucion: str) -> None:
        """Resuelve un requerimiento."""
        if not isinstance(tecnico, Tecnico):
            raise ValueError("Solo los técnicos pueden resolver requerimientos")

        if requerimiento.tecnico_asignado != tecnico:
            raise ValueError("Solo el técnico asignado puede resolver el requerimiento")

        requerimiento.resolver(solucion)

        # Crear evento de resolución usando Factory
        evento = EventoFactory.crear_evento_resolucion(requerimiento, tecnico, solucion)
        requerimiento.agregar_evento(evento)

        # Agregar comentario con la solución
        requerimiento.agregar_comentario(f"Solución: {solucion}", tecnico)

        # Notificar supervisores (Observer Pattern)
        self._notificar_supervisores(tecnico, f"Técnico {tecnico.nombre} resolvió req #{requerimiento.id}")

    def reabrir_requerimiento(self, requerimiento: Requerimiento, usuario: Usuario, motivo: str) -> None:
        """Reabre un requerimiento resuelto."""
        if not isinstance(usuario, (Operador, Tecnico)):
            raise ValueError("Solo un Operador o un Técnico puede reabrir el requerimiento")

        requerimiento.reabrir()

        # Crear evento de reapertura usando Factory
        evento = EventoFactory.crear_evento_reapertura(requerimiento, usuario, motivo)
        requerimiento.agregar_evento(evento)

        # Agregar comentario con el motivo
        requerimiento.agregar_comentario(f"Reabierto: {motivo}", usuario)

    def agregar_comentario(self, requerimiento: Requerimiento, usuario: Usuario, texto: str) -> Comentario:
        """Agrega un comentario a un requerimiento."""
        return requerimiento.agregar_comentario(texto, usuario)

    # ==================== CONSULTAS ====================

    def listar_requerimientos(self, usuario: Usuario) -> List[Requerimiento]:
        """Lista requerimientos según el tipo de usuario."""
        if isinstance(usuario, Solicitante):
            # Solicitantes ven solo sus requerimientos
            return [r for r in self.requerimientos if r.solicitante == usuario]
        elif isinstance(usuario, (Operador, Supervisor)):
            # Operadores y supervisores ven todos
            return self.requerimientos
        elif isinstance(usuario, Tecnico):
            # Técnicos ven los asignados a ellos
            return [r for r in self.requerimientos if r.tecnico_asignado == usuario]

        return []

    def listar_servicios(self) -> List[Servicio]:
        """Lista todos los servicios disponibles."""
        return [s for s in self.servicios if s.activo]

    # ==================== OBSERVER PATTERN ====================

    def _notificar_supervisores(self, empleado: Usuario, mensaje: str) -> None:
        """Notifica a los supervisores cuando un empleado realiza una acción."""
        supervisores = [u for u in self.usuarios if isinstance(u, Supervisor)]

        for supervisor in supervisores:
            if empleado in supervisor.supervisados:
                notificacion = Notificacion(mensaje, empleado)
                supervisor.recibir_notificacion(notificacion)

    def asignar_supervisor(self, supervisor: Supervisor, empleado: Usuario) -> None:
        """Asigna un supervisor a un empleado (configura Observer)."""
        if not isinstance(supervisor, Supervisor):
            raise ValueError("El primer argumento debe ser un Supervisor")

        if not isinstance(empleado, (Operador, Tecnico)):
            raise ValueError("Solo se puede supervisar Operadores y Técnicos")

        supervisor.agregar_supervisado(empleado)
