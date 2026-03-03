
class Servicio:
  
    #representa un servicio ofrecido por la cooperativa
    #actva o desactiva 
    
   
    
    _contador_id: int = 0
    
    def __init__(self, nombre: str, descripcion: str) -> None:
        Servicio._contador_id += 1
        self.id: int = Servicio._contador_id
        self.nombre: str = nombre
        self.descripcion: str = descripcion
        self.activo: bool = True
    
    def activar(self) -> None:
        """activa el servicio"""
        self.activo = True
    
    def desactivar(self) -> None:
        """desactiva el servicio"""
        self.activo = False
    
    def __str__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return f"Servicio: {self.nombre} ({estado})"