# 🤖 Repos GitHub - Catégorisation IA de Photos

## 🎯 Objectif

Trouver des solutions IA pour catégoriser automatiquement les photos :
- Posters / Affiches de spectacles et concerts
- Photos utilisateurs vs photos de famille
- Photos de paysages
- Reconnaissance faciale et événements

---

## 🏆 Solutions recommandées

### 1. **PhotoPrism** ⭐ (Most Popular)

**Repository** : https://github.com/photoprism/photoprism

**Description** : Application photos AI-Powered pour le web décentralisé

**Features** :
- ✅ Labellisation automatique basée sur le contenu et la localisation
- ✅ Reconnaissance faciale pour famille et amis
- ✅ Tagging IA automatique avec machine learning
- ✅ Groupement par personnes
- ✅ Auto-hébergé et privacy-focused
- ✅ Interface web moderne et responsive
- ✅ Support géolocalisation et cartographie
- ✅ Recherche avancée par tags, personnes, lieux

**Technologies** :
- Go (backend)
- TensorFlow (IA)
- MariaDB/MySQL
- Docker

**Installation** :
```bash
docker run -d \
  --name photoprism \
  --security-opt seccomp=unconfined \
  --security-opt apparmor=unconfined \
  -p 2342:2342 \
  -e PHOTOPRISM_UPLOAD_NSFW="true" \
  -e PHOTOPRISM_ADMIN_PASSWORD="admin" \
  -v /path/to/photos:/photoprism/originals \
  -v ./storage:/photoprism/storage \
  photoprism/photoprism
```

**Avantages** :
- Production-ready
- Large communauté (36k+ stars)
- Bien maintenu
- Interface utilisateur excellente

**Inconvénients** :
- Nécessite des ressources (CPU/RAM pour IA)
- Pas de catégorisation "poster vs famille" directe (nécessite custom training)

---

### 2. **Photo-Organizer-CORE** (Standalone AI Agent)

**Repository** : https://github.com/ashesbloom/Photo-Organizer-CORE

**Description** : Agent IA desktop standalone pour catégoriser automatiquement les photos

**Features** :
- ✅ Catégorisation automatique par date, lieu, visages
- ✅ Traitement 100% local (pas de cloud)
- ✅ Organisation en hiérarchie albums/dossiers
- ✅ Reconnaissance faciale intégrée
- ✅ Pas besoin de serveur web

**Technologies** :
- Python
- Deep Learning (modèles locaux)
- Desktop app

**Utilisation** :
```bash
git clone https://github.com/ashesbloom/Photo-Organizer-CORE
cd Photo-Organizer-CORE
pip install -r requirements.txt
python organizer.py --input /path/to/photos --output /path/to/organized
```

**Avantages** :
- Simple et léger
- Pas besoin de serveur
- Privacy total (tout en local)
- Scripts personnalisables

**Inconvénients** :
- Pas d'interface web
- Moins de features que PhotoPrism
- Nécessite adaptation pour catégories spécifiques (posters/concerts)

---

### 3. **jfthuong/photo-organizer** (ML Modules)

**Repository** : https://github.com/jfthuong/photo-organizer

**Description** : Modules ML et heuristiques pour organiser photos de famille

**Features** :
- ✅ Identification faciale avec FaceNet
- ✅ Modules ML multiples
- ✅ Approche heuristique + ML
- ✅ Orienté photos de famille

**Technologies** :
- Python
- FaceNet (reconnaissance faciale)
- TensorFlow

**Avantages** :
- Modulaire et extensible
- Focus sur les photos de famille
- Code bien documenté

**Inconvénients** :
- Moins actif (dernière update 2021)
- Nécessite développement custom pour nouveaux cas d'usage

---

### 4. **PicFolio** (Mobile + Desktop)

**Repository** : https://github.com/meet244/PicFolio

**Description** : Gestionnaire photos avec client-serveur, upload depuis mobile

**Features** :
- ✅ Tagging automatique avec IA (Recognise Anything Model)
- ✅ Reconnaissance faciale (DeepFace)
- ✅ Recherche avec Gemini API
- ✅ Upload depuis mobile
- ✅ Stockage local

**Technologies** :
- Node.js (backend)
- DeepFace (face recognition)
- Gemini API (search)
- RAM (Recognise Anything Model)

**Avantages** :
- Architecture client-serveur moderne
- Multiple modèles IA
- Support mobile

**Inconvénients** :
- Dépendance Gemini API (Google)
- Moins mature que PhotoPrism

---

### 5. **IntelliAlbum**

**Repository** : https://github.com/neozhu/IntelliAlbum

**Description** : Album intelligent avec IA

**Features** :
- ✅ Reconnaissance faciale automatique
- ✅ Sauvegarde des données faciales
- ✅ Interface album

**Technologies** :
- .NET / C#
- Machine Learning

**Avantages** :
- Stack .NET bien structuré
- Interface moderne

**Inconvénients** :
- Moins populaire
- Communauté plus petite

---

## 🎯 Cas d'usage spécifique : Posters/Concerts vs Famille

Pour catégoriser **posters de spectacles/concerts** vs **photos de famille** vs **paysages**, il faut :

### Approche recommandée

1. **Utiliser PhotoPrism comme base**
   - Gère déjà : personnes, lieux, dates
   - Interface web prête

2. **Ajouter un classifier custom**
   - Entraîner un modèle CNN (ResNet50, EfficientNet)
   - 3 classes : "poster", "family", "landscape"
   - Dataset : ImageNet + custom dataset

3. **Pipeline proposé** :

```python
# Pseudo-code
import torch
from torchvision import models, transforms

# Modèle pré-entraîné
model = models.resnet50(pretrained=True)
model.fc = torch.nn.Linear(model.fc.in_features, 3)  # 3 classes

# Inference
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

def classify_photo(image_path):
    image = Image.open(image_path)
    input_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        _, predicted = torch.max(output, 1)

    classes = ['poster', 'family', 'landscape']
    return classes[predicted.item()]

# Intégration avec PhotoPrism
# → Ajouter tags automatiques selon classification
```

---

## 🚀 Solution complète recommandée

### Architecture combinée

```
[ Dropbox 600 Go ]
        |
        | (rclone mount)
        v
   VPS Hostinger
        |
        +-- PhotoPrism (galerie + IA de base)
        +-- Custom Classifier (posters/famille/paysage)
        +-- digiKam (MariaDB externe)
        +-- Lychee (galerie secondaire)
```

### Stack technique

1. **PhotoPrism** pour :
   - Interface web
   - Reconnaissance faciale
   - Géolocalisation
   - Tags de base

2. **Custom Python script** pour :
   - Classification poster/famille/paysage
   - Modèle PyTorch/TensorFlow
   - Ajout de tags dans PhotoPrism via API

3. **digiKam** pour :
   - Édition avancée
   - Catalogage professionnel
   - Workflow photographe

---

## 📦 Installation PhotoPrism sur VPS

```bash
mkdir -p /var/www/photoprism/{storage,originals}

docker run -d \
  --name photoprism \
  --security-opt seccomp=unconfined \
  --security-opt apparmor=unconfined \
  -p 2342:2342 \
  -e PHOTOPRISM_ADMIN_USER="admin" \
  -e PHOTOPRISM_ADMIN_PASSWORD="PhotoPrism2025!" \
  -e PHOTOPRISM_AUTH_MODE="password" \
  -e PHOTOPRISM_SITE_URL="https://photos.srv759970.hstgr.cloud/" \
  -e PHOTOPRISM_DISABLE_TLS="true" \
  -e PHOTOPRISM_DEFAULT_TLS="true" \
  -e PHOTOPRISM_ORIGINALS_LIMIT="5000" \
  -e PHOTOPRISM_HTTP_COMPRESSION="gzip" \
  -e PHOTOPRISM_WORKERS="2" \
  -e PHOTOPRISM_LOG_LEVEL="info" \
  -e PHOTOPRISM_READONLY="false" \
  -e PHOTOPRISM_EXPERIMENTAL="false" \
  -e PHOTOPRISM_DISABLE_CHOWN="false" \
  -e PHOTOPRISM_DISABLE_WEBDAV="false" \
  -e PHOTOPRISM_DISABLE_SETTINGS="false" \
  -e PHOTOPRISM_DISABLE_TENSORFLOW="false" \
  -e PHOTOPRISM_DISABLE_FACES="false" \
  -e PHOTOPRISM_DISABLE_CLASSIFICATION="false" \
  -e PHOTOPRISM_DETECT_NSFW="false" \
  -e PHOTOPRISM_UPLOAD_NSFW="true" \
  -e PHOTOPRISM_DATABASE_DRIVER="mysql" \
  -e PHOTOPRISM_DATABASE_SERVER="mariadb:3306" \
  -e PHOTOPRISM_DATABASE_NAME="photoprism" \
  -e PHOTOPRISM_DATABASE_USER="photoprism" \
  -e PHOTOPRISM_DATABASE_PASSWORD="PhotoPrismDB2025" \
  -e PHOTOPRISM_SITE_CAPTION="AI-Powered Photos" \
  -e PHOTOPRISM_SITE_DESCRIPTION="" \
  -e PHOTOPRISM_SITE_AUTHOR="" \
  -v /mnt/dropbox:/photoprism/originals:ro \
  -v /var/www/photoprism/storage:/photoprism/storage \
  photoprism/photoprism
```

---

## 🎓 Resources

- **PhotoPrism Docs** : https://docs.photoprism.app/
- **PyTorch Image Classification** : https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
- **TensorFlow Image Classification** : https://www.tensorflow.org/tutorials/images/classification
- **DeepFace** : https://github.com/serengil/deepface
- **FaceNet** : https://github.com/davidsandberg/facenet

---

**Créé le** : 2025-10-16
**Recommandation** : PhotoPrism + Custom Classifier pour catégories spécifiques
