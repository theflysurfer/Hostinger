# Paperless-ngx - Document Management System

**URL:** https://paperless.srv759970.hstgr.cloud
**Container:** `paperless-ngx`
**Stack:** Paperless-ngx + PostgreSQL + Redis + Tika

## Vue d'Ensemble

Paperless-ngx est un système de gestion documentaire intelligent qui numérise, indexe et organise automatiquement vos documents papier et numériques.

### Fonctionnalités Principales

- **📄 Numérisation intelligente** - Import automatique depuis scanners, email, FTP
- **🔍 OCR avancé** - Reconnaissance de texte avec Tesseract + Apache Tika
- **🏷️ Auto-tagging** - Classification automatique par machine learning
- **📊 Correspondants & Types** - Organisation par expéditeur/destinataire et catégories
- **🔐 Chiffrement** - Stockage sécurisé des documents sensibles
- **📱 Interface moderne** - UI responsive Angular avec dark mode
- **🔎 Recherche full-text** - Indexation complète avec filtres avancés
- **📧 Import email** - Consommation automatique depuis boîtes mail IMAP

## Architecture

```
┌─────────────────────────────────────────────┐
│          Paperless-ngx Frontend             │
│         (Angular SPA - Port 8000)           │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
┌───▼────────┐          ┌────────▼─────┐
│ PostgreSQL │          │    Redis     │
│  Database  │          │    Cache     │
└────────────┘          └──────────────┘
                                │
                    ┌───────────┴──────────┐
                    │                      │
              ┌─────▼─────┐         ┌──────▼──────┐
              │   Tika    │         │  Gotenberg  │
              │ (OCR/Parse)│         │    (PDF)    │
              └───────────┘         └─────────────┘
```

## Configuration

### Variables d'Environnement

```yaml
environment:
  - PAPERLESS_REDIS=redis://redis:6379
  - PAPERLESS_DBHOST=db
  - PAPERLESS_DBNAME=paperless
  - PAPERLESS_DBUSER=paperless
  - PAPERLESS_DBPASS=<password>
  - PAPERLESS_TIKA_ENABLED=1
  - PAPERLESS_TIKA_ENDPOINT=http://tika:9998
  - PAPERLESS_TIKA_GOTENBERG_ENDPOINT=http://gotenberg:3000
  - PAPERLESS_OCR_LANGUAGE=fra+eng
  - PAPERLESS_TIME_ZONE=Europe/Paris
  - PAPERLESS_ADMIN_USER=admin
  - PAPERLESS_URL=https://paperless.srv759970.hstgr.cloud
```

### Volumes

```yaml
volumes:
  - /opt/paperless/data:/usr/src/paperless/data
  - /opt/paperless/media:/usr/src/paperless/media
  - /opt/paperless/export:/usr/src/paperless/export
  - /opt/paperless/consume:/usr/src/paperless/consume
```

## Utilisation

### Import de Documents

**1. Via Interface Web**
- Glisser-déposer dans l'interface
- Upload multiple supporté

**2. Via Dossier de Consommation**
```bash
# Copier documents dans le dossier consume
cp document.pdf /opt/paperless/consume/

# Paperless détecte et traite automatiquement
```

**3. Via Email**
```bash
# Configuration IMAP dans Admin > Mail
# Paperless récupère automatiquement les pièces jointes
```

### Workflow de Traitement

```
Upload → OCR/Parsing → Classification → Tagging → Indexation → Archivage
```

1. **OCR/Parsing** - Extraction texte via Tesseract + Tika
2. **Classification** - Détection automatique du type de document
3. **Tagging** - Application des tags par règles ou ML
4. **Indexation** - Ajout au moteur de recherche full-text
5. **Archivage** - Stockage sécurisé avec versioning

### Recherche Avancée

**Syntaxe de recherche:**
```
# Recherche simple
facture edf

# Avec tags
tag:facture tag:edf

# Avec correspondant
correspondent:edf

# Par date
created:[2024-01-01 to 2024-12-31]

# Combinaison
tag:facture correspondent:edf created:[2024-01-01 to *]
```

## Intégrations

### Apache Tika

Paperless utilise Tika pour:
- Parsing de formats complexes (Office, iWork, etc.)
- OCR avancé pour images et PDF scannés
- Extraction de métadonnées

**Endpoint Tika:** http://tika.srv759970.hstgr.cloud

### Gotenberg

Service de conversion PDF pour:
- Génération de previews
- Conversion Office → PDF
- Fusion de documents

### Redis

Cache pour:
- Sessions utilisateurs
- Résultats de recherche
- Tasks Celery (processing asynchrone)

## API

### Documentation

**Swagger UI:** https://paperless.srv759970.hstgr.cloud/api/docs/

### Endpoints Principaux

```bash
# Authentification
POST /api/token/
POST /api/token/refresh/

# Documents
GET /api/documents/
GET /api/documents/{id}/
POST /api/documents/
DELETE /api/documents/{id}/

# Téléchargement
GET /api/documents/{id}/download/
GET /api/documents/{id}/preview/

# Recherche
GET /api/documents/?query=facture&tags__id__in=1,2

# Tags
GET /api/tags/
POST /api/tags/

# Correspondants
GET /api/correspondents/
POST /api/correspondents/
```

### Exemple d'Utilisation

```bash
# Obtenir un token
TOKEN=$(curl -X POST https://paperless.srv759970.hstgr.cloud/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<password>"}' \
  | jq -r .access)

# Lister les documents
curl https://paperless.srv759970.hstgr.cloud/api/documents/ \
  -H "Authorization: Bearer $TOKEN"

# Upload d'un document
curl -X POST https://paperless.srv759970.hstgr.cloud/api/documents/post_document/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "document=@facture.pdf" \
  -F "title=Facture EDF Janvier 2024"
```

## Administration

### Accès Admin

**URL:** https://paperless.srv759970.hstgr.cloud/admin/
**Username:** `admin`
**Password:** Voir `/opt/paperless/.env`

### Commandes de Gestion

```bash
# Accéder au container
docker exec -it paperless-ngx bash

# Créer un superuser
docker exec -it paperless-ngx python3 manage.py createsuperuser

# Re-indexer tous les documents
docker exec -it paperless-ngx python3 manage.py document_index reindex

# Lancer OCR sur documents existants
docker exec -it paperless-ngx python3 manage.py document_retagger --tags

# Backup
docker exec -it paperless-ngx python3 manage.py document_exporter /export/backup/
```

### Maintenance

**Nettoyage des vignettes:**
```bash
docker exec -it paperless-ngx python3 manage.py document_thumbnails --recreate
```

**Vérification de l'index:**
```bash
docker exec -it paperless-ngx python3 manage.py document_index check
```

## Sécurité

### Protection

- ✅ **HTTPS** - Let's Encrypt SSL/TLS
- ✅ **Authentification** - Comptes utilisateurs avec permissions
- ✅ **Basic Auth Nginx** - Protection supplémentaire au niveau proxy
- ✅ **CORS** - Configuré pour l'API

### Recommandations

1. ✅ Activer 2FA pour les comptes admin
2. ✅ Rotation régulière des tokens API
3. ✅ Limiter les permissions par utilisateur
4. ✅ Chiffrer les documents sensibles

## Troubleshooting

### Les Documents ne Sont pas Traités

**Vérifier les workers:**
```bash
docker logs paperless-ngx | grep celery
docker exec -it paperless-ngx celery -A paperless inspect active
```

**Vérifier la queue:**
```bash
docker exec -it paperless-ngx celery -A paperless inspect reserved
```

### OCR Échoue

**Vérifier Tika:**
```bash
curl http://tika.srv759970.hstgr.cloud
```

**Vérifier les logs OCR:**
```bash
docker logs paperless-ngx | grep -i ocr
```

### Problèmes de Performance

**Augmenter les workers:**
```yaml
environment:
  - PAPERLESS_TASK_WORKERS=4
  - PAPERLESS_THREADS_PER_WORKER=2
```

## Monitoring

### Métriques

- Documents totaux
- Documents traités aujourd'hui
- Queue size
- Temps moyen de traitement
- Espace disque utilisé

### Logs

```bash
# Logs temps réel
docker logs -f paperless-ngx

# Logs Celery
docker logs paperless-ngx | grep celery

# Logs OCR
docker logs paperless-ngx | grep tesseract
```

## Voir Aussi

- [Apache Tika](../ai/tika.md) - Service de parsing utilisé par Paperless
- [Monitoring](../infrastructure/monitoring.md) - Stack Grafana + Prometheus
- [Infrastructure > Backup](../../guides/operations/backup-restore.md)

## Liens Externes

- **Documentation officielle:** https://docs.paperless-ngx.com/
- **GitHub:** https://github.com/paperless-ngx/paperless-ngx
- **Forum:** https://github.com/paperless-ngx/paperless-ngx/discussions

---

**Dernière mise à jour:** 2025-10-23
**Prochaine révision:** Après optimisation OCR
