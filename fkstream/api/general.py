from fastapi import APIRouter
from fastapi.responses import RedirectResponse

general_router = APIRouter(tags=["General"])


@general_router.get("/")
async def root():
    """Redirige vers la page de configuration."""
    return RedirectResponse("/configure")


@general_router.get("/health")
async def health():
    """Endpoint de verification de l'etat de sante de l'application."""
    return {"status": "ok"}
