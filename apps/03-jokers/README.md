# Jokers Hockey - Site Web du Club

Site web vitrine pour le club de hockey sur glace Les Jokers.

## 🔗 Accès

- **URL Production**: https://jokers.xxx.fr
- **Localisation serveur**: `/var/www/jokers`
- **Port**: 5000
- **Process PM2**: `jokers-hockey`

## 🛠️ Stack Technique

- Frontend: React 18 + Vite 5 + TypeScript
- Backend: Express + Node.js 20
- Database: Neon PostgreSQL (serverless)
- ORM: Drizzle
- UI: shadcn/ui + Tailwind CSS
- Process Manager: PM2
- Reverse Proxy: Nginx
- SSL: Let's Encrypt

## 📚 Documentation Complète

Voir la documentation complète dans le référentiel:
`docs/docs/02-applications/cms-sites/jokers-hockey.md`

## 🚀 Commandes Rapides

### Déploiement

```bash
ssh root@srv759970.hstgr.cloud
cd /var/www/jokers
git pull origin main
npm install --production=false
npm run build
pm2 restart jokers-hockey
```

### Logs

```bash
# Logs application
pm2 logs jokers-hockey

# Logs Nginx
tail -f /var/log/nginx/jokers_access.log
tail -f /var/log/nginx/jokers_error.log
```

### Monitoring

```bash
# Statut de l'application
pm2 status

# Métriques en temps réel
pm2 monit

# État du serveur
curl -I https://jokers.xxx.fr
```

## 🔐 Variables d'Environnement

Fichier `.env` dans `/var/www/jokers/`:

```env
NODE_ENV=production
PORT=5000
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/jokers_prod?sslmode=require
```

## 📂 Code Source

Localisation: `C:\Users\julien\OneDrive\Coding\_Projets de code\2025.11 Site Web Jokers`

## 🗄️ Base de Données

- Provider: Neon (PostgreSQL serverless)
- Console: https://console.neon.tech
- Database: `jokers_prod`
- Backup: Automatique via Neon

## 🔄 Processus de Déploiement

1. Build local: `npm run build`
2. Upload vers serveur (Git ou SCP)
3. Install dépendances: `npm install`
4. Push schéma BDD: `npm run db:push`
5. Build: `npm run build`
6. Restart PM2: `pm2 restart jokers-hockey`

## ⚠️ Notes

- Certificat SSL auto-renouvelable via Let's Encrypt
- Backup BDD automatique via Neon
- Ne jamais commiter le fichier `.env`
- Tester sur branche staging Neon avant production
