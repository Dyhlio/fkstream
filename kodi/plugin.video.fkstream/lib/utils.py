import requests
from urllib.parse import quote as url_quote

try:
    import xbmcaddon
    import xbmc

    ADDON = xbmcaddon.Addon()

    def get_setting(key):
        return ADDON.getSetting(key)

    def get_addon_name():
        return ADDON.getAddonInfo("name")

    def log(msg, level=xbmc.LOGINFO):
        xbmc.log(f"[FKStream] {msg}", level)

except ImportError:
    # Fallback pour les tests hors Kodi
    def get_setting(key):
        return ""

    def get_addon_name():
        return "FKStream"

    def log(msg, level=0):
        print(f"[FKStream] {msg}")


def get_base_url():
    """Retourne l'URL de base du serveur FKStream."""
    url = get_setting("base_url").strip().rstrip("/")
    return url


def get_secret_string():
    """Retourne la clé de configuration (b64config)."""
    return get_setting("secret_string").strip()


def is_configured():
    """Vérifie si l'addon est configuré (base_url + secret_string)."""
    return bool(get_base_url()) and bool(get_secret_string())


def api_get(path, timeout=15):
    """
    Effectue un GET vers le serveur FKStream.
    Retourne le JSON de la réponse ou None en cas d'erreur.
    """
    base = get_base_url()
    if not base:
        log("Erreur: URL du serveur non configurée")
        return None

    url = f"{base}{path}"
    log(f"API GET: {url}")

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        log(f"Timeout sur {url}")
        return None
    except requests.exceptions.RequestException as e:
        log(f"Erreur requête {url}: {e}")
        return None
    except ValueError:
        log(f"Réponse non-JSON depuis {url}")
        return None


def build_catalog_url(search=None, genre=None, sort=None):
    """Construit le chemin d'URL pour le catalogue."""
    secret = get_secret_string()
    prefix = f"/{secret}" if secret else ""
    parts = []
    if search:
        parts.append(f"search={url_quote(search, safe='')}")
    if genre:
        parts.append(f"genre={url_quote(genre, safe='')}")
    if sort:
        parts.append(f"sort={url_quote(sort, safe='')}")

    if parts:
        return f"{prefix}/catalog/anime/fankai_catalog/{'&'.join(parts)}.json"
    return f"{prefix}/catalog/anime/fankai_catalog.json"


def build_meta_url(anime_id):
    """Construit le chemin d'URL pour les métadonnées d'un anime."""
    secret = get_secret_string()
    prefix = f"/{secret}" if secret else ""
    return f"{prefix}/meta/anime/{anime_id}.json"


def build_stream_url(media_id):
    """Construit le chemin d'URL pour les streams d'un épisode."""
    secret = get_secret_string()
    if secret:
        return f"/{secret}/stream/anime/{media_id}.json?kodi=1"
    return f"/stream/anime/{media_id}.json?kodi=1"


def is_elementum_installed():
    """Vérifie si le plugin Elementum est installé dans Kodi."""
    try:
        xbmcaddon.Addon("plugin.video.elementum")
        return True
    except Exception:
        return False


def build_magnet_uri(info_hash, trackers=None, display_name=None):
    """
    Construit une URI magnet à partir d'un infoHash et de sources/trackers.
    Les sources au format 'tracker:url' sont converties en paramètres &tr=.
    Les sources 'dht:hash' sont ajoutées en paramètres &dht=.
    """
    parts = [f"magnet:?xt=urn:btih:{info_hash.strip()}"]

    if display_name:
        parts.append(f"dn={url_quote(display_name, safe='')}")

    seen = set()
    if trackers:
        for source in trackers:
            if source.startswith("tracker:"):
                stype, svalue = "tr", source[len("tracker:"):]
            elif source.startswith("dht:"):
                stype, svalue = "dht", source[len("dht:"):]
            else:
                stype, svalue = "tr", source

            svalue = svalue.strip()
            if not svalue:
                continue

            key = (stype, svalue)
            if key in seen:
                continue
            seen.add(key)

            parts.append(f"{stype}={url_quote(svalue, safe='')}")

    return "&".join(parts)
