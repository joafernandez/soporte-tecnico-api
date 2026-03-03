from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import List, Optional

from infrastructure.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from infrastructure.repositorio_incidentes_mongo import RepositorioIncidentesMongo
from infrastructure.repositorio_solicitudes_mongo import RepositorioSolicitudesMongo
from infrastructure.repositorio_notificaciones_mongo import RepositorioNotificacionesMongo

from domain.usuarios import Usuario, Solicitante, Operador, Tecnico, Supervisor
from domain.requerimientos import Requerimiento, Incidente, Solicitud
from domain.servicios import Servicio
from domain.urgencias import Urgencia
from domain.eventos import EventoFactory  # VOY A UTILIZAR PATRON !!! 
from domain.registros import Notificacion, Comentario  #uso patron
from domain.enums import TipoSolicitud


class SistemaAyuda:
    """
    facade principal del sistema Mesa de Ayuda
    Coordina todas las operaciones y patrones
    
    """

    def __init__(self) -> None:
        # listas
        self.usuarios: List[Usuario] = []
        self.requerimientos: List[Requerimiento] = []
        self.servicios: List[Servicio] = []
        self._inicializar_servicios()

        #  repositorios en mongo
        self.repositorio_usuarios = RepositorioUsuariosMongo()
        self.repositorio_incidentes = RepositorioIncidentesMongo()
        self.repositorio_solicitudes = RepositorioSolicitudesMongo()
        self.repositorio_notificaciones = RepositorioNotificacionesMongo()

    def _inicializar_servicios(self) -> None:
        self.servicios.append(Servicio("Telefonía Celular", "Servicio de telefonía móvil"))
        self.servicios.append(Servicio("Internet Banda Ancha", "Servicio de internet de alta velocidad"))
        self.servicios.append(Servicio("Televisión", "Servicio de televisión por cable"))

    # ==================== GESTIÓN DE USUARIOS ====================

    def registrar_usuario(self, tipo_usuario: str, nombre: str, email: str, password: str) -> Usuario:
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

        self.repositorio_usuarios.guardar(tipo_usuario, usuario, password)
        self.usuarios.append(usuario)
        return usuario

    def autenticar(self, email: str, password: str) -> Optional[Usuario]:
        usuario = self._buscar_usuario_por_email(email)
        if usuario and usuario.verificar_password(password):
            usuario.actualizar_ultimo_acceso()
            return usuario
        return None

    def _email_existe(self, email: str) -> bool:
        doc = self.repositorio_usuarios.buscar_por_email_interno(email)
        return doc is not None

    def _buscar_usuario_por_email(self, email: str) -> Optional[Usuario]:
        usuario_mem = next((u for u in self.usuarios if u.email == email), None)
        if usuario_mem:
            return usuario_mem

        doc = self.repositorio_usuarios.buscar_por_email_interno(email)
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
        if not isinstance(solicitante, Solicitante):
            raise ValueError("Solo los solicitantes pueden crear requerimientos")

        incidente = Incidente(descripcion, solicitante, urgencia, servicio)
        self.requerimientos.append(incidente)

        evento = EventoFactory.crear_evento_creacion(incidente, solicitante)
        incidente.agregar_evento(evento)

        self.repositorio_incidentes.guardar(incidente)
        return incidente

    def crear_solicitud(
        self,
        solicitante: Solicitante,
        descripcion: str,
        tipo_solicitud: TipoSolicitud,
        servicio: Servicio
    ) -> Solicitud:
        if not isinstance(solicitante, Solicitante):
            raise ValueError("Solo los solicitantes pueden crear requerimientos")

        solicitud = Solicitud(descripcion, solicitante, tipo_solicitud, servicio)
        self.requerimientos.append(solicitud)

        evento = EventoFactory.crear_evento_creacion(solicitud, solicitante)
        solicitud.agregar_evento(evento)

        self.repositorio_solicitudes.guardar(solicitud)
        return solicitud

    def asignar_tecnico(self, requerimiento: Requerimiento, tecnico: Tecnico, operador: Operador) -> None:
        if not isinstance(operador, Operador):
            raise ValueError("Solo los operadores pueden asignar técnicos")
        if not isinstance(tecnico, Tecnico):
            raise ValueError("Solo se puede asignar a técnicos")

        requerimiento.asignar_tecnico(tecnico)

        evento = EventoFactory.crear_evento_asignacion(requerimiento, tecnico, operador)
        requerimiento.agregar_evento(evento)

        if isinstance(requerimiento, Incidente):
            self.repositorio_incidentes.actualizar(requerimiento)
        elif isinstance(requerimiento, Solicitud):
            self.repositorio_solicitudes.actualizar(requerimiento)

        self._notificar_supervisores(
            operador,
            f"Operador {operador.nombre} asignó req #{requerimiento.id} a {tecnico.nombre}"
        )

    def derivar_requerimiento(self, requerimiento: Requerimiento, tecnico_origen: Tecnico, tecnico_destino: Tecnico) -> None:
        if not isinstance(tecnico_origen, Tecnico):
            raise ValueError("Solo los técnicos pueden derivar requerimientos")
        if requerimiento.tecnico_asignado != tecnico_origen:
            raise ValueError("Solo el técnico asignado puede derivar el requerimiento")

        requerimiento.derivar(tecnico_destino)

        evento = EventoFactory.crear_evento_derivacion(requerimiento, tecnico_origen, tecnico_destino)
        requerimiento.agregar_evento(evento)

        if isinstance(requerimiento, Incidente):
            self.repositorio_incidentes.actualizar(requerimiento)
        elif isinstance(requerimiento, Solicitud):
            self.repositorio_solicitudes.actualizar(requerimiento)

        self._notificar_supervisores(
            tecnico_origen,
            f"Técnico {tecnico_origen.nombre} derivó req #{requerimiento.id} a {tecnico_destino.nombre}"
        )

    def resolver_requerimiento(self, requerimiento: Requerimiento, tecnico: Tecnico, solucion: str) -> None:
        if not isinstance(tecnico, Tecnico):
            raise ValueError("Solo los técnicos pueden resolver requerimientos")
        if requerimiento.tecnico_asignado != tecnico:
            raise ValueError("Solo el técnico asignado puede resolver el requerimiento")

        requerimiento.resolver(solucion)

        evento = EventoFactory.crear_evento_resolucion(requerimiento, tecnico, solucion)
        requerimiento.agregar_evento(evento)

        requerimiento.agregar_comentario(f"Solución: {solucion}", tecnico)

        if isinstance(requerimiento, Incidente):
            self.repositorio_incidentes.actualizar(requerimiento)
        elif isinstance(requerimiento, Solicitud):
            self.repositorio_solicitudes.actualizar(requerimiento)

        self._notificar_supervisores(tecnico, f"Técnico {tecnico.nombre} resolvió req #{requerimiento.id}")

    def reabrir_requerimiento(self, requerimiento: Requerimiento, usuario: Usuario, motivo: str) -> None:
        if not isinstance(usuario, (Operador, Tecnico)):
            raise ValueError("Solo un Operador o un Técnico puede reabrir el requerimiento")

        requerimiento.reabrir()

        evento = EventoFactory.crear_evento_reapertura(requerimiento, usuario, motivo)
        requerimiento.agregar_evento(evento)

        requerimiento.agregar_comentario(f"Reabierto: {motivo}", usuario)

        if isinstance(requerimiento, Incidente):
            self.repositorio_incidentes.actualizar(requerimiento)
        elif isinstance(requerimiento, Solicitud):
            self.repositorio_solicitudes.actualizar(requerimiento)

        self._notificar_supervisores(usuario, f"{usuario.__class__.__name__} {usuario.nombre} reabrió req #{requerimiento.id}")

    def agregar_comentario(self, requerimiento: Requerimiento, usuario: Usuario, texto: str) -> Comentario:
        comentario = requerimiento.agregar_comentario(texto, usuario)

        if isinstance(requerimiento, Incidente):
            self.repositorio_incidentes.actualizar(requerimiento)
        elif isinstance(requerimiento, Solicitud):
            self.repositorio_solicitudes.actualizar(requerimiento)

        return comentario

    # ==================== CONSULTAS ====================

    def listar_requerimientos(self, usuario: Usuario) -> List[Requerimiento]:
        if isinstance(usuario, Solicitante):
            return [r for r in self.requerimientos if r.solicitante == usuario]
        if isinstance(usuario, (Operador, Supervisor)):
            return self.requerimientos
        if isinstance(usuario, Tecnico):
            return [r for r in self.requerimientos if r.tecnico_asignado == usuario]
        return []

    def listar_servicios(self) -> List[Servicio]:
        return [s for s in self.servicios if s.activo]

    # ==================== NOTIFICACIONES (API) ====================

    def listar_notificaciones(self, supervisor_email: str, solo_no_leidas: bool = False):
        return self.repositorio_notificaciones.listar_por_supervisor(supervisor_email, solo_no_leidas)

    def marcar_notificacion_leida(self, supervisor_email: str, notificacion_id: str) -> bool:
        return self.repositorio_notificaciones.marcar_leida(supervisor_email, notificacion_id)

    # ==================== OBSERVER PATTERN ==================== !!!!1 el que avisa

    def _notificar_supervisores(self, empleado: Usuario, mensaje: str) -> None:
        supervisores = [u for u in self.usuarios if isinstance(u, Supervisor)]

        for supervisor in supervisores:
            #  compara por email
            supervisa = any(s.email == empleado.email for s in supervisor.supervisados)
            if supervisa:
                # memoria
                notificacion = Notificacion(mensaje, empleado)
                supervisor.recibir_notificacion(notificacion)

                # Mongo  "verpendi"
                self.repositorio_notificaciones.crear({
                    "id": str(uuid4()),
                    "supervisor_email": supervisor.email,
                    "texto": mensaje,
                    "autor_email": empleado.email,
                    "autor_nombre": empleado.nombre,
                    "fecha": datetime.now().isoformat(),
                    "tipo_evento": "evento",
                    "requerimiento_id": None,
                    "leida": False
                })

    def asignar_supervisor(self, supervisor: Supervisor, empleado: Usuario) -> None:
        if not isinstance(supervisor, Supervisor):
            raise ValueError("El primer argumento debe ser un Supervisor")
        if not isinstance(empleado, (Operador, Tecnico)):
            raise ValueError("Solo se puede supervisar Operadores y Técnicos")
        supervisor.agregar_supervisado(empleado)
        
        
        
        
        
        