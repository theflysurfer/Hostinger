# Applications - Vue d'Ensemble

**Total** : 45 applications déployées
**Catégories** : 13

---

## Catégories d'Applications

### 🌐 WordPress (5 apps)
Sites WordPress pour clients :
- **[Clemence](wordpress/clemence.md)** - clemencefouquet.fr - `production`
- **[SolidarLink](wordpress/solidarlink.md)** - solidarlink.srv759970.hstgr.cloud - `staging`
- **JeSuisHyperphagique** - jesuishyperphagique.srv759970.hstgr.cloud - `production`
- **PanneauxSolidaires** - panneauxsolidaires.srv759970.hstgr.cloud - `production`
- **Shared Database** - MySQL partagé pour 2 sites

### 🎤 AI Transcription (3 apps)
Services de transcription audio/vidéo :
- **[WhisperX](ai-transcription/whisperx.md)** - Transcription avec diarization - `production`
- **[Faster-Whisper Queue](ai-transcription/faster-whisper.md)** - API async avec queue
- **Whisper Faster** - Transcription rapide OpenAI-compatible

### 🤖 AI RAG (3 apps)
RAG et traitement de documents :
- **[RAGFlow](ai-rag/ragflow.md)** - RAG multimodal - `production`
- **[MemVid](ai-rag/memvid.md)** - RAG avec encodage vidéo
- **RAG-Anything** - RAG avec LightRAG

### 🔊 AI TTS (2 apps)
Text-to-Speech services :
- **NeuTTS Air** - TTS avec voice cloning
- **XTTS v2** - Coqui TTS

### 🧠 AI Services (3 apps)
Infrastructure IA :
- **Ollama** - LLM inference (systemd service)
- **Tika Server** - Extraction contenu documents
- **LangChain Service** - Orchestration LangChain

### 💬 Bots (2 apps)
Chatbots vocaux :
- **Telegram Voice Bot** - Bot Telegram avec voix
- **Discord Voice Bot** - Bot Discord avec voix

### 📄 CMS & Sites (3 apps)
Sites custom et CMS :
- **Cristina Site** - Site Astro statique
- **Cristina Backend** - Strapi headless CMS
- **Impro Manager** - Application métier

### 🤝 Collaboration (3 apps)
Outils collaboratifs :
- **Nextcloud** - Cloud storage (arrêté)
- **RocketChat** - Chat team (arrêté)
- **Jitsi** - Visioconférence (arrêté)

### 📚 Documents (3 apps)
Gestion documentaire :
- **Paperless NGX** - DMS principal (arrêté)
- **Paperless AI** - Extension IA
- **Invidious** - Archivage vidéos

### ⚙️ Automation (2 apps)
Workflow et automatisation :
- **N8N** - Workflow automation
- **RustDesk** - Bureau à distance

### 📊 Dashboards (5 apps)
Dashboards custom :
- **[Energie Dashboard](dashboards/energie-dashboard.md)** - DownTo40 projet - `production` 🔴
- **Support Dashboard** - Dashboard support client
- **SharePoint Dashboards** - Dashboards SharePoint
- **Photos Chantier** - Galerie photos chantier
- **Energie 40€** - Version optimisée dashboard énergie

### 📈 Monitoring (2 apps)
Monitoring et observabilité :
- **Monitoring Stack** - Grafana + Prometheus + Loki (arrêté)
- **Dashy** - Portal dashboard - `production`

### 🔧 Infrastructure (5 apps)
Services infrastructure :
- **Databases Shared** - PostgreSQL + Redis + MongoDB - `critical`
- **Docker AutoStart** - Auto-start/stop conteneurs
- **DockerWakeUp** - Wake-up system
- **API Portal** - Swagger UI centralisé
- **MkDocs** - Documentation (ce site)

---

## Applications par Statut

### 🟢 Production (Apps Critiques)
- Energie Dashboard (DownTo40 🔴 priorité haute)
- WordPress Clemence
- WhisperX
- RAGFlow
- Dashy
- Databases Shared

### 🟡 Staging/Test
- WordPress SolidarLink
- Support Dashboard
- SharePoint Dashboards

### 🔴 Arrêtées (Optimisation RAM)
- Monitoring Stack (Grafana, Prometheus, Loki)
- Nextcloud
- RocketChat
- Jitsi
- Paperless NGX
- WordPress (certains sites)

---

## Tags

Filtrer les applications par tag :

- `production` - Apps en production
- `staging` - Apps de test
- `wordpress` - Sites WordPress
- `ai` - Services IA/ML
- `dashboard` - Dashboards custom
- `monitoring` - Services de monitoring
- `critical` - Infrastructure critique (SPOF)

---

## Quick Links

- **[Dashy Portal](https://dashy.srv759970.hstgr.cloud)** - Vue d'ensemble visuelle
- **[Grafana](https://monitoring.srv759970.hstgr.cloud)** - Métriques (si actif)
- **[Portainer](http://69.62.108.82:9000)** - Gestion Docker
- **[Dozzle](https://dozzle.srv759970.hstgr.cloud)** - Logs temps réel

---

**Dernière mise à jour** : 2025-10-28
