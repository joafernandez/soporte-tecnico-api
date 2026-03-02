from fastapi import FastAPI

from presentation.api.routers.incidentes import router as incidentes_router
from presentation.api.routers.usuarios import router as usuarios_router
from presentation.api.routers.solicitudes import router as router_solicitudes #tercero



app = FastAPI(title="Mesa de Ayuda - Cooperativa Comunicarlos")

# routers
app.include_router(usuarios_router)
app.include_router(incidentes_router)
app.include_router(router_solicitudes) # el tercero que voy agreganod

@app.get("/health")
def health():
    return {"status": "ok"}
