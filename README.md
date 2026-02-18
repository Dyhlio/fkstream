<div align="center">
  <img src="https://raw.githubusercontent.com/Dyhlio/fkstream/refs/heads/main/fkstream/assets/fkstream-logo.jpg" alt="FKStream Logo" width="150">
  <h1>FKStream</h1>
  <p><strong>Addon Stremio & Kodi non officiel pour accéder au contenu de Fankai.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/status-fonctionnel-success?style=for-the-badge" alt="Status">
    <img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python" alt="Python Version">
  </p>
</div>

---

## 🌟 À propos

**FKStream** est un addon non officiel pour Stremio et Kodi, conçu pour accéder au contenu proposé par Fankai. Il permet de parcourir une large bibliothèque d'animes, avec une prise en charge avancée des services de débridage pour un streaming fluide et optimisé.

> **Addon Kodi** : Pour l'installation et l'utilisation sur Kodi, consultez le [README dédié](kodi/README.md).

## 🚨 Note importante sur les versions

Les anciennes versions de FKStream ne sont plus maintenues. Merci de ne plus les utiliser car il n'y aura aucun support sur les anciennes versions !

Nous vous recommandons vivement d'utiliser uniquement la dernière version qui inclut d'importantes améliorations de sécurité et de fonctionnalités.

## ⚠️ Avis de non-responsabilité légal

**FKStream** est fourni à des fins éducatives et de recherche uniquement. Cet addon ne stocke, n'héberge ni ne distribue aucun contenu. L'addon agit comme un simple intermédiaire technique.

Les utilisateurs sont entièrement responsables de l'usage qu'ils font de cet addon et doivent s'assurer que leur utilisation est conforme aux lois applicables dans leur juridiction. Nous recommandons fortement de n'utiliser cet addon que pour accéder à du contenu légal ou pour lequel vous disposez des droits d'accès.

Les développeurs de **FKStream** n'encouragent pas et ne sont pas responsables de toute utilisation illégale de cet addon. En utilisant **FKStream**, vous acceptez d'en assumer l'entière responsabilité légale.

## ✨ Fonctionnalités

- **Catalogue Fankai Complet** : Accès à l'ensemble des animes disponibles sur Fankai.
- **Sources Personnalisées** : Possibilité d'ajouter des sources externes via CUSTOM_SOURCE_URL.
- **Intégration Debrid** : Supporte de nombreux services de débridage (Real-Debrid, AllDebrid, Premiumize, etc.) pour un streaming haute vitesse.
- **Mode Torrent Direct** : Possibilité d'envoyer les torrents directement à Stremio ou Kodi (via Elementum) sans passer par un service debrid.
- **Mise en Cache Intelligente** : Cache les métadonnées et la disponibilité des liens pour des chargements plus rapides.
- **Matching Précis** : Algorithme avancé pour trouver le bon fichier vidéo correspondant à un épisode, même dans des packs contenant toute une saison.
- **Interface de Configuration Web** : Une page de configuration simple et claire pour paramétrer l'addon facilement.
- **Support Proxy** : Permet de router les requêtes via un proxy pour plus de flexibilité.
- **Déploiement Facile** : Prêt à être déployé avec Docker pour un hébergement simple et rapide.

## 🚀 Installation

Il y a deux méthodes principales pour installer et utiliser cet addon : en local ou via Docker.

### Méthode 1 : Installation Locale (Simple)

Idéal pour une utilisation sur votre machine personnelle.

1.  **Prérequis** : Assurez-vous d'avoir [Python 3.11](https://www.python.org/downloads/) ou une version plus récente installé.
2.  **Clonez le projet** :
    ```bash
    git clone https://github.com/Dyhlio/fkstream.git
    cd fkstream
    ```
3.  **Créez un environnement virtuel et installez les dépendances** :
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Sur Windows, utilisez: .venv\Scripts\activate
    pip install -e .
    ```
4.  **Lancez l'application** :
    ```bash
    python -m fkstream.main
    ```
5.  L'addon est maintenant en cours d'exécution sur votre machine.

### Méthode 2 : Déploiement avec Docker (Recommandé)

1. **Créer un fichier `docker-compose.yml`**:

```yaml
services:
  fkstream:
    image: dyhlio/fkstream:latest
    container_name: fkstream
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - FANKAI_URL=https://example.com
      - API_KEY=your_api_key_here
      - DATABASE_TYPE=sqlite
      - DATABASE_PATH=/data/fkstream.db
    restart: unless-stopped
```

2. **Démarrer le conteneur**:
```bash
docker-compose up -d
```

3. **Vérifier les logs**:
```bash
docker-compose logs -f fkstream
```

## ⚙️ Configuration

### Configuration requise

Avant de lancer l'addon, vous devez définir les paramètres obligatoires dans votre fichier `.env` :
- `FANKAI_URL` : URL de l'API pour les métadonnées et les sources
- `API_KEY` : Clé API pour accéder au contenu

**Pour plus d'informations, rejoignez ce serveur Discord : https://discord.gg/B5BmaptXtz**

### Interface de configuration

Une fois l'addon lancé (avec l'une des deux méthodes), ouvrez votre navigateur et allez à l'adresse suivante :

**`http://<adresse-ip-de-votre-machine>:8000/configure`**

(Si vous l'exécutez sur votre machine locale, ce sera `http://127.0.0.1:8000/configure`).

Sur cette page, vous pourrez :
- Choisir votre service de Debrid.
- Entrer votre clé API.
- Sélectionner d'autres options comme le filtrage des flux.

Une fois la configuration terminée, cliquez sur **"Installer sur Stremio"** ou utilisez la section **Kodi** pour associer votre addon via un code d'appairage.

## 🔧 Variables d'environnement

Toutes les configurations avancées se font via le fichier `.env`.

| Variable                                     | Description                                                                          | Défaut                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------ |
| `ADDON_ID`                                   | (Optionnel) Identifiant unique de l'addon.                                           | `community.fkstream`                 |
| `ADDON_NAME`                                 | (Optionnel) Nom de l'addon affiché dans Stremio et Kodi.                             | `FKStream`                           |
| `FASTAPI_HOST`                               | (Optionnel) L'adresse sur laquelle le serveur écoute.                                | `0.0.0.0`                            |
| `FASTAPI_PORT`                               | (Optionnel) Le port sur lequel le serveur écoute.                                    | `8000`                               |
| `FASTAPI_WORKERS`                            | (Optionnel) Nombre de processus. Mettre à -1 pour un calcul automatique.             | `1`                                  |
| `USE_GUNICORN`                               | (Optionnel) Utiliser Gunicorn en production (recommandé sur Linux).                  | `True`                               |
| `DATABASE_TYPE`                              | (Requis) Type de base de données. Options : `sqlite`, `postgresql`.                  | `sqlite`                             |
| `DATABASE_URL`                               | (Requis si `DATABASE_TYPE=postgresql`) URL de connexion PostgreSQL.                  | `user:pass@host:port`                |
| `DATABASE_PATH`                              | (Requis si `DATABASE_TYPE=sqlite`) Chemin vers le fichier de base de données.        | `data/fkstream.db`                   |
| `METADATA_TTL`                               | (Optionnel) Durée de vie du cache pour les métadonnées.                                | `86400` (1 jour)                   |
| `DEBRID_AVAILABILITY_TTL`                    | (Optionnel) Durée de vie du cache pour la disponibilité debrid.                        | `86400` (1 jour)                     |
| `SCRAPE_LOCK_TTL`                            | (Optionnel) Durée de validité d'un verrou de recherche.                                | `300` (5 minutes)                    |
| `SCRAPE_WAIT_TIMEOUT`                        | (Optionnel) Temps d'attente max pour un verrou.                                        | `30` (30 secondes)                   |
| `DEBRID_PROXY_URL`                           | (Optionnel) URL de votre proxy pour contourner les blocages.                           | ` ` (vide)                           |
| `PROXY_DEBRID_STREAM`                        | (Optionnel) Mettre à `True` pour activer le mode proxy.                                | `False`                              |
| `PROXY_DEBRID_STREAM_PASSWORD`               | (Requis si `PROXY_DEBRID_STREAM=True`) Mot de passe pour les utilisateurs.             | `CHANGE_ME`                          |
| `PROXY_DEBRID_STREAM_DEBRID_DEFAULT_SERVICE` | (Requis si `PROXY_DEBRID_STREAM=True`) Votre service debrid.                           | `realdebrid`                         |
| `PROXY_DEBRID_STREAM_DEBRID_DEFAULT_APIKEY`  | (Requis si `PROXY_DEBRID_STREAM=True`) Votre clé API debrid.                           | `CHANGE_ME`                          |
| `CUSTOM_HEADER_HTML`                         | (Optionnel) Code HTML à injecter dans l'en-tête de la page de configuration.         | ` ` (vide)                           |
| `STREMTHRU_URL`                              | (Optionnel) URL du service StremThru.                                                | `https://stremthru.13377001.xyz`     |
| `FANKAI_URL`                                 | **(OBLIGATOIRE)** URL de l'API Fankai - Voir section Configuration requise           | ` ` (vide)                           |
| `API_KEY`                                    | **(OBLIGATOIRE)** Clé API pour accéder au contenu - Voir section Configuration requise | ` ` (vide)                           |
| `LOG_LEVEL`                                  | (Optionnel) Niveau de log. Options : `DEBUG`, `PRODUCTION`.                          | `PRODUCTION`                         |
| `CUSTOM_SOURCE_URL`                          | (Optionnel) URL du fichier JSON contenant les sources personnalisées.                | ` ` (vide)                           |
| `CUSTOM_SOURCE_PATH`                         | (Optionnel) Chemin du fichier JSON pour les sources personnalisées.                  | `data/custom_sources.json`           |
| `CUSTOM_SOURCE_INTERVAL`                     | (Optionnel) Intervalle de mise à jour en secondes.                                   | `3600` (1 heure)                     |
| `CUSTOM_SOURCE_TTL`                          | (Optionnel) Durée du cache pour les sources custom en secondes.                      | `3600` (1 heure)                     |

## 🙏 Remerciements

- Un grand merci à **[g0ldyy]** pour le code original de **[comet](https://github.com/g0ldyy/comet)**.
- Merci à l'équipe de **[Fankai](https://linktr.ee/FanKai)** pour leur travail incroyable sur la bibliothèque de contenu.

---

## 📜 Licence

Le code original de ce projet par g0ldyy est distribué sous la Licence MIT. Les modifications et contributions ultérieures sont également soumises à cette licence. Voir le fichier `LICENSE` pour le texte complet.

