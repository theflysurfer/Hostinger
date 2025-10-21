# 🎬 Guide VideoRAG - Installation et Configuration

> **VideoRAG**: Chat with Your Videos - Système d'analyse vidéo par IA avec interface web

**Date d'installation**: 20 Octobre 2025
**Serveur**: srv759970.hstgr.cloud (69.62.108.82)
**URL**: https://videorag.srv759970.hstgr.cloud ✅ **HTTPS ACTIVÉ**

---

## 📋 Installation Complète

VideoRAG a été installé avec succès sur votre VPS avec tous les composants nécessaires.

### ✅ Ce qui a été installé:

1. **Python 3.11** via Miniconda (`/opt/miniconda/envs/vimo`)
2. **VideoRAG Backend API** (Flask sur port 5000)
3. **Modèles IA** (~8GB total):
   - MiniCPM-V-2_6-int4 (4GB)
   - Whisper large-v3 (1.5GB)
   - ImageBind huge (2.4GB)
4. **Interface Web** simple en `/opt/videorag-web`
5. **Service systemd** `videorag.service`
6. **Configuration Nginx** avec reverse proxy
7. **Certificat SSL Let's Encrypt** (HTTPS configuré)

---

## 🚀 Démarrage Rapide

### Étape 1: Configurer votre clé OpenAI

```bash
ssh root@69.62.108.82
/opt/videorag/set_openai_key.sh sk-proj-VOTRE_CLE_OPENAI
```

### Étape 2: Démarrer le service

```bash
systemctl enable videorag
systemctl start videorag
systemctl status videorag
```

### Étape 3: Accéder

- **Interface Web**: http://videorag.srv759970.hstgr.cloud
- **API Directe**: http://69.62.108.82:5000/health

---

## 📁 Emplacements

| Composant | Chemin |
|-----------|--------|
| Repository principal | `/opt/videorag/` |
| Backend API | `/opt/videorag/Vimo-desktop/python_backend/` |
| Modèles | `/opt/videorag/VideoRAG-algorithm/` |
| Frontend Web | `/opt/videorag-web/` |
| Service | `/etc/systemd/system/videorag.service` |
| Config Nginx | `/etc/nginx/sites-available/videorag` |
| Documentation | `/opt/videorag/README_INSTALL.md` |

---

## 🔧 Gestion du Service

```bash
# Démarrer/Arrêter/Redémarrer
systemctl start videorag
systemctl stop videorag
systemctl restart videorag

# Status
systemctl status videorag

# Logs en temps réel
journalctl -u videorag -f

# Dernières 100 lignes de logs
journalctl -u videorag -n 100
```

---

## 📡 API Endpoints

### Base URL
- Via Nginx: `http://videorag.srv759970.hstgr.cloud/api/`
- Direct: `http://localhost:5000/`

### Endpoints

1. **GET /health** - Vérifier si l'API fonctionne
2. **POST /upload** - Upload une vidéo
3. **POST /query** - Poser une question sur les vidéos
4. **GET /videos** - Lister les vidéos uploadées

### Exemples

```bash
# Health check
curl http://localhost:5000/health

# Upload
curl -X POST -F "video=@video.mp4" http://localhost:5000/upload

# Query
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What happens in the video?"}' \
  http://localhost:5000/query
```

---

## 🔐 Sécurité

### Changer la clé OpenAI

```bash
# Option 1: Script
/opt/videorag/set_openai_key.sh sk-proj-NOUVELLE_CLE

# Option 2: Manuel
nano /etc/systemd/system/videorag.service
systemctl daemon-reload
systemctl restart videorag
```

### Limite d'upload (actuellement 5GB)

```bash
nano /etc/nginx/sites-available/videorag
# Modifier: client_max_body_size 5000M;
systemctl reload nginx
```

### Ajouter HTTPS

```bash
certbot --nginx -d videorag.srv759970.hstgr.cloud
```

---

## 🐛 Troubleshooting

### Service ne démarre pas

```bash
journalctl -u videorag -n 50
lsof -i :5000
systemctl status videorag
```

### API ne répond pas

```bash
curl http://localhost:5000/health
systemctl status videorag
nginx -t
```

### Modèles introuvables

```bash
ls -lh /opt/videorag/VideoRAG-algorithm/MiniCPM-V-2_6-int4/
ls -lh /opt/videorag/VideoRAG-algorithm/faster-distil-whisper-large-v3/
ls -lh /opt/videorag/VideoRAG-algorithm/.checkpoints/
```

---

## 📚 Documentation

- **Documentation complète**: `/opt/videorag/README_INSTALL.md`
- **GitHub VideoRAG**: https://github.com/HKUDS/VideoRAG
- **Paper**: https://arxiv.org/abs/2502.01549
- **Guides locaux**: `docs/guides/`

---

## ✅ Checklist

- [ ] Clé OpenAI configurée
- [ ] Service démarré
- [ ] Interface web accessible
- [ ] API répond (/health)
- [ ] Test upload vidéo
- [ ] Test query vidéo
- [ ] HTTPS configuré (optionnel)
- [ ] Basic Auth ajouté (optionnel)

---

**Installation**: 20 Octobre 2025
**Par**: Claude Code
