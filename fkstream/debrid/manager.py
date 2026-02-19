from .realdebrid import RealDebrid
from .alldebrid import AllDebrid
from .premiumize import Premiumize
from .torbox import TorBox
from .debridlink import DebridLink
from .torrent import Torrent
from .stremthru import StremThru
from .easydebrid import EasyDebrid
from .offcloud import Offcloud
from .pikpak import PikPak

debrid_services = {
    "realdebrid": {"extension": "RD", "cache_availability_endpoint": False, "class": RealDebrid},
    "alldebrid": {"extension": "AD", "cache_availability_endpoint": False, "class": AllDebrid},
    "premiumize": {"extension": "PM", "cache_availability_endpoint": True, "class": Premiumize},
    "torbox": {"extension": "TB", "cache_availability_endpoint": True, "class": TorBox},
    "debridlink": {"extension": "DL", "cache_availability_endpoint": False, "class": DebridLink},
    "stremthru": {"extension": "ST", "cache_availability_endpoint": True, "class": StremThru},
    "easydebrid": {"extension": "ED", "cache_availability_endpoint": True, "class": EasyDebrid},
    "offcloud": {"extension": "OC", "cache_availability_endpoint": False, "class": Offcloud},
    "pikpak": {"extension": "PP", "cache_availability_endpoint": False, "class": PikPak},
    "torrent": {"extension": "TORRENT", "cache_availability_endpoint": False, "class": Torrent},
}

def get_debrid_extension(debrid_service: str):
    if debrid_service not in debrid_services:
        raise ValueError(f"Service debrid inconnu: {debrid_service}")
    return debrid_services[debrid_service]["extension"]


def build_stremthru_token(debrid_service: str, debrid_api_key: str):
    return f"{debrid_service}:{debrid_api_key}"
