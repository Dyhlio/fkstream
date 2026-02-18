# FKStream Kodi

Plugin Kodi (`plugin.video.fkstream`) et son repository de mises à jour (`repository.fkstream`). Cet addon permet de parcourir et streamer des animés depuis le catalogue Fankai directement dans Kodi, avec prise en charge des services de débridage et du mode torrent direct.

## Installation (Recommandée)

L'installation via le repository permet de recevoir les mises à jour automatiquement.

1. **Ajouter la source** : Allez dans **Settings** > **File manager** > **Add source**.
2. **Entrer l'URL** : Entrez `https://dyhlio.github.io/fkstream` et nommez-la `FKStream`.
3. **Installer le repository** : Allez dans **Add-ons** > **Install from zip file** > sélectionnez `FKStream` > installez `repository.fkstream-X.X.X.zip`.
4. **Installer l'addon** : Allez dans **Install from repository** > **FKStream Repository** > **Video add-ons** > **FKStream** > **Install**.

## Configuration / Appairage

Une fois installé, vous devez lier l'addon à votre instance FKStream pour qu'il puisse communiquer avec le serveur et récupérer le catalogue, les streams, etc.

1. Allez dans **Add-ons** > **My add-ons** > **Video add-ons** > **FKStream** > **Configure**.
2. Dans la catégorie **FKStream**, cliquez sur **Configurer / Appairage**.
3. Entrez l'URL du serveur FKStream (ex : `https://domaine.com`).
4. Un **code d'appairage à 8 caractères** s'affiche (ex : `A1B2C3D4`).
5. Ouvrez la page de configuration FKStream dans votre navigateur à l'URL indiquée.
6. Configurez vos paramètres (service de débridage, clé API, filtre des flux, tri par défaut, etc.).
7. Entrez le code affiché dans Kodi dans le champ prévu, puis cliquez sur **Associer à Kodi**.

La configuration est automatiquement récupérée par l'addon. Le code expire après 5 minutes, si le délai est dépassé il suffit de relancer l'appairage.

## Installation manuelle

*Avec cette méthode, vous ne recevrez pas les mises à jour automatiques.*

1. Téléchargez le dernier zip depuis la [page de téléchargement FKStream](https://dyhlio.github.io/fkstream/).
2. Allez dans **Add-ons** > **Install from zip file** > sélectionnez le zip téléchargé.
3. Ouvrez l'addon et suivez les étapes de **Configuration / Appairage** ci-dessus.

## Modes de lecture

L'addon propose plusieurs modes de lecture selon votre configuration :

| Mode | Description | Prérequis |
|------|-------------|-----------|
| **Débridage** | Lecture via Real-Debrid, AllDebrid, TorBox, Premiumize, etc. Les torrents sont téléchargés sur le débrideur et vous recevez un lien direct. | Un compte actif sur un service de débridage, configuré dans FKStream. |
| **Torrent direct** | Streaming torrent en temps réel via Elementum. Le torrent est téléchargé et lu simultanément sans passer par un service tiers. | Le plugin `plugin.video.elementum` doit être installé dans Kodi. Si vous utilisez un service de débridage, Elementum n'est pas nécessaire. |
| **Sources externes** | Lecture directe depuis des sources personnalisées ajoutées via le fichier `custom_sources.json`. | Aucun prérequis supplémentaire. |

## Build

Si vous souhaitez construire l'addon et le repository depuis les sources :

```sh
cd kodi
python build.py
```

Le script génère automatiquement le dossier `dist/` prêt à être déployé :

```text
dist/
├── addons.xml
├── addons.xml.md5
├── index.html
├── plugin.video.fkstream/
│   ├── addon.xml
│   ├── icon.jpg
│   ├── fanart.jpg
│   └── plugin.video.fkstream-X.X.X.zip
└── repository.fkstream/
    ├── addon.xml
    ├── icon.jpg
    ├── fanart.jpg
    └── repository.fkstream-X.X.X.zip
```

Les versions sont lues automatiquement depuis les fichiers `addon.xml` de chaque addon. Le contenu de `dist/` peut ensuite être publié sur GitHub Pages ou n'importe quel hébergement statique.
