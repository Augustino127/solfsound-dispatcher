# 🎵 SolfSound Dispatcher

Un outil puissant d'extraction et de séparation audio **disponible en 3 interfaces** : ligne de commande (CLI), application desktop native, et interface web accessible depuis n'importe quel appareil (ordinateur, tablette, smartphone).

## ✨ Fonctionnalités

- **🎬 Extraction Audio** : Extrayez l'audio de n'importe quelle vidéo (MP4, AVI, MOV, MKV, etc.)
- **🎼 Séparation de Stems** : Séparez la musique en différentes pistes :
  - 🎤 Voix (vocals)
  - 🥁 Batterie (drums)
  - 🎸 Basse (bass)
  - 🎹 Autres instruments (other)
  - Et plus avec certains modèles (guitare, piano, etc.)
- **📊 Analyse Audio** : Analysez la composition et la structure de l'audio
  - Détection du tempo et des battements
  - Estimation du nombre de couches sonores
  - Analyse spectrale et harmonique
  - Distribution d'énergie entre les stems
- **🔄 Pipeline Complet** : Traitez une vidéo de bout en bout automatiquement
- **💻 3 Interfaces au Choix** :
  - 🖥️ **Desktop** : Application native Windows/macOS/Linux
  - 🌐 **Web** : Interface web accessible depuis navigateur
  - ⌨️ **CLI** : Ligne de commande pour les utilisateurs avancés

## 🚀 Installation Rapide

### Installation Automatique

**Linux/macOS :**
```bash
git clone https://github.com/Augustino127/solfsound-dispatcher.git
cd solfsound-dispatcher
chmod +x install.sh
./install.sh
```

**Windows :**
```batch
git clone https://github.com/Augustino127/solfsound-dispatcher.git
cd solfsound-dispatcher
install.bat
```

### Installation Manuelle

#### Prérequis

- Python 3.8 ou supérieur
- FFmpeg (requis pour l'extraction audio)

**Installer FFmpeg :**

- **Linux (Debian/Ubuntu):** `sudo apt-get install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** Téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajoutez au PATH

**Installer SolfSound :**

```bash
# Cloner le dépôt
git clone https://github.com/Augustino127/solfsound-dispatcher.git
cd solfsound-dispatcher

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Installer SolfSound
pip install -e .
```

## 📱 Utilisation

### 1. Interface Desktop (Recommandée)

Application native avec interface graphique moderne.

```bash
# Lancer l'application desktop
python run_desktop.py

# Ou si installé via setup.py:
solfsound-desktop
```

**Fonctionnalités :**
- Interface glisser-déposer
- Sélection facile des options
- Barre de progression en temps réel
- Ouverture directe des résultats
- **Compatible :** Windows, macOS, Linux

![Desktop Interface](docs/images/desktop-preview.png)

### 2. Interface Web

Interface web moderne accessible depuis n'importe quel appareil.

```bash
# Lancer le serveur web
python run_web.py

# Ou avec des options personnalisées:
python run_web.py --host 0.0.0.0 --port 8000
```

**Accès :**
- Local : http://localhost:8000
- Réseau : http://[votre-ip]:8000
- Mobile : Accessible depuis smartphone/tablette sur le même réseau

**Fonctionnalités :**
- Interface responsive (mobile-friendly)
- Upload de fichiers par drag & drop
- Traitement en arrière-plan
- API REST complète
- Documentation API : http://localhost:8000/api/docs

![Web Interface](docs/images/web-preview.png)

### 3. Ligne de Commande (CLI)

Pour les utilisateurs avancés et l'automatisation.

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Windows: venv\Scripts\activate

# Extraire l'audio d'une vidéo
solfsound extract video.mp4

# Séparer une chanson en stems
solfsound separate chanson.wav

# Analyser un audio
solfsound analyze chanson.wav

# Pipeline complet
solfsound process video.mp4

# Aide
solfsound --help
```

## 📖 Guide d'Utilisation Détaillé

### Interface Desktop

1. **Lancer l'application** : `python run_desktop.py`
2. **Sélectionner un fichier** : Cliquez sur "Choisir un fichier"
3. **Choisir une action** :
   - 🎬 Extraire Audio : Convertir vidéo en audio
   - 🎼 Séparer en Stems : Isoler les instruments
   - 📊 Analyser : Obtenir des infos sur la composition
   - 🔄 Pipeline Complet : Tout faire automatiquement
4. **Configurer les options** selon vos besoins
5. **Lancer le traitement** et attendre
6. **Télécharger les résultats** via le bouton "Ouvrir le dossier"

### Interface Web

1. **Lancer le serveur** : `python run_web.py`
2. **Ouvrir le navigateur** : http://localhost:8000
3. **Télécharger un fichier** : Glissez-déposez ou cliquez
4. **Sélectionner une action** et configurer
5. **Lancer le traitement** et suivre la progression
6. **Télécharger les résultats** directement

### CLI (Ligne de Commande)

#### Extraire l'audio

```bash
# Extraction simple
solfsound extract video.mp4

# Avec options
solfsound extract video.mp4 -f mp3 -b 320k -s 48000
```

**Options :**
- `-f, --format` : Format de sortie (mp3, wav, flac, ogg)
- `-b, --bitrate` : Bitrate (320k, 256k, 192k)
- `-s, --sample-rate` : Taux d'échantillonnage (44100, 48000)

#### Séparer en stems

```bash
# Séparer tous les stems
solfsound separate chanson.wav

# Extraire seulement la voix et la batterie
solfsound separate chanson.wav -s vocals -s drums

# Haute qualité
solfsound separate chanson.wav -m htdemucs_ft --shifts 5
```

**Options :**
- `-m, --model` : Modèle (htdemucs, htdemucs_ft, htdemucs_6s, mdx_extra)
- `-s, --stems` : Stems à extraire (vocals, drums, bass, other)
- `--shifts` : Qualité (1-10, plus élevé = meilleur mais plus lent)

#### Analyser

```bash
# Analyse simple
solfsound analyze chanson.wav

# Analyse détaillée
solfsound analyze chanson.wav --detailed
```

#### Pipeline Complet

```bash
# Traiter complètement une vidéo
solfsound process video.mp4

# Avec modèle personnalisé
solfsound process video.mp4 -m htdemucs_ft
```

## 🎯 Modèles de Séparation

| Modèle | Description | Stems | Vitesse |
|--------|-------------|-------|---------|
| `htdemucs` | Haute qualité, rapide (défaut) | vocals, drums, bass, other | ⚡⚡⚡ |
| `htdemucs_ft` | Version fine-tunée, meilleure qualité | vocals, drums, bass, other | ⚡⚡ |
| `htdemucs_6s` | Séparation 6 stems | vocals, drums, bass, guitar, piano, other | ⚡⚡ |
| `mdx_extra` | Qualité maximale (plus lent) | vocals, drums, bass, other | ⚡ |

## 🎨 Exemples d'Usage

### Extraire la voix d'une vidéo YouTube

**Desktop/Web :**
1. Télécharger la vidéo
2. Choisir "Pipeline Complet"
3. Récupérer le fichier `vocals.wav`

**CLI :**
```bash
solfsound extract video_youtube.mp4 -f wav
solfsound separate extracted_audio/video_youtube.wav -s vocals
```

### Créer une version karaoké (sans voix)

**Desktop/Web :**
1. Télécharger la chanson
2. Choisir "Séparer en Stems"
3. Décocher "Voix"
4. Récupérer drums.wav, bass.wav, other.wav

**CLI :**
```bash
solfsound separate chanson.wav -s drums -s bass -s other
```

### Analyser une mélodie

**Desktop/Web :**
1. Télécharger le fichier
2. Choisir "Analyser"
3. Voir le tempo, nombre de couches, etc.

**CLI :**
```bash
solfsound analyze melodie.wav
```

**Résultat exemple :**
```
Duration: 180.50 seconds
Tempo: 128.0 BPM
Estimated Sound Layers: 5
Harmonic Ratio: 65.32%
Percussive Ratio: 34.68%
```

## 📡 API REST

L'interface web expose une API REST complète :

**Endpoints principaux :**
- `POST /api/upload` : Télécharger un fichier
- `POST /api/extract` : Extraire l'audio
- `POST /api/separate` : Séparer en stems
- `POST /api/analyze` : Analyser l'audio
- `POST /api/process` : Pipeline complet
- `GET /api/jobs/{job_id}` : Statut d'un traitement
- `GET /api/models` : Liste des modèles disponibles

**Documentation interactive :**
http://localhost:8000/api/docs

**Exemple d'utilisation :**
```python
import requests

# Upload
files = {'file': open('video.mp4', 'rb')}
response = requests.post('http://localhost:8000/api/upload', files=files)
filepath = response.json()['filepath']

# Separate
data = {
    'audio_file': filepath,
    'model': 'htdemucs_ft',
    'stems': ['vocals', 'drums']
}
response = requests.post('http://localhost:8000/api/separate', json=data)
job_id = response.json()['job_id']

# Check status
response = requests.get(f'http://localhost:8000/api/jobs/{job_id}')
print(response.json())
```

## 📱 Utilisation Mobile

L'interface web est entièrement responsive et optimisée pour mobile :

1. **Lancer le serveur** sur votre ordinateur
2. **Trouver votre IP locale** : `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
3. **Accéder depuis mobile** : http://[votre-ip]:8000
4. **Profiter** de toutes les fonctionnalités sur smartphone/tablette

## 🔧 Configuration Avancée

### Utilisation GPU

Pour une séparation plus rapide avec GPU CUDA :

```bash
# Installer PyTorch avec CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Vérifier
solfsound info
```

### Qualité vs Vitesse

**Meilleure qualité (lent) :**
```bash
solfsound separate chanson.wav -m mdx_extra --shifts 10
```

**Rapide (qualité standard) :**
```bash
solfsound separate chanson.wav -m htdemucs --shifts 1
```

### Serveur Web en Production

```bash
# Accessible depuis le réseau
python run_web.py --host 0.0.0.0 --port 8000

# Avec HTTPS (nécessite certificat)
uvicorn solfsound.web_server:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## 📁 Structure des Fichiers

```
solfsound-dispatcher/
├── src/solfsound/           # Code source
│   ├── cli.py              # Interface CLI
│   ├── desktop_app.py      # Application desktop
│   ├── web_api.py          # API REST
│   ├── web_server.py       # Serveur web
│   ├── extractor.py        # Extraction audio
│   ├── separator.py        # Séparation stems
│   ├── analyzer.py         # Analyse audio
│   └── web/static/         # Interface web (HTML/CSS/JS)
├── output/                  # Fichiers de sortie
│   ├── extracted/          # Audio extraits
│   └── stems/              # Stems séparés
├── run_desktop.py          # Lancer desktop
├── run_web.py              # Lancer web
├── install.sh              # Installation Linux/macOS
├── install.bat             # Installation Windows
└── README.md               # Ce fichier
```

## 🐛 Dépannage

### FFmpeg non trouvé

```bash
# Vérifier l'installation
ffmpeg -version

# Si non installé, voir section Installation
```

### Port 8000 déjà utilisé (Web)

```bash
# Utiliser un autre port
python run_web.py --port 8080
```

### Erreur de mémoire (Séparation)

```bash
# Réduire la qualité
solfsound separate chanson.wav --shifts 1

# Ou utiliser un modèle plus léger
solfsound separate chanson.wav -m htdemucs --shifts 1
```

### Application desktop ne se lance pas

```bash
# Réinstaller Flet
pip install --upgrade flet

# Vérifier les dépendances
pip install -r requirements.txt
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Soumettre des pull requests

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- [Demucs](https://github.com/facebookresearch/demucs) - Pour la séparation de sources
- [FFmpeg](https://ffmpeg.org/) - Pour le traitement audio/vidéo
- [Librosa](https://librosa.org/) - Pour l'analyse audio
- [Flet](https://flet.dev/) - Pour l'interface desktop
- [FastAPI](https://fastapi.tiangolo.com/) - Pour l'API REST

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Vérifier les exemples dans `/examples`

---

**Fait avec ❤️ pour les amateurs de musique et d'audio**

🎵 Profitez de SolfSound Dispatcher sur **desktop, web et mobile** ! 🎵
