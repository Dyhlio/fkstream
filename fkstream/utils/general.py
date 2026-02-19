import base64
import unicodedata
from fastapi import Request


# Extensions video supportees
# Limité aux seuls formats utilisés par Fan-Kai
VIDEO_EXTENSIONS = (
    ".mkv", ".mp4"
)


def b64_encode(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode()).decode()

def b64_decode(s: str) -> str:
    try:
        if not s or not isinstance(s, str):
            raise ValueError("Entree invalide")
        return base64.urlsafe_b64decode(s).decode()
    except Exception:
        raise ValueError("Chaine base64 invalide")


def get_client_ip(request: Request) -> str:
    return request.headers.get("cf-connecting-ip", request.client.host)

def is_video(title: str) -> bool:
    return title.lower().endswith(VIDEO_EXTENSIONS)


def normalize_name(name: str) -> str:
    """Normalise un nom pour comparaison : sans accents, minuscules, uniquement lettres et chiffres."""
    if not name:
        return ""
    nfkd = unicodedata.normalize('NFKD', name)
    without_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return ''.join(c for c in without_accents.lower() if c.isalnum())
