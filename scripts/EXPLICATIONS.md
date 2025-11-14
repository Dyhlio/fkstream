# Scripts FKStream

## add_custom_source - Ajout de sources personnalisées

### Description
Script interactif pour ajouter des URLs de streaming personnalisées au fichier `custom_sources.json`.

### Fonctionnalités
- **Deux modes d'ajout** : simple (1 épisode) ou batch (plusieurs épisodes)
- Détection automatique des doublons (URLs, animes, saisons, épisodes)
- Création automatique du fichier JSON si inexistant
- Support de plusieurs URLs par épisode (séparées par des virgules)
- Tri automatique par `api_id`, saisons et épisodes
- **Mode batch sécurisé** : validation explicite avec 'f' pour envoyer

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
4. **Mode d'ajout** - Choisir entre mode simple (1 épisode) ou batch (plusieurs épisodes)

#### Mode simple (option 1)
5. **Numéro de saison** - Numéro de la saison (1, 2, 3...)
6. **Numéro d'épisode** - Numéro de l'épisode (1, 2, 3...)
7. **URLs** - Une ou plusieurs URLs séparées par des virgules

#### Mode batch (option 2)
5. **Saisie multiple** - Format: `sXeY=url1,url2,url3`
   - Une ligne par épisode
   - **Taper `f` puis ENTREE pour envoyer**
   - Taper `q` puis ENTREE pour annuler
   - Ligne vide = continue la saisie

**Exemples valides:**
```
> s1e1=https://site.com/video.mp4
> s1e2=https://site.com/v2.mp4,https://mirror.com/v2.mp4
> s2e5=https://autre.com/episode.mp4
> f
[SUCCESS] 3 episode(s) ajoute(s) avec 4 URL(s)
```

**Format:**
- `sXeY` : X = numéro de saison, Y = numéro d'épisode (insensible à la casse)
- `=` : Séparateur entre épisode et URLs
- `url1,url2` : URLs séparées par des virgules

### Logique automatique

Le script gère intelligemment toutes les situations :
- Crée automatiquement les animes, saisons ou épisodes manquants
- N'ajoute que les URLs non présentes (pas de doublons)
- Trie automatiquement par `api_id`, saisons et épisodes

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

- Le fichier JSON est automatiquement formaté avec indentation (2 espaces)
- Encodage UTF-8 pour les caractères spéciaux
