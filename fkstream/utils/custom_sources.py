import asyncio
import orjson
import os
from pathlib import Path

from fkstream.utils.common_logger import logger
from fkstream.utils.models import settings


async def download_custom_sources(http_client):
    if not settings.CUSTOM_SOURCE_URL:
        logger.log("FKSTREAM", "CUSTOM_SOURCE_URL non configuré, pas de téléchargement")
        return {"animes": []}

    try:
        logger.log("FKSTREAM", f"Téléchargement de custom_sources depuis {settings.CUSTOM_SOURCE_URL}")
        response = await http_client.get(settings.CUSTOM_SOURCE_URL)
        response.raise_for_status()

        data = orjson.loads(response.content)

        Path(os.path.dirname(settings.CUSTOM_SOURCE_PATH)).mkdir(parents=True, exist_ok=True)

        with open(settings.CUSTOM_SOURCE_PATH, 'wb') as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        anime_count = len(data.get('animes', []))
        logger.log("FKSTREAM", f"Custom sources téléchargées et sauvegardées: {anime_count} anime(s)")

        return data
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de custom_sources: {e}")

        if os.path.exists(settings.CUSTOM_SOURCE_PATH):
            logger.log("FKSTREAM", "Utilisation du fichier custom_sources en cache")
            try:
                with open(settings.CUSTOM_SOURCE_PATH, 'rb') as f:
                    return orjson.loads(f.read())
            except Exception as e2:
                logger.error(f"Erreur lors de la lecture du cache custom_sources: {e2}")

        return {"animes": []}


async def periodic_custom_source_update(http_client, app_state):
    while True:
        try:
            await asyncio.sleep(settings.CUSTOM_SOURCE_INTERVAL)

            logger.log("FKSTREAM", "Mise à jour périodique de custom_sources")
            data = await download_custom_sources(http_client)
            app_state.custom_sources = data

        except asyncio.CancelledError:
            logger.log("FKSTREAM", "Tâche de mise à jour custom_sources annulée")
            break
        except Exception as e:
            logger.error(f"Erreur dans la tâche périodique custom_sources: {e}")


def load_custom_sources_from_cache():
    if os.path.exists(settings.CUSTOM_SOURCE_PATH):
        try:
            with open(settings.CUSTOM_SOURCE_PATH, 'rb') as f:
                data = orjson.loads(f.read())
            anime_count = len(data.get('animes', []))
            logger.log("FKSTREAM", f"Custom sources chargées depuis le cache: {anime_count} anime(s)")
            return data
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache custom_sources: {e}")

    return {"animes": []}
