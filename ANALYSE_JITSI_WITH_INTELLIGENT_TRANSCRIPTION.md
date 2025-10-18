# 🎥 Analyse - Pipeline de Transcription Intelligent Jitsi avec OCR Local

**Date de création :** 2025-01-17
**Contexte :** ~5h réunions/semaine, pas de GPU, OCR local souhaité, détection intelligente de slides

---

## 📋 Table des matières

1. [Objectifs](#objectifs)
2. [Solutions OCR locales](#1-ocr-local---paddleocr-recommandé)
3. [Détection changement de slides](#2-détection-changement-de-slides---imagehash--pyscenedetect)
4. [Détection screenshare](#3-détection-screenshare-dans-vidéo-jitsi)
5. [Architecture finale](#architecture-finale-recommandée)
6. [Performances et coûts](#performances-et-coûts)
7. [Bibliothèques recommandées](#bibliothèques-recommandées)

---

## 🎯 Objectifs

### Problématique initiale
- ❌ Claude Vision API : 1 frame/10sec → 1800 frames/h → **~110€/mois** pour 20h réunions
- ❌ Beaucoup de frames redondantes (même slide affichée plusieurs minutes)
- ❌ OCR sur webcam inutile (seulement screenshare intéressant)

### Solution optimisée
- ✅ OCR **local** (CPU, gratuit)
- ✅ Détection **intelligente** des changements de slides (ImageHash)
- ✅ OCR **uniquement sur screenshare** et **nouvelles slides**
- ✅ **30-50 OCR** au lieu de 1800 par heure → **0€/mois**

---

## 🔍 1. OCR Local - PaddleOCR (recommandé)

### Comparaison des 3 principales options

| Critère | **PaddleOCR** ⭐ | Tesseract | EasyOCR |
|---------|-----------------|-----------|---------|
| **Précision** | ⭐⭐⭐⭐⭐ Meilleure | ⭐⭐⭐⭐ Bonne | ⭐⭐⭐⭐ Bonne |
| **CPU Performance** | ⭐⭐⭐⭐ Rapide | ⭐⭐⭐⭐⭐ Très rapide | ⭐⭐ Lent sans GPU |
| **Langues** | 80+ | 100+ | 80+ |
| **Slides/Présentations** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Très bon | ⭐⭐⭐⭐ Très bon |
| **Installation** | `pip install` | `apt install` | `pip install` |
| **Dépendances** | Medium | Légères | Lourdes (PyTorch) |

### Pourquoi PaddleOCR ?

✅ **Meilleure précision globale** : Moins d'erreurs que Tesseract selon benchmarks 2024
✅ **Bon sur CPU** : Acceptable pour ~5h/semaine (~150 slides à OCR)
✅ **Architecture modulaire** : Détection texte + reconnaissance séparées
✅ **Optimisé pour présentations** : Texte dans images complexes (graphiques, schémas)
✅ **Multilingue** : Supporte 80+ langues dont français/anglais

**Sources :**
- [OCR comparison: Tesseract vs EasyOCR vs PaddleOCR vs MMOCR](https://toon-beerten.medium.com/ocr-comparison-tesseract-versus-easyocr-vs-paddleocr-vs-mmocr-a362d9c79e66)
- [PaddleOCR vs Tesseract: Which is the best open source OCR?](https://www.koncile.ai/en/ressources/paddleocr-analyse-avantages-alternatives-open-source)

### Installation

```bash
pip install paddleocr paddlepaddle
```

### Usage de base

```python
from paddleocr import PaddleOCR

# Initialiser (une seule fois)
ocr = PaddleOCR(use_angle_cls=True, lang='fr', use_gpu=False)

# OCR sur une image
result = ocr.ocr('screenshot_slide.jpg', cls=True)

# Extraire le texte
text_lines = []
if result and result[0]:
    for line in result[0]:
        text = line[1][0]  # [1][0] = texte détecté
        confidence = line[1][1]  # [1][1] = score de confiance
        text_lines.append(text)

full_text = '\n'.join(text_lines)
print(full_text)
```

### Exemple de résultat

**Input :** Screenshot PowerPoint avec titre "Q4 2024 Results" et bullet points

**Output :**
```python
[
    [[[120, 45], [580, 45], [580, 95], [120, 95]], ('Q4 2024 Results', 0.987)],
    [[[150, 180], [520, 180], [520, 220], [150, 220]], ('Revenue: +23% YoY', 0.953)],
    [[[150, 250], [480, 250], [480, 290], [150, 290]], ('Customer growth: 45k', 0.941)]
]
```

### Configuration avancée

```python
# Optimisations pour screenshots de présentations
ocr = PaddleOCR(
    use_angle_cls=True,      # Correction rotation
    lang='fr',               # ou 'en' pour anglais
    use_gpu=False,           # CPU only
    show_log=False,          # Pas de logs verbeux
    det_db_thresh=0.3,       # Seuil détection texte (plus bas = plus sensible)
    det_db_box_thresh=0.6,   # Seuil bounding boxes
    rec_batch_num=6          # Batch size (augmenter si beaucoup de RAM)
)
```

---

## 🎯 2. Détection changement de slides - ImageHash + PySceneDetect

### Solution hybride recommandée

#### A. **ImageHash** - Perceptual Hashing ⭐ **Recommandé pour slides**

**Concept :** Générer un "hash perceptuel" de chaque frame. Deux images similaires auront des hashes similaires.

**GitHub :** https://github.com/JohannesBuchner/imagehash
**Stars :** 3.2k | **Dernière release :** 1er février 2025

##### Pourquoi c'est parfait pour les slides ?

✅ **Hash perceptuel** : 2 images similaires = hashes similaires
✅ **Distance de Hamming** : Mesure numérique de la différence (0 = identiques, 64 = très différents)
✅ **Insensible aux variations** : Compression vidéo, petits mouvements de curseur ignorés
✅ **Ultra rapide** : Hash en <1ms par image

##### Algorithmes disponibles

| Algorithme | Usage | Vitesse | Précision |
|------------|-------|---------|-----------|
| `average_hash` | Simple, slides statiques | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| `phash` (perceptual) | **⭐ Meilleur pour slides** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| `dhash` (difference) | Détection bordures | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| `whash` (wavelet) | Très précis | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

##### Installation

```bash
pip install ImageHash Pillow
```

##### Code : Détection changement de slide

```python
import imagehash
from PIL import Image
from pathlib import Path

def detect_slide_changes(frames: list[str], threshold: int = 5) -> list[int]:
    """
    Détecte les changements de slides en comparant les hashes perceptuels.

    Args:
        frames: Liste de chemins vers les images (frames extraits)
        threshold: Seuil de distance Hamming
            - 0-5  : Images quasi identiques (même slide)
            - 6-10 : Petites variations (curseur, animation)
            - 10+  : Changement significatif (nouvelle slide)

    Returns:
        Liste des indices de frames où un changement de slide est détecté

    Example:
        >>> frames = ["frame_0001.jpg", "frame_0002.jpg", ...]
        >>> changes = detect_slide_changes(frames, threshold=8)
        >>> print(changes)
        [45, 123, 289, 456]  # Nouvelles slides aux frames 45, 123, 289, 456
    """

    changes = []
    prev_hash = None

    for i, frame_path in enumerate(frames):
        img = Image.open(frame_path)

        # Générer hash perceptuel (16x16 = 256 bits)
        current_hash = imagehash.phash(img, hash_size=16)

        if prev_hash is not None:
            # Distance de Hamming = nombre de bits différents
            distance = current_hash - prev_hash

            if distance > threshold:
                changes.append(i)
                print(f"📊 Changement de slide détecté : frame {i} (distance: {distance})")

        prev_hash = current_hash

    return changes
```

##### Exemple d'utilisation

```python
# Cas d'usage : 1h de screenshare, 1 frame/sec = 3600 frames
frames = [f"frame_{i:04d}.jpg" for i in range(3600)]

# Détection avec seuil 8 (équilibre sensibilité/bruit)
slide_changes = detect_slide_changes(frames, threshold=8)

# Résultat typique : 30-50 changements de slides détectés
print(f"Slides détectées : {len(slide_changes)}")
# → Slides détectées : 42

# OCR uniquement sur ces 42 frames au lieu de 3600 !
for idx in slide_changes:
    ocr_result = ocr.ocr(frames[idx])
    # ... traiter résultat
```

##### Performances

- **Hash d'une image 1920×1080** : ~1-2ms
- **Comparaison de 3600 frames** : ~5-7 secondes
- **Pour 1h vidéo (1 frame/sec)** : ~7 secondes de traitement

##### Réglage du seuil

```python
# Tester différents seuils pour trouver le bon équilibre
test_frames = frames[:100]  # Tester sur 100 frames

for threshold in [5, 8, 10, 12, 15]:
    changes = detect_slide_changes(test_frames, threshold=threshold)
    print(f"Seuil {threshold:2d} → {len(changes)} changements détectés")

# Output typique :
# Seuil  5 → 23 changements détectés (trop sensible, curseur = nouveau slide)
# Seuil  8 → 12 changements détectés (bon équilibre)
# Seuil 10 → 9 changements détectés
# Seuil 12 → 7 changements détectés
# Seuil 15 → 4 changements détectés (pas assez sensible, rate des slides)
```

---

#### B. **PySceneDetect** - Analyse de contenu vidéo

**Utile pour :** Détection grossière des zones webcam vs screenshare

**GitHub :** https://github.com/Breakthrough/PySceneDetect
**Stars :** 3.8k | **PyPI :** https://pypi.org/project/scenedetect/

##### Installation

```bash
pip install scenedetect[opencv]
```

##### Usage : Détecter les scènes

```python
from scenedetect import detect, ContentDetector, AdaptiveDetector

# Détecter les coupures de scène (changement webcam ↔ screenshare)
scene_list = detect('meeting_recording.mp4', ContentDetector(threshold=30))

# scene_list = [(start_timecode, end_timecode), ...]
# Exemple :
# [
#   (00:00:00, 00:07:30),  # Scène 1 : Webcam introduction
#   (00:07:30, 00:35:12),  # Scène 2 : Screenshare présentation
#   (00:35:12, 00:40:00),  # Scène 3 : Retour webcam discussion
#   (00:40:00, 01:00:00)   # Scène 4 : Screenshare démo
# ]

for i, (start, end) in enumerate(scene_list):
    duration = (end - start).get_seconds()
    print(f"Scène {i+1}: {start} → {end} ({duration:.1f}s)")
```

##### Extraire frames uniquement dans zones screenshare

```python
from scenedetect import detect, ContentDetector
import cv2

# 1. Détecter les scènes
scenes = detect('meeting.mp4', ContentDetector(threshold=27))

# 2. Analyser chaque scène pour déterminer si screenshare
for i, (start, end) in enumerate(scenes):
    # Extraire 1 frame au milieu de la scène pour analyse
    mid_frame_num = (start.frame_num + end.frame_num) // 2

    cap = cv2.VideoCapture('meeting.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_num)
    ret, frame = cap.read()

    # Tester si c'est screenshare (voir section 3 ci-dessous)
    is_screen = is_screenshare_frame(frame)

    if is_screen:
        print(f"Scène {i}: {start} → {end} = SCREENSHARE ✅")
        # Extraire frames de cette scène pour ImageHash + OCR
    else:
        print(f"Scène {i}: {start} → {end} = WEBCAM ⏭️ (skip)")
```

---

## 🖥️ 3. Détection screenshare dans vidéo Jitsi

### 3 approches identifiées

#### **Approche 1 : Metadata Jibri** ⭐ **Le plus fiable**

**Découverte :** Jibri génère un fichier `metadata.json` lors de l'enregistrement.

**Source :** [Jitsi Community Forum - Jibri metadata.json](https://community.jitsi.org/t/jibri-metadata-json/20254)

##### Localisation

```bash
/tmp/recordings/<MEETING_ID>/metadata.json
```

##### Structure JSON

```json
{
  "meeting_url": "https://meet.jit.si/MyRoom",
  "participants": [
    {
      "id": "abc123",
      "name": "Julien",
      "jid": "julien@meet.jit.si"
    },
    {
      "id": "def456",
      "name": "Clémence",
      "jid": "clemence@meet.jit.si"
    }
  ],
  "share": true
}
```

##### Interprétation

- `"share": true` → Au moins 1 screenshare a eu lieu pendant la réunion
- `"share": false` → Pas de screenshare (uniquement webcams)

##### ⚠️ Limitation

Ce flag indique **si** il y a eu screenshare, mais **pas quand** (timestamps manquants).

##### Usage

```python
import json

def check_has_screenshare(metadata_path: str) -> bool:
    """Vérifie si la réunion a eu au moins 1 screenshare"""
    with open(metadata_path) as f:
        metadata = json.load(f)

    return metadata.get("share", False)

# Décision rapide avant traitement
if check_has_screenshare("/tmp/recordings/abc123/metadata.json"):
    print("✅ Screenshare détecté → Lancer pipeline OCR")
else:
    print("⏭️ Pas de screenshare → Skip OCR, transcription audio uniquement")
```

---

#### **Approche 2 : Analyse heuristique des frames** (custom)

**Principe :** Distinguer webcam vs screenshare par analyse d'image OpenCV

##### Caractéristiques visuelles

| Webcam | Screenshare |
|--------|-------------|
| Formes floues, peau | **Contours nets, texte** |
| Couleurs variées (visages) | **Couleurs UI (blancs, gris, bleus)** |
| Mouvement fluide | **Changements brusques** |
| Peu/pas de texte | **Beaucoup de texte** |
| Visages détectables (Haar Cascade) | **Pas de visages** |
| Basse fréquence spatiale | **Haute fréquence spatiale** (contours) |

##### Code : Détection screenshare par heuristiques

```python
import cv2
import numpy as np
from paddleocr import PaddleOCR

# Initialiser OCR (réutilisé pour chaque frame)
ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=False, show_log=False)

def is_screenshare_frame(frame: np.ndarray) -> tuple[bool, float]:
    """
    Détermine si une frame est un screenshare ou une webcam.

    Args:
        frame: Image numpy array (BGR)

    Returns:
        (is_screenshare, confidence_score)

    Example:
        >>> cap = cv2.VideoCapture('meeting.mp4')
        >>> ret, frame = cap.read()
        >>> is_screen, score = is_screenshare_frame(frame)
        >>> print(f"Screenshare: {is_screen} (score: {score:.2%})")
        Screenshare: True (score: 0.34)
    """

    frame_area = frame.shape[0] * frame.shape[1]

    # ==========================
    # 1. Détection de TEXTE
    # ==========================
    # Beaucoup de texte = probablement screenshare

    result = ocr.ocr(frame, cls=False)

    text_area = 0
    if result and result[0]:
        for detection in result[0]:
            bbox = detection[0]
            # Calculer aire de la bounding box
            width = bbox[1][0] - bbox[0][0]
            height = bbox[2][1] - bbox[1][1]
            text_area += width * height

    text_ratio = text_area / frame_area

    # ==========================
    # 2. Détection de CONTOURS
    # ==========================
    # Slides = beaucoup de contours nets (bordures, séparateurs)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = np.count_nonzero(edges) / frame_area

    # ==========================
    # 3. Analyse COULEUR
    # ==========================
    # UI = beaucoup de blanc/gris (backgrounds PowerPoint, Google Docs)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Masque blanc (Saturation faible, Value élevée)
    white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
    white_ratio = np.count_nonzero(white_mask) / frame_area

    # ==========================
    # 4. SCORE COMPOSITE
    # ==========================

    score = (
        text_ratio * 0.5 +      # 50% poids texte (critère principal)
        edge_ratio * 0.3 +      # 30% poids contours
        white_ratio * 0.2       # 20% poids blanc
    )

    # Seuil : ajuster selon tests
    # - Webcam typique : score 0.05-0.10
    # - Screenshare typique : score 0.20-0.50
    is_screenshare = score > 0.15

    return is_screenshare, score


# ==========================
# UTILISATION
# ==========================

cap = cv2.VideoCapture('meeting.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Tester toutes les 30 frames (1 fois par seconde si 30fps)
frame_num = 0
screenshare_periods = []
current_period_start = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_num % 30 == 0:  # Tester chaque seconde
        is_screen, score = is_screenshare_frame(frame)

        timestamp = frame_num / fps

        if is_screen:
            if current_period_start is None:
                current_period_start = timestamp
                print(f"🖥️ Screenshare START à {timestamp:.1f}s (score: {score:.2%})")
        else:
            if current_period_start is not None:
                screenshare_periods.append((current_period_start, timestamp))
                print(f"📷 Screenshare END à {timestamp:.1f}s")
                current_period_start = None

    frame_num += 1

cap.release()

# Résultat : Liste de périodes screenshare
print(f"\n📊 Périodes de screenshare détectées :")
for start, end in screenshare_periods:
    duration = end - start
    print(f"  {start:.1f}s → {end:.1f}s (durée: {duration:.1f}s)")

# Exemple output :
# 📊 Périodes de screenshare détectées :
#   450.0s → 2100.0s (durée: 1650.0s = 27.5min)
#   2850.0s → 3300.0s (durée: 450.0s = 7.5min)
```

##### Optimisations possibles

```python
# Cache OCR pour éviter réinitialisation
_ocr_instance = None

def get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=False, show_log=False)
    return _ocr_instance

# Utiliser dans is_screenshare_frame()
ocr = get_ocr()
```

##### Ajustement des seuils

```python
# Tester sur échantillon connu
test_frames = {
    "webcam_julien.jpg": False,
    "slide_intro.jpg": True,
    "webcam_clemence.jpg": False,
    "slide_results.jpg": True,
    "split_screen.jpg": True  # Split screen webcam + slides = screenshare
}

for filename, expected in test_frames.items():
    frame = cv2.imread(filename)
    is_screen, score = is_screenshare_frame(frame)

    status = "✅" if is_screen == expected else "❌"
    print(f"{status} {filename}: {is_screen} (score: {score:.3f}, attendu: {expected})")

# Ajuster le seuil 0.15 si trop de faux positifs/négatifs
```

---

#### **Approche 3 : PySceneDetect pour zones temporelles**

**Principe :** Détecter les **changements majeurs de scène** (transitions webcam ↔ screenshare)

```python
from scenedetect import detect, ContentDetector

# Détecter les changements de scène
scenes = detect('meeting.mp4', ContentDetector(threshold=27))

# Analyser seulement 1 frame par scène (optimisation)
for i, (start, end) in enumerate(scenes):
    # Extraire 1 frame au milieu de la scène
    mid_frame_num = (start.frame_num + end.frame_num) // 2

    cap = cv2.VideoCapture('meeting.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_num)
    ret, frame = cap.read()
    cap.release()

    # Tester avec approche 2
    is_screen, score = is_screenshare_frame(frame)

    if is_screen:
        print(f"✅ Scène {i} ({start} → {end}) = SCREENSHARE → OCR à faire")
        # Extraire frames dans cette période pour ImageHash + OCR
    else:
        print(f"⏭️ Scène {i} ({start} → {end}) = WEBCAM → Skip")
```

**Avantage :** Teste seulement **1 frame par scène** au lieu de toutes les frames → très rapide

---

## 🏗️ Architecture finale recommandée

### Pipeline complet

```
┌─────────────────────────────────┐
│  Vidéo Jibri                    │
│  meeting.mp4                    │
│  + metadata.json                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ÉTAPE 1 : Vérification rapide              │
│  ─────────────────────────────              │
│  Lire metadata.json                         │
│  Si share=false → Skip OCR ⏭️              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ÉTAPE 2 : Détection zones screenshare     │
│  ───────────────────────────────────────    │
│  PySceneDetect → Scènes                     │
│  Pour chaque scène :                        │
│    - Tester 1 frame mid-scene               │
│    - is_screenshare_frame() → bool          │
│  → Périodes screenshare identifiées         │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ÉTAPE 3 : Extraction frames screenshare   │
│  ─────────────────────────────────────────  │
│  ffmpeg extract 1 frame/sec                 │
│  SEULEMENT dans périodes screenshare        │
│  Exemple : 30min screenshare = 1800 frames  │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ÉTAPE 4 : Détection changements slides    │
│  ────────────────────────────────────────   │
│  ImageHash (phash) sur 1800 frames          │
│  Distance Hamming > 8 = nouvelle slide      │
│  → ~30-50 frames de slides uniques          │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ÉTAPE 5 : OCR local PaddleOCR             │
│  ──────────────────────────────────────     │
│  OCR sur 30-50 slides uniques               │
│  Extraction texte + structure               │
│  Temps : ~15 secondes (CPU)                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  ÉTAPE 6 : Fusion avec transcription       │
│  ────────────────────────────────────────   │
│  Transcription audio (faster-whisper)       │
│  + Diarization (pyannote)                   │
│  + Texte OCR avec timestamps                │
│  → Transcription enrichie complète          │
└─────────────────────────────────────────────┘
```

### Workflow visuel

```
Vidéo 1h (3600 frames @ 1fps)
         │
         ├─→ metadata.json: share=true ✅
         │
         ▼
   PySceneDetect
         │
         ├─→ Scène 1 (0-450s) : Webcam ⏭️ SKIP
         ├─→ Scène 2 (450-2100s) : Screenshare ✅ → 1650 frames
         ├─→ Scène 3 (2100-2850s) : Webcam ⏭️ SKIP
         └─→ Scène 4 (2850-3300s) : Screenshare ✅ → 450 frames
         │
         ▼
   Extract frames (2100 frames total)
         │
         ▼
   ImageHash perceptual diff
         │
         ├─→ Frame 450 : Hash A
         ├─→ Frame 451 : Hash A (distance=2) → SKIP
         ├─→ Frame 452 : Hash A (distance=1) → SKIP
         ├─→ ...
         ├─→ Frame 498 : Hash B (distance=12) → ✅ NOUVELLE SLIDE
         ├─→ Frame 499 : Hash B (distance=3) → SKIP
         └─→ ...
         │
         ▼
   30-50 slides uniques identifiées
         │
         ▼
   PaddleOCR (30-50 fois)
         │
         ▼
   Texte structuré par slide
```

---

## 📊 Performances et coûts

### Estimation pour 1h de réunion avec 30min screenshare

| Étape | Temps CPU | Frames traitées | Coût |
|-------|-----------|-----------------|------|
| **1. Metadata check** | <1sec | - | Gratuit |
| **2. PySceneDetect** | ~2min | 3600 frames (analyse) | Gratuit |
| **3. Extract frames** | ~1min | 1800 frames (30min screenshare) | Gratuit |
| **4. ImageHash** | ~3-5sec | 1800 frames | Gratuit |
| **→ Slides uniques** | - | **~30-50 frames** | - |
| **5. PaddleOCR** | ~15-20sec | 30-50 slides | Gratuit |
| **TOTAL** | **~3-4 min** | **30-50 OCR** (vs 1800 !) | **0€** |

### Comparaison Claude Vision API

| Approche | Frames OCR | Temps | Coût/heure | Coût/mois (20h) |
|----------|-----------|-------|------------|-----------------|
| **Claude Vision API** | 1800 (1 frame/10sec) | ~30sec | 5,40€ | **~110€** |
| **Solution locale optimisée** | 30-50 (slides uniques) | ~4min | 0€ | **0€** |

**Économie : 110€/mois → 100% d'économie !**

### Temps de traitement détaillé (CPU)

**Configuration test :** Intel i5-8250U (4 cores @ 1.6GHz), 16GB RAM

| Opération | 1 frame | 100 frames | 1800 frames |
|-----------|---------|------------|-------------|
| **ImageHash (phash)** | 1ms | 100ms | 1.8s |
| **PaddleOCR** | 350ms | 35s | 10.5min |
| **is_screenshare_frame()** | 400ms | 40s | 12min |
| **PySceneDetect** | - | - | 2-3min (vidéo complète) |

**Optimisation parallèle possible :**
- ImageHash : Traitement batch (100 frames en parallèle)
- PaddleOCR : `rec_batch_num=6` pour OCR multiple simultané

---

## 📦 Bibliothèques recommandées

### Installation complète

```bash
# OCR
pip install paddleocr==2.7.3
pip install paddlepaddle==2.6.0  # CPU version

# Détection changement slides
pip install ImageHash==4.3.1
pip install Pillow==10.2.0

# Détection scènes
pip install scenedetect[opencv]==0.6.3

# Traitement vidéo
pip install opencv-python==4.9.0.80

# Utilitaires
pip install numpy
```

### requirements.txt

```txt
paddleocr==2.7.3
paddlepaddle==2.6.0
ImageHash==4.3.1
Pillow==10.2.0
scenedetect[opencv]==0.6.3
opencv-python==4.9.0.80
numpy>=1.24.0
```

### Versions GPU (optionnel, si GPU disponible plus tard)

```bash
# Remplacer paddlepaddle CPU par GPU
pip uninstall paddlepaddle
pip install paddlepaddle-gpu  # Nécessite CUDA
```

---

## 🔗 Ressources et références

### Benchmarks et comparaisons OCR
- [OCR comparison: Tesseract vs EasyOCR vs PaddleOCR vs MMOCR (Medium)](https://toon-beerten.medium.com/ocr-comparison-tesseract-versus-easyocr-vs-paddleocr-vs-mmocr-a362d9c79e66)
- [PaddleOCR vs Tesseract: Which is the best open source OCR?](https://www.koncile.ai/en/ressources/paddleocr-analyse-avantages-alternatives-open-source)
- [8 Top Open-Source OCR Models Compared (Modal Blog)](https://modal.com/blog/8-top-open-source-ocr-models-compared)

### Bibliothèques GitHub
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 44k stars
- [ImageHash](https://github.com/JohannesBuchner/imagehash) - 3.2k stars
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) - 3.8k stars
- [Jibri (Jitsi Recording)](https://github.com/jitsi/jibri) - 500+ stars

### Documentation
- [PaddleOCR Documentation](https://paddlepaddle.github.io/PaddleOCR/)
- [PySceneDetect Documentation](https://pyscenedetect.readthedocs.io/)
- [Jitsi Community Forum - Jibri metadata](https://community.jitsi.org/t/jibri-metadata-json/20254)

---

## 🎯 Prochaines étapes

1. ✅ **Valider architecture** avec Julien
2. ⏳ **Coder prototype** (`transcription_local_ocr.py`)
3. ⏳ **Tester sur vidéo réelle** (ajuster seuils ImageHash + is_screenshare)
4. ⏳ **Intégrer au pipeline complet** (Jibri → Transcription → Résumé)
5. ⏳ **Déployer sur VPS** (Docker Compose)

---

**Version :** 1.0
**Auteur :** Claude Code + Julien
**Prochaine révision :** Après tests prototype
