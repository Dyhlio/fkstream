import re
import time
import unicodedata
from fkstream.utils.common_logger import logger
from fkstream.utils.models import Episode

# --- Fonctions utilitaires de base ---

def bytes_to_size(bytes_val: int) -> str:
    """Convertit les octets en une chaîne de caractères lisible (KB, MB, GB)."""
    if not isinstance(bytes_val, (int, float)) or bytes_val == 0:
        return "N/A"
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024**2:
        return f"{bytes_val/1024:.2f} KB"
    elif bytes_val < 1024**3:
        return f"{bytes_val/1024**2:.2f} MB"
    else:
        return f"{bytes_val/1024**3:.2f} GB"

# --- Cache module-level pour la liste de renommage ---

_rename_map_cache: dict | None = None
_rename_map_cache_time: float = 0
_RENAME_MAP_TTL = 604800  # 7 jours

# --- Logique de matching ---

def _normalize_filename_for_matching(filename: str) -> str:
    """
    Normalise une chaîne de caractères pour une comparaison flexible.
    """
    if not filename:
        return ''
    
    base = filename.lower()
    base = unicodedata.normalize('NFD', base).encode('ascii', 'ignore').decode('utf-8')
    
    # Supprime les métadonnées courantes
    base = re.sub(r'\[.*?\]|\(.*?\)', '', base)
    base = re.sub(r'\b\d{3,4}p\b', '', base)
    base = re.sub(r'.(mkv|mp4|avi|nfo)(?=\s|$)', '', base, flags=re.IGNORECASE, count=0)
    base = re.sub(r'\b(multi|vo|vf|vostfr|x264|x265|hevc|bdrip|webrip|dvdrip)\b', '', base)
    
    # Nettoyage final
    base = re.sub(r'[.\-_|\']', ' ', base)
    
    base = re.sub(r'\b(\d+)\s*x\s*(\d+)\b', r' \2 ', base)
    
    # Supprime les zéros non significatifs (ex: "02" -> "2")
    base = re.sub(r'\b0+(\d+)\b', r'\1', base)
    
    return ' '.join(base.split()).strip()

async def _get_rename_map(http_client) -> dict:
    """
    Récupère et met en cache le dictionnaire de renommage depuis l'URL distante.
    Utilise un cache module-level avec TTL de 7 jours pour éviter les téléchargements répétés.
    """
    global _rename_map_cache, _rename_map_cache_time
    if _rename_map_cache is not None and (time.time() - _rename_map_cache_time) < _RENAME_MAP_TTL:
        return _rename_map_cache

    logger.info("Mise en cache de la liste de renommage depuis l'URL...")
    rename_map = {}
    url = "https://raw.githubusercontent.com/Nackophilz/fankai_utilitaire/refs/heads/main/rename/films.txt"

    try:
        response = await http_client.get(url)
        response.raise_for_status()

        content = response.text
        for line in content.splitlines():
            if ' -> ' in line:
                old, new = line.split(' -> ', 1)
                rename_map[old.strip()] = new.strip()

        _rename_map_cache = rename_map
        _rename_map_cache_time = time.time()
        logger.info(f"Liste de renommage chargée avec succès ({len(rename_map)} entrées).")
        return rename_map

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la liste de renommage: {e}")
        if _rename_map_cache is not None:
            logger.info("Utilisation du cache existant de la liste de renommage.")
            return _rename_map_cache
        _rename_map_cache = {}
        _rename_map_cache_time = time.time()
        return {}

async def find_best_file_for_episode(http_client, files_in_torrent: list[dict], selected_episode: Episode) -> dict | None:
    """
    Trouve le fichier le plus pertinent en utilisant une stratégie de matching en 3 étapes.
    """
    if not selected_episode or not selected_episode.nfo_filename:
        logger.warning("Aucune information d'épisode (nfo_filename) fournie pour le matching.")
        return None

    base_nfo_name = selected_episode.nfo_filename.rsplit('.nfo', 1)[0]

    # Étape 1: Match Exact
    logger.debug(f"Étape 1: Recherche de correspondance exacte pour '{base_nfo_name}'")
    for file_info in files_in_torrent:
        file_title = file_info.get("title", "")
        if not file_title.lower().endswith(('.mkv', '.mp4', '.avi')):
            continue
        
        base_file_name = file_title.split('/')[-1].rsplit('.', 1)[0]
        if base_nfo_name == base_file_name:
            logger.info(f"✅ Étape 1: Succès - Correspondance exacte trouvée : '{file_title}'")
            return file_info

    # Étape 2: Match Normalisé
    logger.debug("Étape 2: Recherche de correspondance normalisée...")
    normalized_nfo = _normalize_filename_for_matching(base_nfo_name)
    for file_info in files_in_torrent:
        file_title = file_info.get("title", "")
        if not file_title.lower().endswith(('.mkv', '.mp4', '.avi')):
            continue
            
        base_file_name = file_title.split('/')[-1].rsplit('.', 1)[0]
        normalized_file = _normalize_filename_for_matching(base_file_name)
        if normalized_nfo == normalized_file:
            logger.info(f"✅ Étape 2: Succès - Correspondance normalisée trouvée : '{file_title}'")
            return file_info
            
    # Étape 3: Match avec liste de renommage
    logger.debug("Étape 3: Recherche avec la liste de renommage...")
    rename_map = await _get_rename_map(http_client)
    if rename_map:
        for file_info in files_in_torrent:
            file_title = file_info.get("title", "")
            if not file_title.lower().endswith(('.mkv', '.mp4', '.avi')):
                continue

            base_file_name = file_title.split('/')[-1].rsplit('.', 1)[0]
            
            if base_file_name in rename_map:
                renamed_file = rename_map[base_file_name]
                if renamed_file == base_nfo_name:
                    logger.info(f"✅ Étape 3: Succès - Correspondance par renommage trouvée : '{file_title}' -> '{renamed_file}'")
                    return file_info

    logger.warning(f"❌ Échec des 3 étapes. Aucune correspondance trouvée pour '{base_nfo_name}'")
    return None
    
