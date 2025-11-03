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
set /p "SEASON=Numero de saison: "
set /p "EPISODE=Numero d'episode: "
set /p "URLS=URL(s) (separees par des virgules): "

echo.
echo [INFO] Traitement en cours...

python -c "import json;data=json.load(open(r'%JSON_FILE%',encoding='utf-8'));anime=next((a for a in data.get('animes',[]) if a['api_id']==%API_ID%),None);urls=[u.strip() for u in '%URLS%'.split(',')];anime=anime or {'api_id':%API_ID%,'id':'%ANIME_ID%','name':'%ANIME_NAME%','seasons':[]};data.setdefault('animes',[]).append(anime) if anime not in data.get('animes',[]) else None;season=next((s for s in anime['seasons'] if s['season_number']==%SEASON%),None);season=season or {'season_number':%SEASON%,'episodes':[]};anime['seasons'].append(season) if season not in anime['seasons'] else None;episode=next((e for e in season['episodes'] if e['episode_number']==%EPISODE%),None);episode=episode or {'episode_number':%EPISODE%,'urls':[]};season['episodes'].append(episode) if episode not in season['episodes'] else None;new_urls=[url for url in urls if url not in episode['urls']];episode['urls'].extend(new_urls);[a.__setitem__('seasons',sorted(a['seasons'],key=lambda s:s['season_number'])) or [s.__setitem__('episodes',sorted(s['episodes'],key=lambda e:e['episode_number'])) for s in a['seasons']] for a in data.get('animes',[])];json.dump(data,open(r'%JSON_FILE%','w',encoding='utf-8'),ensure_ascii=False,indent=2);print(f'[SUCCESS] {len(new_urls)} URL(s) ajoutee(s) pour %ANIME_NAME% S{%SEASON%}E{%EPISODE%}')"

if errorlevel 1 (
    echo [ERROR] Erreur lors de l'ajout
    pause
    exit /b 1
)

echo.
echo.
set /p "CHOICE=Ajouter une autre source (A) ou Quitter (Q) ? "

if /I "%CHOICE%"=="A" goto MENU
if /I "%CHOICE%"=="Q" exit /b 0

echo Choix invalide, fermeture...
timeout /t 2 >nul
exit /b 0
