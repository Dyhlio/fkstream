import os
import subprocess
import time
import traceback
from urllib.parse import urljoin

import requests
import xbmc
import xbmcaddon
import xbmcgui

ADDON_ID = "plugin.video.fkstream"
REQUEST_TIMEOUT = 20
POLL_INTERVAL_SECONDS = 3
HTTP_SESSION = requests.Session()


def normalize_base_url(url):
    return url.rstrip("/")


def open_configuration_page(url):
    os_windows = xbmc.getCondVisibility("system.platform.windows")
    os_osx = xbmc.getCondVisibility("system.platform.osx")
    os_linux = xbmc.getCondVisibility("system.platform.linux")
    os_android = xbmc.getCondVisibility("System.Platform.Android")

    try:
        if os_osx:
            subprocess.run(["open", url], check=True)
            return
        if os_windows:
            os.startfile(url)
            return
        if os_linux and not os_android:
            subprocess.run(["xdg-open", url], check=True)
            return
        if os_android:
            safe_url = url.replace('"', "%22")
            xbmc.executebuiltin(
                f'StartAndroidActivity("","android.intent.action.VIEW","","{safe_url}")'
            )
            return
    except Exception as exc:
        xbmc.log(f"[FKStream] Impossible d'ouvrir la page de configuration: {exc}", xbmc.LOGERROR)


def _post_json(url, payload=None):
    response = HTTP_SESSION.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _get_json(url):
    response = HTTP_SESSION.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def configure_fkstream():
    try:
        addon = xbmcaddon.Addon(ADDON_ID)
        dialog = xbmcgui.Dialog()
        monitor = xbmc.Monitor()

        base_url = addon.getSetting("base_url")
        secret_string = addon.getSetting("secret_string")

        entered_url = dialog.input("URL du serveur FKStream", base_url)
        if not entered_url:
            return

        base_url = normalize_base_url(entered_url)
        addon.setSetting("base_url", base_url)

        entered_secret = dialog.input(
            "Configuration (optionnel)",
            secret_string,
            option=xbmcgui.ALPHANUM_HIDE_INPUT,
        )
        if entered_secret is not None:
            secret_string = entered_secret
            addon.setSetting("secret_string", secret_string)

        try:
            data = _post_json(
                urljoin(base_url + "/", "kodi/generate_setup_code"),
                {"secret_string": secret_string},
            )
        except requests.RequestException as exc:
            dialog.notification(
                "FKStream",
                "Impossible de generer le code",
                xbmcgui.NOTIFICATION_ERROR,
            )
            xbmc.log(f"[FKStream] Impossible de generer le code d'appairage: {exc}", xbmc.LOGERROR)
            return

        try:
            code = data["code"]
            configure_url = data["configure_url"]
            expires_in = data["expires_in"]
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError("Reponse invalide depuis /kodi/generate_setup_code") from exc

        dialog.ok(
            "FKStream - Appairage Kodi",
            f"Code d'appairage : {code}\n"
            f"Ouvrez la page de configuration et completez avant expiration.",
        )

        if dialog.yesno(
            "FKStream",
            "Ouvrir la page de configuration dans le navigateur ?",
        ):
            open_configuration_page(configure_url)

        dialog.notification(
            "FKStream",
            f"En attente du code {code}...",
            xbmcgui.NOTIFICATION_INFO,
        )

        deadline = time.time() + expires_in
        while time.time() < deadline:
            try:
                manifest_data = _get_json(
                    urljoin(base_url + "/", f"kodi/get_manifest/{code}")
                )
            except requests.HTTPError as exc:
                response = exc.response
                if response is None or response.status_code != 404:
                    xbmc.log(
                        f"[FKStream] Erreur lors du polling: {exc}",
                        xbmc.LOGWARNING,
                    )
            except requests.RequestException as exc:
                xbmc.log(
                    f"[FKStream] Erreur lors du polling: {exc}",
                    xbmc.LOGWARNING,
                )
            else:
                addon.setSetting("secret_string", manifest_data["secret_string"])
                dialog.notification(
                    "FKStream",
                    "Appairage Kodi reussi !",
                    xbmcgui.NOTIFICATION_INFO,
                )
                return

            if monitor.waitForAbort(POLL_INTERVAL_SECONDS):
                return

        dialog.notification(
            "FKStream",
            "Code expire. Relancez l'appairage.",
            xbmcgui.NOTIFICATION_ERROR,
        )

    except Exception:
        xbmc.log(
            "[FKStream] Erreur appairage Kodi:\n" + traceback.format_exc(),
            xbmc.LOGERROR,
        )
        xbmcgui.Dialog().notification(
            "FKStream",
            "Erreur d'appairage (voir log Kodi)",
            xbmcgui.NOTIFICATION_ERROR,
        )


if __name__ == "__main__":
    configure_fkstream()
