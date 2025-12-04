# Inventaire des Images Docker - Classement par Sécurité de Suppression

**Date:** 2025-11-09
**Serveur:** hostinger-automation (69.62.108.82)
**Total images:** 92

---

## 🟢 NIVEAU 1 - TRÈS SÛR (Images dangling - Aucun conteneur)

### Images sans nom ni tag - 33 images = **~42 GB**

| # | ID | Taille | Date | Statut |
|---|---|--------|------|--------|
| 1 | 0e0de735aaba | 6.96GB | 2025-10-30 | ❌ DANGLING |
| 2 | 2d352ebbaeda | 6.96GB | 2025-10-30 | ❌ DANGLING |
| 3 | aae7e5c439f2 | 6.96GB | 2025-10-30 | ❌ DANGLING |
| 4 | 6ee68d2b8827 | 6.96GB | 2025-10-30 | ❌ DANGLING |
| 5 | 39f5d89965e8 | 950MB | 2025-10-28 | ❌ DANGLING |
| 6 | f128794e9fba | 950MB | 2025-10-28 | ❌ DANGLING |
| 7 | f12ec4a00690 | 950MB | 2025-10-28 | ❌ DANGLING |
| 8 | fbe9024bbc0a | 950MB | 2025-10-28 | ❌ DANGLING |
| 9 | c8d7dc59491f | 847MB | 2025-10-28 | ❌ DANGLING |
| 10 | 328c24a043f1 | 847MB | 2025-10-28 | ❌ DANGLING |
| 11 | c735a7035d36 | 847MB | 2025-10-28 | ❌ DANGLING |
| 12 | d25d78e836c3 | 737MB | 2025-11-09 | ❌ DANGLING |
| 13 | 0571cc7a53b5 | 502MB | 2025-11-09 | ❌ DANGLING |
| 14 | 7359c137a167 | 502MB | 2025-11-09 | ❌ DANGLING |
| 15 | 101390f358bc | 466MB | 2025-10-30 | ❌ DANGLING |
| 16 | ce2d837782ed | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 17 | 189954dcd283 | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 18 | 708c3a8f82cf | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 19 | c65d805f4f1e | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 20 | 96c57ee2b49c | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 21 | a3146e6e032f | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 22 | aabfeeca814f | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 23 | c700072d1f32 | 1.03GB | 2025-10-28 | ❌ DANGLING |
| 24 | 2bcbb271cb1d | 1.02GB | 2025-10-28 | ❌ DANGLING |
| 25 | 0a682591aee9 | 247MB | 2025-10-28 | ❌ DANGLING |
| 26 | 1f9ef3480bfa | 247MB | 2025-10-28 | ❌ DANGLING |
| 27 | 8c0dd05e9698 | 247MB | 2025-10-28 | ❌ DANGLING |
| 28 | 549a9ee53459 | 247MB | 2025-10-28 | ❌ DANGLING |
| 29 | a398f1a0ba46 | 247MB | 2025-10-28 | ❌ DANGLING |
| 30 | 2ab908e1b5eb | 247MB | 2025-10-28 | ❌ DANGLING |
| 31 | 72a6e723c1a7 | 247MB | 2025-10-28 | ❌ DANGLING |
| 32 | ef346cfadf77 | 246MB | 2025-10-28 | ❌ DANGLING |
| 33 | 695cce41f4f1 | 246MB | 2025-10-27 | ❌ DANGLING |

**Recommandation:** SUPPRESSION IMMÉDIATE - Aucun risque

---

## 🟡 NIVEAU 2 - SÛR (Images inutilisées mais taggées)

### Anciennes versions MemVid - 2 images = **~9.65 GB**

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 34 | memvid_memvid-api:latest | 124a02ef32a1 | 9.08GB | 2025-10-21 | ❌ Aucun |
| 35 | memvid_memvid-ui:latest | db4faede28b5 | 565MB | 2025-10-21 | ❌ Aucun |

**Note:** Versions plus anciennes, remplacées par memvid-memvid-* (avec tiret)

### Images de test/développement - 1 image = **830 MB**

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 36 | wordpress-test-themes-wordpress-test-sqlite:latest | 014a09c64ba5 | 830MB | 2025-11-09 | ❌ Aucun |

### Outils/Bases de données anciennes versions

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 37 | elasticsearch:8.11.3 | ac1eef415132 | 1.41GB | 2023-12-12 | ❌ Aucun |
| 38 | mysql:8.0.39 | f5da8fc4b539 | 573MB | 2024-07-22 | ❌ Aucun |
| 39 | nextcloud:29-apache | b20bd60e6bc5 | 1.32GB | 2025-04-18 | ❌ Exited |
| 40 | caddy:2-alpine | e4bd530ab75a | 53.5MB | 2025-08-23 | ❌ Aucun |
| 41 | valkey/valkey:8 | 84be4d718bb5 | 120MB | 2025-10-03 | ❌ Aucun |
| 42 | php:8.3-fpm-alpine | 2b99916435d4 | 85.8MB | 2025-10-23 | ❌ Aucun |
| 43 | node:20-alpine | 2b56f2779663 | 134MB | 2025-10-16 | ❌ Aucun |
| 44 | python:3.11-slim | ff15e80be861 | 124MB | 2025-10-09 | ❌ Aucun |

### Applications non utilisées - 5 images = **~3 GB**

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 45 | energie-dashboard_app:latest | a9e13ac2d3ce | 968MB | 2025-10-24 | ❌ Aucun |
| 46 | infiniflow/ragflow:v0.21.0-slim | 73a672a31bbf | 7.06GB | 2025-10-15 | ❌ Aucun |
| 47 | quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z | c4260bcf2c25 | 175MB | 2025-06-23 | ❌ Aucun |
| 48 | aquasec/trivy:latest | 02e41b284e46 | 180MB | 2025-10-10 | ❌ Aucun |
| 49 | alpine:latest | 706db57fb206 | 8.32MB | 2025-10-08 | ❌ Aucun |

**Recommandation:** SUPPRESSION RECOMMANDÉE - Risque faible

---

## 🟠 NIVEAU 3 - ATTENTION (Images avec conteneurs arrêtés)

### N8N (conteneur exited mais potentiellement réutilisable)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 50 | n8nio/n8n:latest | fb3926d2063d | 975MB | 2025-10-28 | ⚠️ Exited (0) |

### XTS API (conteneur exited)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 51 | deploy-xtts-api:latest | 0ff1f7882db1 | 9.01GB | 2025-10-28 | ⚠️ Exited (0) |

### RAG Anything (conteneur exited)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 52 | rag-anything-rag-anything:latest | 0b183e46b7ed | 12GB | 2025-10-27 | ⚠️ Exited (0) |

### MemVid (nouvelles versions non utilisées)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 53 | memvid-memvid-api:latest | b004749d594e | 9.09GB | 2025-10-27 | ❌ Aucun |
| 54 | memvid-memvid-worker:latest | da6342ebcb06 | 9.09GB | 2025-10-27 | ❌ Aucun |
| 55 | memvid-memvid-ui:latest | 9a776bd26099 | 570MB | 2025-10-27 | ❌ Aucun |

### WordPress Solidarlink (conteneur exited)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 56 | wordpress:php8.3-fpm | 3003d86e585d | 725MB | 2025-09-30 | ⚠️ Exited (0) |
| 57 | wordpress:php8.3-fpm-alpine | 6f978b5963c2 | 278MB | 2025-10-01 | ❌ Aucun |
| 58 | nginx:<none> | 5e7abcdd2021 | 52.8MB | 2025-10-07 | ⚠️ Exited (0) |

**Recommandation:** VÉRIFIER AVANT SUPPRESSION - Conteneurs potentiellement réutilisables

---

## 🔴 NIVEAU 4 - PRUDENCE (Images avec conteneurs actifs)

### PaperFlow (3 images partagent le même ID - conteneurs UP)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 59 | paperflow_paperflow-api:latest | 443f4134f532 | 6.96GB | 2025-10-30 | ✅ UP (unhealthy) |
| 60 | paperflow_paperflow-flower:latest | 443f4134f532 | 6.96GB | 2025-10-30 | ✅ UP |
| 61 | paperflow_paperflow-worker:latest | 443f4134f532 | 6.96GB | 2025-10-30 | ✅ UP |

**Note:** Ces 3 images partagent le MÊME ID (même image, 3 tags) = 6.96 GB total (pas 20 GB)

### WhisperX (conteneurs exited récemment)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 62 | whisperx-whisperx:latest | c8c8fcea9ca8 | 8.77GB | 2025-10-27 | ⚠️ Exited (0) |
| 63 | whisperx-whisperx-worker:latest | 5ff1c89be817 | 8.77GB | 2025-10-27 | ⚠️ Exited (0) |
| 64 | eoranged/rq-dashboard:latest | 0ddebcbe71c4 | 242MB | 2020-08-28 | ⚠️ Exited (137) |

### WordPress Clemence (conteneurs actifs)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 65 | wordpress-clemence-custom:production | 38d68e3e6146 | 268MB | 2025-11-09 | ✅ UP (healthy) |
| 66 | wordpress-clemence-custom:phase3 | 232abbbf7c29 | 268MB | 2025-11-09 | ✅ UP (healthy) |
| 67 | wordpress-sqlite-optimized:latest | ef0a48391a86 | 373MB | 2025-11-09 | ✅ UP (unhealthy) |
| 68 | wordpress:cli-php8.3 | d02960aae1f7 | 196MB | 2025-05-07 | ⚠️ Exited (137) |

### Services en production

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 69 | support-dashboard_dashboard:latest | 7815f5dd84f5 | 838MB | 2025-10-29 | ✅ UP |
| 70 | photos-chantier_photos-chantier:latest | d81403102ee0 | 247MB | 2025-10-28 | ✅ UP |
| 71 | downto40-streamlit:latest | 3d827e92e702 | 951MB | 2025-10-28 | ✅ UP |
| 72 | discord-bot_discord-bot:latest | 1f216e8bd497 | 810MB | 2025-10-23 | ✅ UP (unhealthy) |
| 73 | telegram-bot_telegram-bot:latest | d3634fd97fcd | 155MB | 2025-10-24 | ✅ UP (healthy) |
| 74 | langchain-service_langchain-service:latest | 4c361255b825 | 325MB | 2025-10-24 | ✅ UP (healthy) |
| 75 | human-chain_backend:latest | 5b449fe5655a | 173MB | 2025-10-24 | ✅ UP (unhealthy) |
| 76 | human-chain_frontend:latest | dc25e8a4dbe1 | 53.3MB | 2025-10-24 | ✅ UP (healthy) |
| 77 | mkdocs_mkdocs:latest | bbd912a139bb | 217MB | 2025-10-23 | ✅ UP |
| 78 | faster-whisper-queue_faster-whisper-worker:latest | afd0da401eeb | 185MB | 2025-10-20 | ✅ UP |

### Monitoring & Infrastructure (NE PAS TOUCHER)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 79 | portainer/portainer-ce:latest | e6b0d4bc3234 | 186MB | 2025-09-25 | ✅ UP |
| 80 | lissy93/dashy:latest | 64e0d66683bb | 521MB | 2025-10-18 | ✅ UP (healthy) |
| 81 | prom/prometheus:latest | e2099aa77463 | 370MB | 2025-10-17 | ✅ UP |
| 82 | grafana/loki:latest | 4d58e59bc9fc | 123MB | 2025-10-13 | ✅ UP |
| 83 | grafana/promtail:latest | 0447e05db9f9 | 200MB | 2025-10-13 | ✅ UP |
| 84 | grafana/grafana:latest | 1849e2140421 | 733MB | 2025-09-23 | ✅ UP |
| 85 | mdawar/rq-exporter:latest | e7d0235d82f5 | 133MB | 2024-11-21 | ✅ UP |
| 86 | prometheuscommunity/postgres-exporter:latest | 519a5596d17c | 22.7MB | 2025-09-29 | ✅ UP |
| 87 | nicolargo/glances:latest | eb7ef01a0f2c | 86.2MB | 2025-07-09 | ✅ UP |

### Bases de données & Infrastructure (NE PAS TOUCHER)

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 88 | mysql:8.0 | 94753e67a0a9 | 780MB | 2025-09-23 | ✅ UP |
| 89 | postgres:17-alpine | 2acb7da3552b | 278MB | 2025-09-30 | ✅ UP (healthy) |
| 90 | mongo:7 | ad5e46b29e1a | 834MB | 2025-10-06 | ✅ UP |
| 91 | redis:7-alpine | 5f703438f575 | 41.4MB | 2025-10-03 | ✅ UP (healthy) |
| 92 | nginx:alpine | d4918ca78576 | 52.8MB | 2025-10-28 | ✅ UP |

### Autres services

| # | Nom | ID | Taille | Date | Conteneur |
|---|-----|---|--------|------|-----------|
| 93 | rustdesk/rustdesk-server:latest | 9227b43758be | 12.8MB | 2025-01-25 | ✅ UP |
| 94 | python:3.10-slim | 4fb709907e2a | 122MB | 2025-10-09 | ✅ UP |

**Recommandation:** NE PAS SUPPRIMER - Services en production

---

## 📊 Résumé par niveau de sécurité

| Niveau | Description | Nombre | Espace total | Risque |
|--------|-------------|--------|--------------|--------|
| 🟢 Niveau 1 | Images dangling | 33 | ~42 GB | Aucun |
| 🟡 Niveau 2 | Images inutilisées taggées | 16 | ~15 GB | Faible |
| 🟠 Niveau 3 | Conteneurs arrêtés | 10 | ~40 GB | Moyen |
| 🔴 Niveau 4 | Conteneurs actifs | 33 | ~35 GB | Élevé |

## 🎯 Recommandation de nettoyage

### Suppression immédiate (sans risque) :
- **Images 1-33 :** Toutes les images dangling = **~42 GB récupérés**

### Suppression recommandée (risque faible) :
- **Images 34-35 :** Anciennes versions memvid = **~9.65 GB**
- **Image 36 :** wordpress-test-themes = **830 MB**
- **Image 37 :** elasticsearch ancien = **1.41 GB**
- **Images 38-44 :** Bases images/outils non utilisés = **~2 GB**
- **Images 45-49 :** Applications non utilisées = **~8 GB**

### Total récupérable facilement : **~64 GB**

---

**Note:** Attendez les instructions de l'utilisateur avant de supprimer quoi que ce soit.
