# 🎵 SolfSound Dispatcher

Un outil puissant d'extraction et de séparation audio pour extraire le son des vidéos et séparer la musique en différentes pistes (stems).

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

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- FFmpeg (requis pour l'extraction audio)

#### Installer FFmpeg

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajoutez au PATH

### Installation de SolfSound

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

## 📖 Utilisation

### 1. Extraire l'audio d'une vidéo

```bash
# Extraction simple
solfsound extract video.mp4

# Spécifier le format et la qualité
solfsound extract video.mp4 -f mp3 -b 320k

# Choisir un taux d'échantillonnage
solfsound extract video.mp4 -f wav -s 48000
```

**Options disponibles :**
- `-o, --output` : Dossier de sortie (défaut: `extracted_audio`)
- `-f, --format` : Format de sortie (`mp3`, `wav`, `flac`, `ogg`, `aac`, `m4a`)
- `-b, --bitrate` : Bitrate audio (ex: `320k`, `256k`, `192k`)
- `-s, --sample-rate` : Taux d'échantillonnage en Hz (ex: `44100`, `48000`)

### 2. Séparer l'audio en stems

```bash
# Séparer tous les stems
solfsound separate chanson.wav

# Extraire seulement certains stems
solfsound separate chanson.wav -s vocals -s drums

# Utiliser un modèle haute qualité
solfsound separate chanson.wav -m htdemucs_ft --shifts 5

# Choisir le format de sortie
solfsound separate chanson.wav -f mp3
```

**Options disponibles :**
- `-o, --output` : Dossier de sortie (défaut: `separated_stems`)
- `-m, --model` : Modèle de séparation (voir section Modèles)
- `-s, --stems` : Stems spécifiques à extraire (peut être utilisé plusieurs fois)
- `-f, --format` : Format de sortie (`wav`, `mp3`, `flac`)
- `--shifts` : Nombre de décalages pour meilleure qualité (1-10, plus élevé = plus lent)

### 3. Analyser un audio

```bash
# Analyse rapide
solfsound analyze chanson.wav

# Analyse détaillée
solfsound analyze chanson.wav --detailed
```

L'analyse fournit :
- Durée et propriétés de base
- Tempo (BPM) et nombre de battements
- Estimation du nombre de couches sonores
- Ratios harmonique/percussif
- Score de complexité

### 4. Pipeline complet

Traitement complet : extraction + séparation + analyse

```bash
# Traiter une vidéo complètement
solfsound process video.mp4

# Avec options personnalisées
solfsound process video.mp4 -m htdemucs_ft -f mp3 -o mon_output
```

Ce qui effectue :
1. ✅ Extraction de l'audio de la vidéo
2. ✅ Séparation en stems
3. ✅ Analyse complète avec distribution d'énergie

### 5. Commandes utiles

```bash
# Lister les modèles disponibles
solfsound models

# Vérifier les informations système
solfsound info

# Aide générale
solfsound --help

# Aide pour une commande spécifique
solfsound extract --help
```

## 🎯 Modèles de Séparation

| Modèle | Description | Stems |
|--------|-------------|-------|
| `htdemucs` | Haute qualité, rapide (défaut) | vocals, drums, bass, other |
| `htdemucs_ft` | Version fine-tunée, meilleure qualité | vocals, drums, bass, other |
| `htdemucs_6s` | Séparation 6 stems | vocals, drums, bass, guitar, piano, other |
| `mdx_extra` | Qualité extra (plus lent) | vocals, drums, bass, other |

**Choisir un modèle :**
```bash
solfsound separate chanson.wav -m htdemucs_6s
```

## 🎨 Exemples d'Usage

### Extraire la voix d'une chanson YouTube

```bash
# 1. Télécharger la vidéo (avec yt-dlp ou autre)
# 2. Extraire l'audio
solfsound extract chanson_youtube.mp4 -f wav

# 3. Séparer et garder uniquement la voix
solfsound separate extracted_audio/chanson_youtube.wav -s vocals
```

### Créer une version instrumentale

```bash
# Extraire tout sauf la voix
solfsound separate chanson.wav -s drums -s bass -s other

# Ou simplement ne pas extraire la voix
# Les stems séparés peuvent être remixés dans un DAW
```

### Analyser la composition d'une mélodie

```bash
# Analyse complète
solfsound process video.mp4

# Résultat : vous saurez combien de couches sonores,
# quel stem est dominant, le tempo, etc.
```

## 🔧 Configuration Avancée

### Utilisation GPU

Pour une séparation plus rapide, utilisez un GPU CUDA :

```bash
# Installer PyTorch avec support CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Vérifier que CUDA est disponible
solfsound info
```

### Qualité vs Vitesse

Pour une meilleure qualité (mais plus lent) :
```bash
solfsound separate chanson.wav -m mdx_extra --shifts 10
```

Pour une séparation rapide (qualité standard) :
```bash
solfsound separate chanson.wav -m htdemucs --shifts 1
```

## 📁 Structure des Fichiers de Sortie

```
output/
├── extracted_audio/          # Audio extraits des vidéos
│   └── video.wav
├── separated_stems/          # Stems séparés
│   └── chanson/
│       ├── vocals.wav
│       ├── drums.wav
│       ├── bass.wav
│       └── other.wav
└── solfsound.log            # Fichier de log
```

## 🐛 Dépannage

### FFmpeg non trouvé

```bash
# Vérifier l'installation
ffmpeg -version

# Si non installé, voir section Installation
```

### Erreur de mémoire lors de la séparation

```bash
# Utiliser des fichiers plus courts ou réduire la qualité
solfsound separate chanson.wav --shifts 1
```

### Modèle non trouvé

Les modèles Demucs sont téléchargés automatiquement à la première utilisation.
Assurez-vous d'avoir une connexion internet.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- [Demucs](https://github.com/facebookresearch/demucs) - Pour la séparation de sources
- [FFmpeg](https://ffmpeg.org/) - Pour le traitement audio/vidéo
- [Librosa](https://librosa.org/) - Pour l'analyse audio

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation

---

Fait avec ❤️ pour les amateurs de musique et d'audio
