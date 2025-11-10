# Guide de Démarrage Rapide

## Installation Rapide

```bash
# 1. Cloner et installer
git clone https://github.com/Augustino127/solfsound-dispatcher.git
cd solfsound-dispatcher
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 2. Vérifier l'installation
solfsound info
```

## Exemples Basiques

### Extraire l'audio d'une vidéo

```bash
solfsound extract ma_video.mp4
# Résultat : extracted_audio/ma_video.wav
```

### Séparer une chanson

```bash
solfsound separate chanson.wav
# Résultat : separated_stems/chanson/vocals.wav, drums.wav, bass.wav, other.wav
```

### Analyser un audio

```bash
solfsound analyze chanson.wav
# Affiche : tempo, durée, nombre de couches sonores, etc.
```

### Pipeline Complet

```bash
solfsound process video.mp4
# Fait tout : extraction + séparation + analyse
```

## Cas d'Usage Courants

### 1. Extraire uniquement la voix

```bash
# Étape 1 : Extraire audio de vidéo
solfsound extract video_chanson.mp4

# Étape 2 : Séparer et garder la voix
solfsound separate extracted_audio/video_chanson.wav -s vocals
```

**Résultat :** `separated_stems/video_chanson/vocals.wav`

### 2. Créer une version karaoké (sans voix)

```bash
# Séparer tous les stems sauf vocals
solfsound separate chanson.wav -s drums -s bass -s other

# Ou extraire tous et ignorer vocals.wav
solfsound separate chanson.wav
```

### 3. Analyser une mélodie

```bash
# Analyse simple
solfsound analyze melodie.wav

# Sortie exemple :
# Duration: 180.50 seconds
# Tempo: 128.0 BPM
# Estimated Sound Layers: 5
# Harmonic Ratio: 65.32%
# Percussive Ratio: 34.68%
```

### 4. Traitement batch

```bash
# Pour plusieurs fichiers
for video in *.mp4; do
    solfsound process "$video"
done
```

## Astuces

### Meilleure qualité

```bash
# Utiliser le modèle fine-tuned avec plus de shifts
solfsound separate chanson.wav -m htdemucs_ft --shifts 5
```

### Plus rapide

```bash
# Modèle standard avec 1 shift
solfsound separate chanson.wav -m htdemucs --shifts 1
```

### Séparer en 6 stems

```bash
# Inclut guitare et piano séparément
solfsound separate chanson.wav -m htdemucs_6s
```

## Workflow Recommandé

```bash
# 1. Extraire audio haute qualité
solfsound extract video.mp4 -f wav -s 48000

# 2. Analyser d'abord
solfsound analyze extracted_audio/video.wav

# 3. Séparer avec bonne qualité
solfsound separate extracted_audio/video.wav -m htdemucs_ft --shifts 3

# 4. Utiliser les stems dans votre DAW préféré
```

## Formats Supportés

**Vidéo (entrée):**
- MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V

**Audio (entrée/sortie):**
- MP3, WAV, FLAC, OGG, AAC, M4A, WMA

## Prochaines Étapes

- Consulter le [README complet](../README.md)
- Explorer les [modèles disponibles](../README.md#-modèles-de-séparation)
- Voir la [configuration avancée](../README.md#-configuration-avancée)
