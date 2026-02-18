"""
Script de build pour le repository Kodi FKStream.
Equivalent Python du Makefile de Comet, compatible Windows/Linux/Mac.

Usage:
    python build.py
"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

KODI_DIR = Path(__file__).parent
DIST_DIR = KODI_DIR / "dist"
BUILD_DIR = KODI_DIR / "build"

ADDON_ID = "plugin.video.fkstream"
REPO_ID = "repository.fkstream"
ASSETS_DIR = KODI_DIR / ADDON_ID / "resources"

def get_version(addon_dir: Path) -> str:
    """Extrait la version depuis addon.xml."""
    xml_path = addon_dir / "addon.xml"
    tree = ET.parse(xml_path)
    return tree.getroot().attrib["version"]


def build_zip(addon_id: str, version: str, is_addon: bool = False):
    """Construit le zip d'un addon et copie les fichiers nécessaires dans dist/."""
    src_dir = KODI_DIR / addon_id
    build_addon_dir = BUILD_DIR / addon_id
    dist_addon_dir = DIST_DIR / addon_id

    # Préparer les dossiers
    build_addon_dir.mkdir(parents=True, exist_ok=True)
    dist_addon_dir.mkdir(parents=True, exist_ok=True)

    # Copier les sources dans build/
    shutil.copytree(src_dir, build_addon_dir, dirs_exist_ok=True)

    # Supprimer __pycache__ pour les addons
    if is_addon:
        for cache_dir in build_addon_dir.rglob("__pycache__"):
            shutil.rmtree(cache_dir)

    # Copier addon.xml dans dist/ (pour generate_repository.py)
    shutil.copy2(src_dir / "addon.xml", dist_addon_dir / "addon.xml")

    # Copier les assets (icon/fanart) dans dist/ pour le repository
    icon_src = ASSETS_DIR / "icon.jpg"
    fanart_src = ASSETS_DIR / "fanart.jpg"

    if icon_src.exists():
        shutil.copy2(icon_src, dist_addon_dir / "icon.jpg")
    if fanart_src.exists():
        shutil.copy2(fanart_src, dist_addon_dir / "fanart.jpg")

    # Créer le zip
    zip_name = f"{addon_id}-{version}.zip"
    zip_path = dist_addon_dir / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(build_addon_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".pyc"):
                    continue
                filepath = Path(root) / f
                arcname = f"{addon_id}/{filepath.relative_to(build_addon_dir)}"
                zf.write(filepath, arcname.replace("\\", "/"))

    print(f"  Built {addon_id} v{version}")


def generate_index_html(addon_version: str, repo_version: str):
    """Génère la page HTML de téléchargement."""
    template_path = KODI_DIR / "index.html.template"
    if not template_path.exists():
        print("  Skipping index.html (no template found)")
        return

    content = template_path.read_text(encoding="utf-8")
    content = content.replace("ADDON_URL", f"{ADDON_ID}/{ADDON_ID}-{addon_version}.zip")
    content = content.replace("V_ADDON", addon_version)
    content = content.replace("REPO_URL", f"{REPO_ID}/{REPO_ID}-{repo_version}.zip")
    content = content.replace("V_REPO", repo_version)

    (DIST_DIR / "index.html").write_text(content, encoding="utf-8")
    print("  Generated index.html")


def main():
    # Nettoyer
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    # Versions
    addon_version = get_version(KODI_DIR / ADDON_ID)
    repo_version = get_version(KODI_DIR / REPO_ID)

    print(f"Building FKStream Kodi Repository (Plugin v{addon_version} / Repo v{repo_version})...")

    # Build les zips
    build_zip(ADDON_ID, addon_version, is_addon=True)
    build_zip(REPO_ID, repo_version)

    # Générer addons.xml + addons.xml.md5
    print("  Generating repository index...")
    import generate_repository
    generate_repository.main()

    # Générer index.html
    generate_index_html(addon_version, repo_version)

    # Nettoyer build/
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    print(f"Success: {DIST_DIR}/ is ready.")


if __name__ == "__main__":
    main()
