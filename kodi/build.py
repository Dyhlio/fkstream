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
ASSETS_DIR = KODI_DIR.parent / "fkstream" / "assets"
ASSETS_MAP = {
    "fkstream-logo.jpg": "icon.jpg",
    "fkstream-background.jpg": "fanart.jpg",
}

def get_version(addon_dir: Path) -> str:
    xml_path = addon_dir / "addon.xml"
    tree = ET.parse(xml_path)
    return tree.getroot().attrib["version"]


def build_zip(addon_id: str, version: str, is_addon: bool = False):
    src_dir = KODI_DIR / addon_id
    build_addon_dir = BUILD_DIR / addon_id
    dist_addon_dir = DIST_DIR / addon_id

    build_addon_dir.mkdir(parents=True, exist_ok=True)
    dist_addon_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(src_dir, build_addon_dir, dirs_exist_ok=True)

    if is_addon:
        for cache_dir in build_addon_dir.rglob("__pycache__"):
            shutil.rmtree(cache_dir)

    # Copier addon.xml dans dist/ (pour generate_repository.py)
    shutil.copy2(src_dir / "addon.xml", dist_addon_dir / "addon.xml")

    # Copier les assets (icon/fanart) depuis fkstream/assets/ vers build/ (ZIP) et dist/ (repo index)
    # Pour le plugin, les assets vont dans resources/ ; pour le repo, à la racine
    assets_subdir = "resources" if is_addon else ""
    for src_name, dst_name in ASSETS_MAP.items():
        src_path = ASSETS_DIR / src_name
        if src_path.exists():
            for target_dir in [build_addon_dir, dist_addon_dir]:
                dst_dir = target_dir / assets_subdir if assets_subdir else target_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_dir / dst_name)

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
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    addon_version = get_version(KODI_DIR / ADDON_ID)
    repo_version = get_version(KODI_DIR / REPO_ID)

    print(f"Building FKStream Kodi Repository (Plugin v{addon_version} / Repo v{repo_version})...")

    build_zip(ADDON_ID, addon_version, is_addon=True)
    build_zip(REPO_ID, repo_version)

    print("  Generating repository index...")
    import generate_repository
    generate_repository.main()

    generate_index_html(addon_version, repo_version)

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    print(f"Success: {DIST_DIR}/ is ready.")


if __name__ == "__main__":
    main()
