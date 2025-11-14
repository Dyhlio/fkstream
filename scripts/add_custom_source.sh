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

    echo ""
    echo "Mode d'ajout:"
    echo "  [1] Un seul episode (mode simple)"
    echo "  [2] Plusieurs episodes (mode batch)"
    read -p "Votre choix (1 ou 2): " MODE_CHOICE

    echo ""

    if [ "$MODE_CHOICE" = "2" ]; then
        echo "========================================================="
        echo "Format: sXeY=url1,url2,url3"
        echo ""
        echo "Exemples valides:"
        echo "  s1e1=https://site.com/video.mp4"
        echo "  s1e2=https://site.com/v2.mp4,https://mirror.com/v2.mp4"
        echo "  s2e5=https://autre.com/episode.mp4"
        echo ""
        echo "Commandes: 'f' puis ENTREE = envoyer | 'q' puis ENTREE = annuler"
        echo "========================================================="
        echo ""

        BATCH_DATA=""
        while true; do
            read -p "> " LINE
            LINE_TRIMMED=$(echo "$LINE" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            LINE_LOWER=$(echo "$LINE_TRIMMED" | tr '[:upper:]' '[:lower:]')

            if [ "$LINE_LOWER" = "f" ]; then
                break
            elif [ "$LINE_LOWER" = "q" ]; then
                echo "[INFO] Saisie annulee"
                BATCH_DATA=""
                break
            elif [ -z "$LINE_TRIMMED" ]; then
                continue
            else
                if [ -z "$BATCH_DATA" ]; then
                    BATCH_DATA="$LINE"
                else
                    BATCH_DATA="$BATCH_DATA|$LINE"
                fi
            fi
        done

        if [ -z "$BATCH_DATA" ]; then
            echo "[INFO] Aucune donnee a traiter"
            echo ""
            read -p "Ajouter une autre source (a) ou quitter (q) ? " CHOICE
            if [ "$CHOICE" = "Q" ] || [ "$CHOICE" = "q" ]; then
                exit 0
            fi
            continue
        fi

        echo ""
        echo "[INFO] Traitement en cours..."

        python3 -c "
import json
import re
data = json.load(open('$JSON_FILE', encoding='utf-8'))
anime = next((a for a in data.get('animes', []) if a['api_id'] == $API_ID), None)
if not anime:
    anime = {'api_id': $API_ID, 'id': '$ANIME_ID', 'name': '$ANIME_NAME', 'seasons': []}
    data.setdefault('animes', []).append(anime)
batch_lines = '$BATCH_DATA'.split('|')
total_episodes = 0
total_urls = 0
for line in batch_lines:
    line = line.strip()
    if not line:
        continue
    match = re.match(r's(\d+)e(\d+)=(.+)', line, re.IGNORECASE)
    if not match:
        print(f'[ERREUR] Format invalide ignore: {line}')
        continue
    season_num = int(match.group(1))
    episode_num = int(match.group(2))
    urls = [u.strip() for u in match.group(3).split(',') if u.strip()]
    season = next((s for s in anime['seasons'] if s['season_number'] == season_num), None)
    if not season:
        season = {'season_number': season_num, 'episodes': []}
        anime['seasons'].append(season)
    episode = next((e for e in season['episodes'] if e['episode_number'] == episode_num), None)
    if not episode:
        episode = {'episode_number': episode_num, 'urls': []}
        season['episodes'].append(episode)
    new_urls = [url for url in urls if url not in episode['urls']]
    episode['urls'].extend(new_urls)
    total_episodes += 1
    total_urls += len(new_urls)
for a in data.get('animes', []):
    a['seasons'] = sorted(a['seasons'], key=lambda s: s['season_number'])
    for s in a['seasons']:
        s['episodes'] = sorted(s['episodes'], key=lambda e: e['episode_number'])
data['animes'] = sorted(data.get('animes', []), key=lambda a: a['api_id'])
json.dump(data, open('$JSON_FILE', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'[SUCCESS] {total_episodes} episode(s) ajoute(s) avec {total_urls} URL(s) pour $ANIME_NAME')
"
    else
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
data['animes'] = sorted(data.get('animes', []), key=lambda a: a['api_id'])
json.dump(data, open('$JSON_FILE', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'[SUCCESS] {len(new_urls)} URL(s) ajoutee(s) pour $ANIME_NAME S{$SEASON}E{$EPISODE}')
"
    fi

    if [ $? -ne 0 ]; then
        echo "[ERROR] Erreur lors de l'ajout"
        exit 1
    fi

    echo ""
    echo ""
    read -p "Ajouter une autre source (a) ou quitter (q) ? " CHOICE

    if [ "$CHOICE" = "Q" ] || [ "$CHOICE" = "q" ]; then
        exit 0
    elif [ "$CHOICE" != "A" ] && [ "$CHOICE" != "a" ]; then
        echo "Choix invalide, fermeture..."
        sleep 2
        exit 0
    fi
done
