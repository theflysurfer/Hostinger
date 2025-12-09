# 🐳 Services Docker Actifs - srv759970
**Date:** 2025-12-04
**Context:** Documentation des services actifs identifiés lors du nettoyage d'espace disque

---

## 📊 État Actuel

- **Disque:** 163 GB utilisé / 193 GB (85%)
- **Espace libre:** 31 GB
- **Conteneurs actifs:** 53/54
- **Images Docker:** 47 (33.9 GB après nettoyage)

---

## 🎯 Services Actifs Documentés

Les services suivants tournent actuellement et doivent être **préservés et documentés** dans l'architecture.

### 1. Discord Voice Bot
**Container:** `discord-voice-bot`
**Image:** `discord-bot_discord-bot:latest` (617 MB)
**Status:** Up 3 weeks (unhealthy)
**Ports:** Internal only
**Type:** Shared service / Bot
**Priority:** Production

**Description:** Bot Discord pour automatisation vocale

**Action requise:**
- ⚠️ Status unhealthy - investigation nécessaire
- 📝 Créer `docs/services/discord-bot.md`
- ✅ Ajouter au registry.yml

---

### 2. Telegram Voice Bot
**Container:** `telegram-voice-bot`
**Image:** `telegram-bot_telegram-bot:latest` (155 MB)
**Status:** Up 3 weeks (healthy)
**Ports:** Internal only
**Type:** Shared service / Bot
**Priority:** Production

**Description:** Bot Telegram pour automatisation

**Registry:** ✅ Déjà documenté dans `registry.yml` ligne 292
**Documentation:** `docs/services/telegram-bot.md`

---

### 3. Human Chain - Backend
**Container:** `human-chain-backend`
**Image:** `human-chain_backend:latest` (173 MB)
**Status:** Up 3 weeks (unhealthy)
**Ports:** 8888:8000
**URL:** http://69.62.108.82:8888
**Type:** Client app / API
**Priority:** Production

**Description:** Backend API pour Human Chain

**Action requise:**
- ⚠️ Status unhealthy - investigation nécessaire
- 📝 Créer documentation projet Human Chain
- ✅ Ajouter au registry.yml

---

### 4. Human Chain - Frontend
**Container:** `human-chain-frontend`
**Image:** `human-chain_frontend:latest` (53.3 MB)
**Status:** Up 3 weeks (healthy)
**Ports:** 3333:80
**URL:** http://69.62.108.82:3333
**Type:** Client app / Web
**Priority:** Production

**Description:** Frontend web pour Human Chain

**Action requise:**
- 📝 Créer documentation projet Human Chain
- ✅ Ajouter au registry.yml
- 🌐 Configurer domaine/sous-domaine si nécessaire

---

### 5. Photos Chantier
**Container:** `photos-chantier`
**Image:** `photos-chantier_photos-chantier:latest` (247 MB)
**Status:** Up 3 weeks
**Ports:** 9521:3000
**URL:** http://69.62.108.82:9521
**Type:** Client app / Dashboard
**Priority:** Production

**Registry:** ✅ Déjà documenté dans `registry.yml` ligne 199
**URL documentée:** https://photos.srv759970.hstgr.cloud
**Port documenté:** 8503

**Action requise:**
- ⚠️ Port mismatch: documenté 8503 vs réel 9521
- 🔧 Mettre à jour registry.yml avec port correct

---

### 6. MkDocs
**Container:** `mkdocs`
**Image:** `mkdocs_mkdocs:latest` (225 MB)
**Status:** Up 9 hours
**Ports:** 8005:8000
**URL:** http://69.62.108.82:8005
**Type:** Infrastructure / Documentation
**Priority:** Development

**Description:** Site de documentation MkDocs (ce site)

**Registry:** ✅ Déjà documenté dans `registry.yml` ligne 463
**Documentation:** `docs/infrastructure/mkdocs.md`

---

### 7. LangChain Service
**Container:** `langchain-service`
**Image:** `langchain-service_langchain-service:latest` (333 MB)
**Status:** Up 3 weeks (healthy)
**Ports:** 5000:5000
**URL:** http://69.62.108.82:5000
**Type:** Shared service / AI
**Priority:** Production

**Description:** Service LangChain pour intégrations LLM

**Action requise:**
- 📝 Créer `docs/services/langchain-service.md`
- ✅ Ajouter au registry.yml section AI/ML Services

---

### 8. DownTo40 Streamlit
**Container:** `downto40-streamlit`
**Image:** `downto40_streamlit:latest` (778 MB)
**Status:** Up 3 weeks (healthy)
**Ports:** 8509:8501
**URL:** http://69.62.108.82:8509
**Type:** Client app / Dashboard
**Priority:** Production

**Description:** Dashboard Energie DownTo40 (Streamlit)

**Registry:** ✅ Partiellement documenté ligne 179
**Nom registry:** "energie-dashboard"
**URL documentée:** https://energie.srv759970.hstgr.cloud
**Port documenté:** 8501

**Action requise:**
- ⚠️ Port mismatch: documenté 8501 vs réel 8509
- 🔧 Mettre à jour registry.yml avec port et container name corrects

---

### 9. Paperflow - API
**Container:** `paperflow-api`
**Image:** `d39037f5b4df` (image ID - paperflow worker base)
**Status:** Up 3 weeks (healthy)
**Ports:** 9520:8000
**URL:** http://69.62.108.82:9520
**Type:** Shared service / Document Processing
**Priority:** Production

**Description:** API Paperflow pour traitement de documents

**Action requise:**
- 📝 Créer `docs/services/paperflow.md`
- ✅ Ajouter au registry.yml section Documents

---

### 10. Paperflow - Worker
**Container:** `paperflow-worker`
**Image:** `paperflow_paperflow-worker:latest` (6.65 GB) ⚠️ **Très grosse image**
**Status:** Up 34 minutes (unhealthy)
**Ports:** 8000/tcp (internal)
**Type:** Shared service / Background Worker
**Priority:** Production

**Description:** Worker Celery pour Paperflow (traitement asynchrone)

**Action requise:**
- ⚠️ Status unhealthy + redémarrage récent - investigation nécessaire
- 📝 Documenter dans `docs/services/paperflow.md`
- 🔍 Analyser pourquoi image si lourde (6.65 GB)
- 💡 Optimisation possible avec multi-stage build (voir DOCKER_SPACE_ANALYSIS_REPORT.md)

---

### 11. Paperflow - Flower
**Container:** `paperflow-flower`
**Image:** `d39037f5b4df` (image ID - paperflow worker base)
**Status:** Up 35 hours (unhealthy)
**Ports:** 9522:5555
**URL:** http://69.62.108.82:9522
**Type:** Shared service / Monitoring
**Priority:** Development

**Description:** Flower monitoring pour Paperflow Celery workers

**Action requise:**
- ⚠️ Status unhealthy - investigation nécessaire
- 📝 Documenter dans `docs/services/paperflow.md`

---

## 📋 Actions Requises

### Immédiat

1. **Investiguer les services unhealthy** ⚠️
   - discord-voice-bot (up 3 weeks, unhealthy)
   - human-chain-backend (up 3 weeks, unhealthy)
   - paperflow-worker (up 34 min, unhealthy)
   - paperflow-flower (up 35h, unhealthy)

2. **Corriger port mismatches** 🔧
   - photos-chantier: registry 8503 → réel 9521
   - energie-dashboard: registry 8501 → réel 8509

### Court terme

3. **Créer documentation manquante** 📝
   - `docs/services/discord-bot.md`
   - `docs/services/langchain-service.md`
   - `docs/services/paperflow.md` (couvre API + Worker + Flower)
   - Documentation projet Human Chain (dans repo projet)

4. **Mettre à jour registry.yml** ✅
   - Ajouter discord-bot
   - Ajouter langchain-service
   - Ajouter paperflow (3 conteneurs)
   - Ajouter human-chain
   - Corriger ports pour photos-chantier et energie-dashboard

### Moyen terme

5. **Optimisations Docker** 💡
   - Investiguer paperflow-worker (6.65 GB)
   - Possibilité de multi-stage build (gain ~1-1.5 GB)
   - Voir `COMPREHENSIVE_SPACE_ANALYSIS.md` pour détails

6. **Configuration domaines** 🌐
   - human-chain: actuellement port 3333/8888 sans domaine
   - Considérer https://humanchain.srv759970.hstgr.cloud

---

## 🔍 Services à NE PAS Supprimer

**IMPORTANT:** Les images suivantes sont **utilisées par des conteneurs actifs** et doivent être **préservées** :

| Image | Taille | Conteneurs actifs | Raison |
|-------|--------|-------------------|--------|
| paperflow_paperflow-worker | 6.65 GB | 3 | API + Worker + Flower |
| downto40_streamlit | 778 MB | 1 | Dashboard Energie (client principal) |
| discord-bot_discord-bot | 617 MB | 1 | Bot Discord automation |
| langchain-service_langchain-service | 333 MB | 1 | Service AI/LLM |
| photos-chantier_photos-chantier | 247 MB | 1 | Dashboard photos client |
| mkdocs_mkdocs | 225 MB | 1 | Documentation (ce site) |
| human-chain_backend | 173 MB | 1 | API Human Chain |
| telegram-bot_telegram-bot | 155 MB | 1 | Bot Telegram automation |
| human-chain_frontend | 53.3 MB | 1 | Frontend Human Chain |

**Total préservé:** ~9.2 GB sur 11 services actifs

---

## 📊 Images Supprimées (session 2025-12-04)

| Image | Taille | Raison | Status |
|-------|--------|--------|--------|
| deploy_xtts-api:latest | 9.01 GB | Aucun conteneur XTTS | ✅ Supprimé |
| curlimages/curl:latest | 22.7 MB | Utilitaire temporaire | ✅ Supprimé |
| postgres:<none> | 278 MB | Image dangling | ❌ En cours d'utilisation |
| dive_dive-web:latest | 205 MB | Outil temporaire | ❌ En cours d'utilisation |

**Total supprimé:** ~9 GB
**Espace libéré total (caches + docker):** ~24 GB

---

## 🎯 Résumé État Final

### Avant nettoyage
- Disque: 186 GB utilisé (97%)
- Libre: 6.8 GB

### Après nettoyage (Caches + Docker)
- Disque: 163 GB utilisé (85%)
- Libre: 31 GB
- **Gain total: ~24 GB**

### Décomposition du gain
- Caches (pip, huggingface, npm, temp): ~8 GB
- Docker images obsolètes (XTTS, curl): ~9 GB
- Docker images supprimées automatiquement: ~6 GB

---

## 📝 Prochaines étapes

1. ✅ Mettre à jour `docs/docs/applications/registry.yml`
2. 📝 Créer documentation services manquants
3. 🔧 Investiguer et corriger services unhealthy
4. 🌐 Configurer domaines/sous-domaines si nécessaire
5. 💡 Planifier optimisations Docker (paperflow-worker)

---

**Maintenu par:** Claude Code Space Optimization Task
**Dernière mise à jour:** 2025-12-04 17:15 UTC
