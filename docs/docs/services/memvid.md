# MemVid - Video Memory RAG System

**Service de RAG (Retrieval Augmented Generation) utilisant la vidéo comme stockage.**

---

## 📋 Vue d'ensemble

**URL Production** : https://memvid.srv759970.hstgr.cloud
**Type** : Service AI/ML - RAG System
**Port** : 8000
**Container** : `memvid`
**Status** : 🟢 Production

### Description

MemVid est un système innovant de RAG qui encode le texte dans des vidéos MP4 via QR codes, permettant:
- Recherche sémantique ultra-rapide (<100ms pour 1M de chunks)
- Réduction de stockage 50-100x vs bases vectorielles traditionnelles
- Indexation et recherche de texte avec embeddings

---

## 🚀 Endpoints API

### Indexer du texte

```bash
curl -X POST https://memvid.srv759970.hstgr.cloud/index/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text content to index"
  }'
```

### Rechercher

```bash
curl -X POST https://memvid.srv759970.hstgr.cloud/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search query",
    "top_k": 3
  }'
```

### Health Check

```bash
curl https://memvid.srv759970.hstgr.cloud/health
```

---

## 🐳 Configuration Docker

**Container** : `memvid`
**Image** : Custom (à documenter)
**Réseau** : Internal bridge
**Volumes** :
- Stockage vidéos encodées
- Base de données embeddings

**Auto-start** : Oui (haute priorité)

---

## 📊 Caractéristiques Techniques

### Performance
- **Recherche** : <100ms pour 1 million de chunks
- **Compression** : 50-100x vs bases vectorielles
- **Encodage** : Texte → QR codes → MP4

### Cas d'usage
- Documentation technique volumineuse
- Base de connaissances d'entreprise
- Archives textuelles
- RAG à faible coût de stockage

---

## 🔧 Opérations

### Démarrer le service

```bash
ssh srv759970
docker start memvid
docker logs -f memvid
```

### Vérifier l'état

```bash
docker ps | grep memvid
curl https://memvid.srv759970.hstgr.cloud/health
```

### Troubleshooting

**Service ne répond pas** :
```bash
# Vérifier logs
docker logs memvid --tail 100

# Restart
docker restart memvid

# Vérifier Nginx
sudo nginx -t
sudo systemctl status nginx
```

**Espace disque** :
```bash
# Vérifier utilisation
du -sh /path/to/memvid/volumes

# Nettoyer anciennes vidéos si nécessaire
docker exec memvid cleanup-old-videos
```

---

## 📚 Documentation

### Liens utiles
- **Repository** : (À compléter)
- **Documentation officielle** : (À compléter)
- **Configuration Nginx** : `/etc/nginx/sites-available/memvid`

### Infrastructure
- **Server** : srv759970.hstgr.cloud (69.62.108.82)
- **SSL** : Let's Encrypt (auto-renewal)
- **Monitoring** : Grafana dashboard

---

## 🔐 Sécurité

**Accès** :
- ✅ HTTPS obligatoire
- ⚠️ Pas d'authentification actuellement (API publique)
- 🔒 Rate limiting via Nginx

**Considérations** :
- Évaluer besoin d'authentification selon usage
- Monitorer utilisation API
- Backup régulier des vidéos encodées

---

## 📝 Notes

- Service expérimental avec technologie innovante
- Performance exceptionnelle pour RAG à grande échelle
- À documenter: processus d'encodage/décodage
- À documenter: gestion du cycle de vie des vidéos

---

**Dernière mise à jour** : 2025-12-04
**Maintenu par** : Infrastructure team
