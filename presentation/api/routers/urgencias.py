from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/urgencias", tags=["Urgencias"])

@router.get("/", response_model=List[str])
def listar_urgencias():
    return ["critica", "importante", "menor"]