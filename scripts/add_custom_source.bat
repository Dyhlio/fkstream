@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:MENU
cls
echo.
echo  _____ _  ______ _____ ____  _____    _    __  __
echo ^|  ___^| ^|/ / ___^|_   _^|  _ \^| ____^|  / \  ^|  \/  ^|
echo ^| ^|_  ^| ' /\___ \ ^| ^| ^| ^|_) ^|  _^|   / _ \ ^| ^|\/^| ^|
echo ^|  _^| ^| . \ ___) ^|^| ^| ^|  _ ^<^| ^|___ / ___ \^| ^|  ^| ^|
echo ^|_^|   ^|_^|\_\____/ ^|_^| ^|_^| \_\_____/_/   \_\_^|  ^|_^|
echo.
echo =========================================================
echo.

set "JSON_FILE=custom_sources.json"

if not exist "%JSON_FILE%" (
    echo [INFO] Creation du fichier custom_sources.json...
    echo {"animes":[]}> "%JSON_FILE%"
) else (
    echo [INFO] Fichier custom_sources.json trouve
)
echo.

set /p "API_ID=API ID de l'anime: "
set /p "ANIME_ID=ID de l'anime (slug): "
set /p "ANIME_NAME=Nom de l'anime: "

echo.
echo Mode d'ajout:
echo   [1] Un seul episode (mode simple)
echo   [2] Plusieurs episodes (mode batch)
set /p "MODE_CHOICE=Votre choix (1 ou 2): "

echo.

if "%MODE_CHOICE%"=="2" goto MODE_BATCH
if "%MODE_CHOICE%"=="1" goto MODE_SIMPLE
echo Mode invalide
goto MENU

:MODE_BATCH
echo =========================================================
echo Format: sXeY=url1,url2,url3
echo.
echo Exemples valides:
echo   s1e1=https://site.com/video.mp4
echo   s1e2=https://site.com/v2.mp4,https://mirror.com/v2.mp4
echo   s2e5=https://autre.com/episode.mp4
echo.
echo Commandes: 'f' puis ENTREE = envoyer ^| 'q' puis ENTREE = annuler
echo =========================================================
echo.

set "BATCH_DATA="

:BATCH_LOOP
set /p "LINE=> "

rem Trim leading/trailing spaces only
for /f "tokens=* delims= " %%a in ("!LINE!") do set "LINE_TRIMMED=%%a"
if not defined LINE_TRIMMED set "LINE_TRIMMED="

rem Check commands (case insensitive)
if /I "!LINE_TRIMMED!"=="f" goto BATCH_PROCESS
if /I "!LINE_TRIMMED!"=="q" (
    echo [INFO] Saisie annulee
    set "BATCH_DATA="
    goto BATCH_PROCESS
)
if "!LINE_TRIMMED!"=="" goto BATCH_LOOP

if "!BATCH_DATA!"=="" (
    set "BATCH_DATA=!LINE!"
) else (
    set "BATCH_DATA=!BATCH_DATA!|!LINE!"
)
goto BATCH_LOOP

:BATCH_PROCESS
if "!BATCH_DATA!"=="" (
    echo [INFO] Aucune donnee a traiter
    echo.
    set /p "CHOICE=Ajouter une autre source (a) ou quitter (q) ? "
    if /I "!CHOICE!"=="A" goto MENU
    if /I "!CHOICE!"=="Q" exit /b 0
    goto MENU
)

echo.
echo [INFO] Traitement en cours...

python -c "import json;import re;data=json.load(open(r'%JSON_FILE%',encoding='utf-8'));anime=next((a for a in data.get('animes',[]) if a['api_id']==%API_ID%),None);anime=anime or {'api_id':%API_ID%,'id':'%ANIME_ID%','name':'%ANIME_NAME%','seasons':[]};data.setdefault('animes',[]).append(anime) if anime not in data.get('animes',[]) else None;batch_lines=r'''!BATCH_DATA!'''.split('|');total_episodes=0;total_urls=0;exec('''for line in batch_lines:\n line=line.strip()\n if not line:continue\n match=re.match(r\"s(\\d+)e(\\d+)=(.+)\",line,re.IGNORECASE)\n if not match:print(f\"[ERREUR] Format invalide ignore: {line}\");continue\n season_num=int(match.group(1));episode_num=int(match.group(2));urls=[u.strip() for u in match.group(3).split(\",\") if u.strip()]\n season=next((s for s in anime[\"seasons\"] if s[\"season_number\"]==season_num),None)\n if not season:season={\"season_number\":season_num,\"episodes\":[]};anime[\"seasons\"].append(season)\n episode=next((e for e in season[\"episodes\"] if e[\"episode_number\"]==episode_num),None)\n if not episode:episode={\"episode_number\":episode_num,\"urls\":[]};season[\"episodes\"].append(episode)\n new_urls=[url for url in urls if url not in episode[\"urls\"]];episode[\"urls\"].extend(new_urls);total_episodes+=1;total_urls+=len(new_urls)''');[a.__setitem__('seasons',sorted(a['seasons'],key=lambda s:s['season_number'])) or [s.__setitem__('episodes',sorted(s['episodes'],key=lambda e:e['episode_number'])) for s in a['seasons']] for a in data.get('animes',[])];data.__setitem__('animes',sorted(data.get('animes',[]),key=lambda a:a['api_id']));json.dump(data,open(r'%JSON_FILE%','w',encoding='utf-8'),ensure_ascii=False,indent=2);print(f'[SUCCESS] {total_episodes} episode(s) ajoute(s) avec {total_urls} URL(s) pour %ANIME_NAME%')"
goto CHECK_ERROR

:MODE_SIMPLE
set /p "SEASON=Numero de saison: "
set /p "EPISODE=Numero d'episode: "
set /p "URLS=URL(s) (separees par des virgules): "

echo.
echo [INFO] Traitement en cours...

python -c "import json;data=json.load(open(r'%JSON_FILE%',encoding='utf-8'));anime=next((a for a in data.get('animes',[]) if a['api_id']==%API_ID%),None);urls=[u.strip() for u in r'''%URLS%'''.split(',')];anime=anime or {'api_id':%API_ID%,'id':'%ANIME_ID%','name':'%ANIME_NAME%','seasons':[]};data.setdefault('animes',[]).append(anime) if anime not in data.get('animes',[]) else None;season=next((s for s in anime['seasons'] if s['season_number']==%SEASON%),None);season=season or {'season_number':%SEASON%,'episodes':[]};anime['seasons'].append(season) if season not in anime['seasons'] else None;episode=next((e for e in season['episodes'] if e['episode_number']==%EPISODE%),None);episode=episode or {'episode_number':%EPISODE%,'urls':[]};season['episodes'].append(episode) if episode not in season['episodes'] else None;new_urls=[url for url in urls if url not in episode['urls']];episode['urls'].extend(new_urls);[a.__setitem__('seasons',sorted(a['seasons'],key=lambda s:s['season_number'])) or [s.__setitem__('episodes',sorted(s['episodes'],key=lambda e:e['episode_number'])) for s in a['seasons']] for a in data.get('animes',[])];data.__setitem__('animes',sorted(data.get('animes',[]),key=lambda a:a['api_id']));json.dump(data,open(r'%JSON_FILE%','w',encoding='utf-8'),ensure_ascii=False,indent=2);print(f'[SUCCESS] {len(new_urls)} URL(s) ajoutee(s) pour %ANIME_NAME% S{%SEASON%}E{%EPISODE%}')"

:CHECK_ERROR
if errorlevel 1 (
    echo [ERROR] Erreur lors de l'ajout
    pause
    exit /b 1
)

echo.
echo.
set /p "CHOICE=Ajouter une autre source (a) ou quitter (q) ? "

if /I "%CHOICE%"=="A" goto MENU
if /I "%CHOICE%"=="Q" exit /b 0

echo Choix invalide, fermeture...
timeout /t 2 >nul
exit /b 0
