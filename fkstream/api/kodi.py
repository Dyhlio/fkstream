import secrets
import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from fkstream.utils.common_logger import logger
from fkstream.utils.config_validator import validate_config
from fkstream.utils.database import (
    create_kodi_setup_code,
    associate_kodi_manifest,
    get_kodi_manifest,
)

kodi_router = APIRouter(prefix="/kodi", tags=["Kodi"])

KODI_SETUP_CODE_TTL = 300  # 5 minutes


class GenerateSetupCodeRequest(BaseModel):
    secret_string: str = ""


class AssociateManifestRequest(BaseModel):
    code: str = Field(min_length=4, max_length=16)
    manifest_url: str


@kodi_router.post("/generate_setup_code")
async def generate_setup_code(request: Request, body: GenerateSetupCodeRequest = GenerateSetupCodeRequest()):
    """
    Génère un code d'appairage pour Kodi.
    Le code est valide pendant 5 minutes.
    """
    for _ in range(8):
        code = secrets.token_hex(4).upper()
        nonce = secrets.token_hex(8)
        created_at = time.time()
        expires_at = created_at + KODI_SETUP_CODE_TTL

        success = await create_kodi_setup_code(code, nonce, created_at, expires_at)
        if success:
            base_url = str(request.base_url).rstrip("/")
            configure_url = f"{base_url}/configure?kodi_code={code}"

            logger.info(f"Code Kodi généré: {code} (expire dans {KODI_SETUP_CODE_TTL}s)")
            return {
                "code": code,
                "configure_url": configure_url,
                "expires_in": KODI_SETUP_CODE_TTL,
            }

    raise HTTPException(status_code=500, detail="Impossible de générer un code unique")


@kodi_router.post("/associate_manifest")
async def associate_manifest(body: AssociateManifestRequest):
    """
    Associe une configuration utilisateur à un code d'appairage Kodi.
    Appelé depuis la page de configuration après que l'utilisateur a rempli ses paramètres.
    """
    try:
        parts = body.manifest_url.rstrip("/").split("/")
        manifest_idx = None
        for i, part in enumerate(parts):
            if part == "manifest.json":
                manifest_idx = i
                break

        if manifest_idx is None or manifest_idx < 1:
            raise ValueError("Format d'URL manifest invalide")

        b64config = parts[manifest_idx - 1]

        config = validate_config(b64config)
        if not config:
            raise ValueError("Configuration invalide")

    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail=f"URL manifest invalide: {e}")

    success = await associate_kodi_manifest(body.code, b64config)
    if not success:
        raise HTTPException(status_code=404, detail="Code introuvable ou expiré")

    logger.info(f"Code Kodi {body.code} associé avec succès")
    return {"status": "ok"}


@kodi_router.get("/get_manifest/{code}")
async def get_manifest_endpoint(code: str):
    """
    Récupère la configuration associée à un code d'appairage Kodi.
    Appelé par l'addon Kodi qui interroge périodiquement cet endpoint.
    """
    result = await get_kodi_manifest(code)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Configuration non prête ou code expiré",
        )

    logger.info(f"Configuration Kodi récupérée pour le code {code}")
    return {"secret_string": result["b64config"]}
