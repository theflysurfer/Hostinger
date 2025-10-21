# 📊 Benchmark Whisper Services

Benchmark comparatif entre **faster-whisper** et **WhisperX** pour la transcription audio.

## 🎯 Objectifs

Comparer les deux services sur :
1. ⏱️ **Temps de traitement** (vitesse)
2. 🔢 **Nombre de tokens** (longueur transcription)
3. 🎤 **Diarization** (identification speakers - WhisperX uniquement)

## 📁 Structure

```
benchmark/
├── audio_samples/          # 9 fichiers audio test
│   ├── short_01_*.m4a      # Courts (~700KB-1.3MB)
│   ├── medium_01_*.m4a     # Moyens (~3-9MB)
│   └── long_01_*.m4a       # Longs (~63-93MB)
├── results/
│   ├── benchmark_results.json      # Résultats bruts
│   └── benchmark_analysis.csv      # Analyse exportée
├── benchmark.py            # Script de benchmark
├── analyze.py              # Script d'analyse
├── requirements.txt
└── README.md
```

## 🚀 Installation

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer les credentials

Éditer `benchmark.py` ligne 18-19 :

```python
AUTH = ("your_username", "your_password")  # Basic auth Nginx
```

## 📊 Utilisation

### Étape 1 : Lancer le benchmark

```bash
python benchmark.py
```

**Durée estimée** : 30-90 minutes selon taille fichiers

**Sortie** :
```
================================================================================
🚀 BENCHMARK WHISPER SERVICES
================================================================================

📁 Fichiers à traiter: 9
🔧 Services: faster-whisper, WhisperX (avec/sans diarization)

[1/9] 📄 short_01_it_tour.m4a (0.7 MB)
--------------------------------------------------------------------------------
  [faster-whisper] short_01_it_tour.m4a... ✅ 00:12 | 342 tokens | 285 mots
  [WhisperX] short_01_it_tour.m4a... ✅ 00:15 | 348 tokens | 290 mots

...

================================================================================
✅ BENCHMARK TERMINÉ
================================================================================
📊 Résultats: 21 transcriptions effectuées
⏱️  Durée totale: 45:32 (2732s)
💾 Sauvegardé: results/benchmark_results.json
```

### Étape 2 : Analyser les résultats

```bash
python analyze.py
```

**Sortie** :
```
================================================================================
  📊 ANALYSE BENCHMARK WHISPER
================================================================================

✅ 21 résultats chargés

================================================================================
  ⏱️  TEMPS DE TRAITEMENT
================================================================================

📊 Statistiques par service:

                 Moyenne   Min    Max  Std Dev
service
faster-whisper     12.50  2.10  45.30     8.20
whisperx           15.80  3.20  52.10    10.50

💡 WhisperX est 26.4% plus lent que faster-whisper

...

💡 RECOMMANDATIONS
🏆 Service le plus rapide: faster-whisper
📝 Service le plus verbeux: whisperx
⚡ Service le plus efficace: faster-whisper
```

## 📈 Métriques mesurées

### Par service :
- **Temps total** (secondes)
- **Temps moyen** par fichier
- **Tokens GPT-4** (cl100k_base)
- **Nombre de mots**
- **Efficacité** (secondes / MB)

### WhisperX spécifique :
- **Impact diarization** (overhead %)
- **Nombre de speakers** détectés
- **Nombre de segments**

## 🎓 Interprétation résultats

### Temps de traitement
- **faster-whisper** : Généralement 20-30% plus rapide
- **WhisperX (sans diar)** : Performance similaire
- **WhisperX (avec diar)** : +50-70% de temps (détection speakers)

### Tokens / Qualité
- Les deux services produisent des transcriptions similaires
- Différences de tokens < 5% en général
- WhisperX peut être plus verbeux (ponctuation)

### Cas d'usage recommandés

| Service | Idéal pour |
|---------|-----------|
| **faster-whisper** | Transcription simple, rapide, API OpenAI compatible |
| **WhisperX** | Meetings, interviews, multi-speakers, timestamps précis |

## 🔧 Personnalisation

### Ajouter des fichiers audio

Placer vos fichiers `.m4a` dans `audio_samples/`

Le script détecte automatiquement tous les fichiers.

### Changer les modèles

Éditer `benchmark.py` :

```python
MODELS = {
    "faster-whisper": "Systran/faster-whisper-medium",  # ou small, large
    "whisperx": "large-v2"  # ou tiny, base, small, medium
}
```

### Ajuster timeouts

Si fichiers très longs :

```python
# benchmark.py, ligne 95 et 174
timeout=1200  # 20 minutes au lieu de 10
```

## 📊 Export résultats

Les résultats sont sauvegardés dans :

1. **JSON** : `results/benchmark_results.json`
   - Données brutes complètes
   - Textes de transcription inclus

2. **CSV** : `results/benchmark_analysis.csv`
   - Format tableur
   - Textes exclus (fichier plus léger)

## ⚠️ Limitations

- Nécessite credentials Basic Auth Nginx
- Services doivent être accessibles (via VPN si nécessaire)
- Fichiers très longs (>100MB) peuvent timeout
- La précision n'est pas mesurée automatiquement (évaluation manuelle requise)

## 💡 Troubleshooting

### Erreur 401 Unauthorized
```
✅ Vérifier credentials AUTH dans benchmark.py
```

### Erreur timeout
```
✅ Augmenter timeout (ligne 95, 174 de benchmark.py)
✅ Vérifier que services sont démarrés
```

### Aucun fichier trouvé
```
✅ Vérifier présence fichiers dans audio_samples/
✅ Extensions supportées: .m4a
```

## 📞 URLs Services

- **faster-whisper** : https://whisper.srv759970.hstgr.cloud
- **WhisperX** : https://whisperx.srv759970.hstgr.cloud
- **Swagger faster-whisper** : https://whisper.srv759970.hstgr.cloud/docs
- **Swagger WhisperX** : https://whisperx.srv759970.hstgr.cloud/docs

## 📚 Documentation

- [GUIDE_WHISPER_SERVICES.md](../docs/guides/GUIDE_WHISPER_SERVICES.md) - Documentation services
- [faster-whisper repo](https://github.com/fedirz/faster-whisper-server)
- [WhisperX repo](https://github.com/m-bain/whisperX)

---

**Dernière mise à jour** : Octobre 2025
