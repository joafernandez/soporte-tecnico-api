from abc import ABC, abstractmethod
from datetime import datetime
import bcrypt
from typing import List, Optional
from domain.registros import Notificacion


class Usuario(ABC):
    """
    Clase base abstracta para todos los usuarios del sistema.
    
    Attributes:
        id: Identificador único
        nombre: Nombre completo
        email: Correo electrónico (único)
        password_hash: Contraseña hasheada con Bcrypt
        fecha_creacion: Timestamp de registro
        ultimo_acceso: Timestamp de último login
    """
    
    _contador_id: int = 0
    
    def __init__(self, nombre: str, email: str, password: str) -> None:
        Usuario._contador_id += 1
        self.id: int = Usuario._contador_id
        self.nombre: str = nombre
        self.email: str = email
        self.password_hash: str = self._hashear_password(password)
        self.fecha_creacion: datetime = datetime.now()
        self.ultimo_acceso: Optional[datetime] = None
    
    def _hashear_password(self, password: str) -> str:
        """Hashea la contraseña usando Bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def actualizar_ultimo_acceso(self) -> None:
        """Actualiza el timestamp de último acceso."""
        self.ultimo_acceso = datetime.now()
    
    @abstractmethod
    def puede_crear_requerimiento(self) -> bool:
        """Determina si el usuario puede crear requerimientos."""
        pass
    
    @abstractmethod
    def puede_asignar_tecnico(self) -> bool:
        """Determina si el usuario puede asignar técnicos."""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.nombre} ({self.email})"


class Solicitante(Usuario):
    """
    Usuario que crea requerimientos y ve solo los suyos.
    Puede usar cualquier email.
    """
    
    def puede_crear_requerimiento(self) -> bool:
        return True
    
    def puede_asignar_tecnico(self) -> bool:
        return False


class Operador(Usuario):
    """
    Usuario que asigna técnicos a requerimientos.
    Ve todos los requerimientos del sistema.
    Email debe ser @comunicarlos.com.ar
    """
    
    def __init__(self, nombre: str, email: str, password: str) -> None:
        if not email.endswith("@comunicarlos.com.ar"):
            raise ValueError("Email de operador debe ser @comunicarlos.com.ar")
        super().__init__(nombre, email, password)
    
    def puede_crear_requerimiento(self) -> bool:
        return False
    
    def puede_asignar_tecnico(self) -> bool:
        return True


class Tecnico(Usuario):
    """
    Usuario que resuelve requerimientos asignados.
    Puede derivar tickets a otros técnicos.
    Email debe ser @comunicarlos.com.ar
    """
    
    def __init__(self, nombre: str, email: str, password: str) -> None:
        if not email.endswith("@comunicarlos.com.ar"):
            raise ValueError("Email de técnico debe ser @comunicarlos.com.ar")
        super().__init__(nombre, email, password)
    
    def puede_crear_requerimiento(self) -> bool:
        return False
    
    def puede_asignar_tecnico(self) -> bool:
        return False


class Supervisor(Usuario):
    """
    Usuario que supervisa operadores y técnicos.
    Recibe notificaciones de sus supervisados (Observer Pattern).
    Email debe ser @comunicarlos.com.ar
    
    Attributes:
        supervisados: Lista de usuarios supervisados
        notificaciones: Lista de notificaciones recibidas
    """
    
    def __init__(self, nombre: str, email: str, password: str) -> None:
        if not email.endswith("@comunicarlos.com.ar"):
            raise ValueError("Email de supervisor debe ser @comunicarlos.com.ar")
        super().__init__(nombre, email, password)
        self.supervisados: List[Usuario] = []
        self.notificaciones: List[Notificacion] = []
    
    def puede_crear_requerimiento(self) -> bool:
        return False
    
    def puede_asignar_tecnico(self) -> bool:
        return False
    
    def agregar_supervisado(self, usuario: Usuario) -> None:
        """Agrega un usuario a la lista de supervisados."""
        if usuario not in self.supervisados:
            self.supervisados.append(usuario)
    
    def recibir_notificacion(self, notificacion: Notificacion) -> None:
        """Recibe una notificación (Observer Pattern)."""
        self.notificaciones.append(notificacion)
    
    def notificaciones_no_leidas(self) -> List[Notificacion]:
        """Retorna notificaciones no leídas."""
        return [n for n in self.notificaciones if not n.leida]