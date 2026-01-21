from fastapi import FastAPI
from presentation.api.routers.incidentes import router as incidentes_router

app = FastAPI(title="Mesa de Ayuda - Cooperativa Comunicarlos")

app.include_router(incidentes_router)

@app.get("/health")
def health():
    return {"status": "ok"}
