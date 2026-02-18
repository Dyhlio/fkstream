from typing import Optional
from collections import OrderedDict
import threading

class MagnetStore:
    """Stockage thread-safe pour les liens magnets."""
    _MAX_SIZE = 10_000

    def __init__(self):
        self._store: OrderedDict[str, str] = OrderedDict()
        self._lock = threading.RLock()

    def store_magnet_link(self, hash: str, magnet_link: str) -> None:
        """Stocke un lien magnet avec de vrais traqueurs pour une récupération ultérieure."""
        with self._lock:
            key = hash.lower()
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = magnet_link
            while len(self._store) > self._MAX_SIZE:
                self._store.popitem(last=False)

    def get_magnet_link(self, hash: str) -> Optional[str]:
        """Récupère un lien magnet stocké avec de vrais traqueurs."""
        with self._lock:
            return self._store.get(hash.lower())

# Instance globale pour la compatibilité ascendante
_global_magnet_store = MagnetStore()

def store_magnet_link(hash: str, magnet_link: str) -> None:
    """Stocke un lien magnet avec de vrais traqueurs pour une récupération ultérieure."""
    _global_magnet_store.store_magnet_link(hash, magnet_link)

def get_magnet_link(hash: str) -> Optional[str]:
    """Récupère un lien magnet stocké avec de vrais traqueurs."""
    return _global_magnet_store.get_magnet_link(hash)
