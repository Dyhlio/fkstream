# -*- coding: utf-8 -*-
try:
    import xbmc
    import xbmcgui
    import xbmcplugin
except ImportError:
    pass

from urllib.parse import urlencode, parse_qsl, quote

from lib.utils import (
    api_get,
    build_catalog_url,
    build_meta_url,
    build_stream_url,
    build_magnet_uri,
    is_configured,
    is_elementum_installed,
    get_addon_name,
    log,
)


class Router:
    def __init__(self, argv):
        self.addon_url = argv[0]
        self.handle = int(argv[1])
        self.params = dict(parse_qsl(argv[2].lstrip("?")))

    def run(self):
        action = self.params.get("action")

        if action is None:
            self.list_root()
        elif action == "browse":
            self.list_animes()
        elif action == "search":
            self.search_animes()
        elif action == "seasons":
            self.list_seasons(self.params["id"])
        elif action == "episodes":
            self.list_episodes(self.params["id"], int(self.params["season"]))
        elif action == "streams":
            self.list_streams(self.params["id"])
        elif action == "play":
            self.play_stream()
        else:
            log(f"Action inconnue: {action}")

    def _build_url(self, **kwargs):
        return f"{self.addon_url}?{urlencode(kwargs)}"

    def list_root(self):
        items = []

        li = xbmcgui.ListItem("Animes")
        li.setArt({"icon": "DefaultVideoPlaylists.png"})
        items.append((self._build_url(action="browse"), li, True))

        li = xbmcgui.ListItem("Rechercher")
        li.setArt({"icon": "DefaultAddonsSearch.png"})
        items.append((self._build_url(action="search"), li, True))

        xbmcplugin.addDirectoryItems(self.handle, items, len(items))
        xbmcplugin.endOfDirectory(self.handle)

    def list_animes(self):
        if not is_configured():
            xbmcgui.Dialog().ok(
                get_addon_name(),
                "L'addon n'est pas encore configuré.\n"
                "Allez dans les paramètres de l'addon pour lancer l'appairage.",
            )
            return

        search = self.params.get("search")
        genre = self.params.get("genre")
        sort = self.params.get("sort")

        path = build_catalog_url(search=search, genre=genre, sort=sort)
        data = api_get(path)

        if not data or "metas" not in data:
            xbmcgui.Dialog().notification(
                get_addon_name(),
                "Impossible de charger le catalogue",
                xbmcgui.NOTIFICATION_ERROR,
            )
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
            return

        metas = data["metas"]
        items = []

        for anime in metas:
            anime_id = anime.get("id", "")
            title = anime.get("name", "Inconnu")
            poster = anime.get("poster", "")
            description = anime.get("description", "")
            genres = anime.get("genres", [])
            rating = anime.get("imdbRating", "")
            year = anime.get("releaseInfo", "")

            li = xbmcgui.ListItem(title)
            li.setArt({
                "poster": poster,
                "thumb": poster,
                "icon": poster,
                "fanart": anime.get("logo", ""),
            })

            info_tag = li.getVideoInfoTag()
            info_tag.setTitle(title)
            info_tag.setPlot(description)
            if genres:
                info_tag.setGenres(genres)
            if rating:
                try:
                    info_tag.setRating(float(rating))
                except (ValueError, TypeError):
                    pass
            if year:
                try:
                    info_tag.setYear(int(year))
                except (ValueError, TypeError):
                    pass
            status = anime.get("runtime", "")
            if status:
                info_tag.setTvShowStatus(status)
            info_tag.setMediaType("tvshow")

            url = self._build_url(action="seasons", id=anime_id)
            items.append((url, li, True))

        xbmcplugin.setContent(self.handle, "tvshows")
        xbmcplugin.addDirectoryItems(self.handle, items, len(items))
        xbmcplugin.endOfDirectory(self.handle)

    def search_animes(self):
        keyboard = xbmc.Keyboard("", "Rechercher un anime")
        keyboard.doModal()

        if not keyboard.isConfirmed():
            return

        query = keyboard.getText().strip()
        if not query:
            return

        self.params["search"] = query
        self.list_animes()

    def list_seasons(self, anime_id):
        if not is_configured():
            return

        path = build_meta_url(anime_id)
        data = api_get(path)

        if not data or "meta" not in data:
            xbmcgui.Dialog().notification(
                get_addon_name(),
                "Impossible de charger les détails de l'anime",
                xbmcgui.NOTIFICATION_ERROR,
            )
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
            return

        meta = data["meta"]
        videos = meta.get("videos", [])
        anime_title = meta.get("name", "Anime")
        poster = meta.get("poster", "")
        background = meta.get("background", "")
        description = meta.get("description", "")
        genres = meta.get("genres", [])
        rating = meta.get("imdbRating", "")
        year = meta.get("releaseInfo", "")
        status = meta.get("runtime", "")

        seasons = {}
        for video in videos:
            season_num = video.get("season")
            if season_num is not None and season_num not in seasons:
                seasons[season_num] = []
            if season_num is not None:
                seasons[season_num].append(video)

        # Images et métadonnées par saison (fourni par l'API, ignoré par Stremio)
        season_images = meta.get("seasonImages", {})

        xbmcplugin.setPluginCategory(self.handle, anime_title)

        items = []
        for season_num in sorted(seasons.keys()):
            episode_count = len(seasons[season_num])
            label = f"Saison {season_num} ({episode_count} épisodes)"

            si = season_images.get(str(season_num), {})
            season_poster = si.get("poster", poster)
            season_fanart = si.get("fanart", background)
            season_overview = si.get("overview", description)

            li = xbmcgui.ListItem(label)
            li.setArt({
                "poster": season_poster,
                "thumb": season_poster,
                "fanart": season_fanart,
            })

            info_tag = li.getVideoInfoTag()
            info_tag.setTitle(anime_title)
            info_tag.setPlot(season_overview)
            info_tag.setSeason(season_num)
            if genres:
                info_tag.setGenres(genres)
            if rating:
                try:
                    info_tag.setRating(float(rating))
                except (ValueError, TypeError):
                    pass
            if year:
                try:
                    info_tag.setYear(int(year))
                except (ValueError, TypeError):
                    pass
            if status:
                info_tag.setTvShowStatus(status)
            info_tag.setMediaType("season")

            url = self._build_url(action="episodes", id=anime_id, season=season_num)
            items.append((url, li, True))

        xbmcplugin.setContent(self.handle, "seasons")
        xbmcplugin.addDirectoryItems(self.handle, items, len(items))
        xbmcplugin.endOfDirectory(self.handle)

    def list_episodes(self, anime_id, season_number):
        if not is_configured():
            return

        path = build_meta_url(anime_id)
        data = api_get(path)

        if not data or "meta" not in data:
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
            return

        meta = data["meta"]
        videos = meta.get("videos", [])
        anime_title = meta.get("name", "Anime")
        poster = meta.get("poster", "")
        background = meta.get("background", "")

        si = meta.get("seasonImages", {}).get(str(season_number), {})
        season_fanart = si.get("fanart", background)
        season_poster = si.get("poster", poster)

        xbmcplugin.setPluginCategory(self.handle, f"{anime_title} / Saison {season_number}")

        episodes = [v for v in videos if v.get("season") == season_number]
        episodes.sort(key=lambda x: x.get("episode", 0))

        items = []
        for ep in episodes:
            ep_num = ep.get("episode", 0)
            ep_title = ep.get("title", f"Épisode {ep_num}")
            ep_id = ep.get("id", "")
            thumbnail = ep.get("thumbnail", "")
            overview = ep.get("overview", "")

            label = f"E{ep_num:02d} — {ep_title}"

            li = xbmcgui.ListItem(label)
            ep_image = thumbnail or season_poster
            li.setArt({
                "poster": ep_image,
                "thumb": ep_image,
                "fanart": season_fanart,
            })

            info_tag = li.getVideoInfoTag()
            info_tag.setTitle(ep_title)
            info_tag.setSeason(season_number)
            info_tag.setEpisode(ep_num)
            info_tag.setPlot(overview)
            info_tag.setMediaType("episode")

            url = self._build_url(action="streams", id=ep_id)
            items.append((url, li, True))

        xbmcplugin.setContent(self.handle, "episodes")
        xbmcplugin.addDirectoryItems(self.handle, items, len(items))
        xbmcplugin.endOfDirectory(self.handle)

    def list_streams(self, media_id):
        if not is_configured():
            return

        ep_plot = ""
        ep_poster = ""
        ep_fanart = ""
        ep_title = ""
        ep_thumbnail = ""
        ep_season = 0
        ep_number = 0
        anime_title = ""
        parts = media_id.split(":")
        if len(parts) >= 2:
            anime_id = ":".join(parts[:2])
            meta_path = build_meta_url(anime_id)
            meta_data = api_get(meta_path)
            if meta_data and "meta" in meta_data:
                meta = meta_data["meta"]
                anime_title = meta.get("name", "")
                ep_poster = meta.get("poster", "")
                ep_fanart = meta.get("background", "")
                for video in meta.get("videos", []):
                    if video.get("id") == media_id:
                        ep_plot = video.get("overview", "")
                        ep_title = video.get("title", "")
                        ep_season = video.get("season", 0)
                        ep_number = video.get("episode", 0)
                        ep_thumbnail = video.get("thumbnail", "")
                        break
                if not ep_plot:
                    ep_plot = meta.get("description", "")

                if ep_season:
                    si = meta.get("seasonImages", {}).get(str(ep_season), {})
                    ep_poster = si.get("poster", ep_poster)
                    ep_fanart = si.get("fanart", ep_fanart)

        if ep_season and ep_number:
            category = f"{anime_title} / S{ep_season:02d}E{ep_number:02d}" if anime_title else f"S{ep_season:02d}E{ep_number:02d}"
            if ep_title:
                category += f" / {ep_title}"
            xbmcplugin.setPluginCategory(self.handle, category)

        path = build_stream_url(media_id)
        data = api_get(path, timeout=30)

        if not data or "streams" not in data:
            xbmcgui.Dialog().notification(
                get_addon_name(),
                "Aucun stream disponible",
                xbmcgui.NOTIFICATION_WARNING,
            )
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
            return

        streams = data["streams"]
        if not streams:
            xbmcgui.Dialog().notification(
                get_addon_name(),
                "Aucun stream trouvé pour cet épisode",
                xbmcgui.NOTIFICATION_WARNING,
            )
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
            return

        items = []
        for stream in streams:
            stream_name = stream.get("name", "Stream")
            stream_desc = stream.get("description", "")
            stream_url = stream.get("url")
            info_hash = stream.get("infoHash")
            sources = stream.get("sources", [])
            behavior = stream.get("behaviorHints", {})
            filename = behavior.get("filename", stream_desc)
            video_size = behavior.get("videoSize", 0)

            size_str = ""
            if video_size and video_size > 0:
                size_mb = video_size / (1024 * 1024)
                if size_mb >= 1024:
                    size_str = f" [{size_mb / 1024:.1f} GB]"
                else:
                    size_str = f" [{size_mb:.0f} MB]"

            label = f"{stream_name} — {stream_desc}{size_str}"

            li = xbmcgui.ListItem(label)
            li.setProperty("IsPlayable", "true")
            stream_image = ep_thumbnail or ep_poster
            li.setArt({
                "poster": stream_image,
                "thumb": stream_image,
                "fanart": ep_fanart,
            })

            info_tag = li.getVideoInfoTag()
            info_tag.setTitle(ep_title or stream_desc)
            info_tag.setPlot(ep_plot)
            if ep_season:
                info_tag.setSeason(ep_season)
            if ep_number:
                info_tag.setEpisode(ep_number)
            info_tag.setMediaType("episode")

            file_idx = stream.get("fileIdx")

            if stream_url:
                # Stream debrid ou custom : URL directe
                play_url = self._build_url(
                    action="play",
                    url=stream_url,
                    type="url",
                )
            elif info_hash:
                # Stream torrent : magnet via Elementum
                magnet = build_magnet_uri(info_hash, sources, display_name=filename)
                play_params = {
                    "action": "play",
                    "magnet": magnet,
                    "type": "magnet",
                    "filename": filename,
                }
                if file_idx is not None:
                    play_params["file_idx"] = str(file_idx)
                play_url = self._build_url(**play_params)
            else:
                continue

            items.append((play_url, li, False))

        xbmcplugin.setContent(self.handle, "videos")
        xbmcplugin.addDirectoryItems(self.handle, items, len(items))
        xbmcplugin.endOfDirectory(self.handle)

    def play_stream(self):
        stream_type = self.params.get("type")

        if stream_type == "url":
            # Debrid ou custom source : lecture directe
            url = self.params.get("url")
            if not url:
                log("Erreur: pas d'URL de stream")
                return

            log(f"Lecture URL directe: {url}")
            li = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(self.handle, True, li)

        elif stream_type == "magnet":
            # Torrent : via Elementum
            magnet = self.params.get("magnet")
            filename = self.params.get("filename", "")
            file_idx = self.params.get("file_idx")

            if not magnet:
                log("Erreur: pas de magnet URI")
                return

            if is_elementum_installed():
                elementum_url = f"plugin://plugin.video.elementum/play?uri={quote(magnet, safe='')}"
                if file_idx is not None:
                    elementum_url += f"&oindex={file_idx}"
                    log(f"Lecture via Elementum avec oindex={file_idx}: {elementum_url}")
                else:
                    log(f"Lecture via Elementum: {elementum_url}")
                li = xbmcgui.ListItem(path=elementum_url)
                xbmcplugin.setResolvedUrl(self.handle, True, li)
            else:
                xbmcgui.Dialog().ok(
                    get_addon_name(),
                    "Le plugin Elementum est requis pour le streaming torrent.\n\n"
                    "Installez 'plugin.video.elementum' depuis le gestionnaire d'addons Kodi,\n"
                    "ou utilisez un service de débridage dans les paramètres FKStream.",
                )
                xbmcplugin.setResolvedUrl(self.handle, False, xbmcgui.ListItem())
        else:
            log(f"Type de stream inconnu: {stream_type}")
            xbmcplugin.setResolvedUrl(self.handle, False, xbmcgui.ListItem())
