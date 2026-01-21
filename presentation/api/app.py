from fastapi import FastAPI

from presentation.api.routers.incidentes import router as incidentes_router
from presentation.api.routers.usuarios import router as usuarios_router

app = FastAPI(title="Mesa de Ayuda - Cooperativa Comunicarlos")

# routers
app.include_router(usuarios_router)
app.include_router(incidentes_router)

@app.get("/health")
def health():
    return {"status": "ok"}
