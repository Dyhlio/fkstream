#!/bin/bash

while true; do
    clear
    echo ""
    echo " _____ _  ______ _____ ____  _____    _    __  __"
    echo "|  ___| |/ / ___|_   _|  _ \| ____|  / \  |  \/  |"
    echo "| |_  | ' /\___ \ | | | |_) |  _|   / _ \ | |\/| |"
    echo "|  _| | . \ ___) || | |  _ <| |___ / ___ \| |  | |"
    echo "|_|   |_|\_\____/ |_| |_| \_\_____/_/   \_\_|  |_|"
    echo ""
    echo "========================================================="
    echo ""

    JSON_FILE="custom_sources.json"

    if [ ! -f "$JSON_FILE" ]; then
        echo "[INFO] Creation du fichier custom_sources.json..."
        echo '{"animes":[]}' > "$JSON_FILE"
    else
        echo "[INFO] Fichier custom_sources.json trouve"
    fi
    echo ""

    read -p "API ID de l'anime: " API_ID
    read -p "ID de l'anime (slug): " ANIME_ID
    read -p "Nom de l'anime: " ANIME_NAME
    read -p "Numero de saison: " SEASON
    read -p "Numero d'episode: " EPISODE
    read -p "URL(s) (separees par des virgules): " URLS

    echo ""
    echo "[INFO] Traitement en cours..."

    python3 -c "
import json
data = json.load(open('$JSON_FILE', encoding='utf-8'))
anime = next((a for a in data.get('animes', []) if a['api_id'] == $API_ID), None)
urls = [u.strip() for u in '$URLS'.split(',')]
if not anime:
    anime = {'api_id': $API_ID, 'id': '$ANIME_ID', 'name': '$ANIME_NAME', 'seasons': []}
    data.setdefault('animes', []).append(anime)
season = next((s for s in anime['seasons'] if s['season_number'] == $SEASON), None)
if not season:
    season = {'season_number': $SEASON, 'episodes': []}
    anime['seasons'].append(season)
episode = next((e for e in season['episodes'] if e['episode_number'] == $EPISODE), None)
if not episode:
    episode = {'episode_number': $EPISODE, 'urls': []}
    season['episodes'].append(episode)
new_urls = [url for url in urls if url not in episode['urls']]
episode['urls'].extend(new_urls)
for a in data.get('animes', []):
    a['seasons'] = sorted(a['seasons'], key=lambda s: s['season_number'])
    for s in a['seasons']:
        s['episodes'] = sorted(s['episodes'], key=lambda e: e['episode_number'])
json.dump(data, open('$JSON_FILE', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'[SUCCESS] {len(new_urls)} URL(s) ajoutee(s) pour $ANIME_NAME S{$SEASON}E{$EPISODE}')
"

    if [ $? -ne 0 ]; then
        echo "[ERROR] Erreur lors de l'ajout"
        exit 1
    fi

    echo ""
    echo ""
    read -p "Ajouter une autre source (A) ou Quitter (Q) ? " CHOICE

    if [ "$CHOICE" = "Q" ] || [ "$CHOICE" = "q" ]; then
        exit 0
    elif [ "$CHOICE" != "A" ] && [ "$CHOICE" != "a" ]; then
        echo "Choix invalide, fermeture..."
        sleep 2
        exit 0
    fi
done
