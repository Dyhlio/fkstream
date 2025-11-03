# Scripts FKStream

## add_custom_source - Ajout de sources personnalisées

### Description
Script interactif pour ajouter des URLs de streaming personnalisées au fichier `custom_sources.json`.

### Fonctionnalités
- Vérification intelligente des doublons
- Création automatique du fichier JSON si inexistant
- Ajout uniquement des nouvelles URLs (évite les duplications)
- Support de plusieurs URLs par épisode (séparées par des virgules)
- Mise à jour automatique des animes/saisons/épisodes existants

### Utilisation

#### Windows
```batch
cd scripts
add_custom_source.bat
```

#### Linux/Mac
```bash
cd scripts
chmod +x add_custom_source.sh
./add_custom_source.sh
```

### Workflow du script

1. **API ID de l'anime** - Entrer l'ID numérique de l'anime
2. **ID de l'anime** - Slug de l'anime (ex: black-clover-kai)
3. **Nom de l'anime** - Nom complet de l'anime
4. **Numéro de saison** - Numéro de la saison (1, 2, 3...)
5. **Numéro d'épisode** - Numéro de l'épisode (1, 2, 3...)
6. **URLs** - Une ou plusieurs URLs séparées par des virgules

### Logique de vérification

#### Si l'anime n'existe pas
→ Crée un nouvel anime avec la saison et l'épisode

#### Si l'anime existe mais pas la saison
→ Ajoute la nouvelle saison avec l'épisode

#### Si l'anime et la saison existent mais pas l'épisode
→ Ajoute le nouvel épisode avec les URLs

#### Si tout existe déjà
→ Ajoute uniquement les URLs qui ne sont pas déjà présentes (évite les doublons)

### Structure du fichier custom_sources.json

```json
{
  "animes": [
    {
      "api_id": 58,
      "id": "black-clover-kai",
      "name": "Black Clover Kaï",
      "seasons": [
        {
          "season_number": 1,
          "episodes": [
            {
              "episode_number": 1,
              "urls": [
                "https://exemple.com/videas1",
                "https://autre.com/videas2"
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Notes importantes

- Le fichier JSON est automatiquement formaté avec indentation (2 espaces) pour une meilleure lisibilité
- Le script gère automatiquement les doublons d'URLs au niveau de chaque épisode
