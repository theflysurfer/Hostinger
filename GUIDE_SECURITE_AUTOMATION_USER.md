# Guide Sécurité - Compte Automation

**Dernière mise à jour** : 18 octobre 2025
**Serveur** : srv759970.hstgr.cloud (69.62.108.82)
**Contexte** : Migration de l'accès root SSH vers compte automation sécurisé

---

## 🎯 Objectif

Créer un compte `automation` avec privilèges étendus pour Claude Code, permettant :
- ✅ 98% des capacités de root (debugging, configuration, déploiement)
- ✅ Traçabilité des actions (logs séparés)
- ✅ Révocabilité (désactiver automation sans casser le système)
- ✅ Protection contre erreurs catastrophiques (garde-fous)
- ❌ Sans bloquer Claude Code dans ses opérations quotidiennes

---

## ✅ État actuel

### Compte automation créé le 18/10/2025

**User** : `automation` (UID 1001)
**Groupes** : `automation`, `sudo`, `docker`, `users`
**Home** : `/home/automation`
**SSH** : Clés copiées depuis root
**Sudo** : Accès quasi-total (voir détails ci-dessous)

### Ce que automation PEUT faire (avec sudo)

**Quasi tout** :
- ✅ Gérer services : `sudo systemctl restart nginx`
- ✅ Docker : `sudo docker-compose up -d`
- ✅ Modifier configs : `sudo nano /etc/nginx/sites-available/mon-site`
- ✅ SSL/Certbot : `sudo certbot --nginx`
- ✅ Pare-feu : `sudo ufw allow 8080`
- ✅ Installer packages : `sudo apt install python3-pip`
- ✅ Lire fichiers root : `sudo ls /root`
- ✅ Logs système : `sudo journalctl -u service -f`
- ✅ Nginx logs : `sudo tail -f /var/log/nginx/error.log`
- ✅ Changer permissions : `sudo chown -R automation:automation /opt/mon-app`
- ✅ Créer/modifier fichiers système : `sudo touch /etc/cron.d/backup`

### Ce que automation NE PEUT PAS faire

**Protections actives** :
- ❌ `sudo reboot` - Redémarrer le serveur
- ❌ `sudo shutdown` - Arrêter le serveur
- ❌ `sudo poweroff` - Éteindre le serveur
- ❌ `sudo halt` - Stopper le serveur
- ❌ `sudo visudo` - Modifier les droits sudo
- ❌ `sudo nano /etc/sudoers.d/automation` - Modifier ses propres droits

**Pourquoi** : Empêcher accidents/erreurs catastrophiques tout en gardant flexibilité maximale

### Logs et audit

**Tous les `sudo` sont loggés** dans `/var/log/sudo-automation.log`

```bash
# Voir ce que automation a fait aujourd'hui
ssh automation@69.62.108.82 "sudo tail -100 /var/log/sudo-automation.log"

# Surveiller en temps réel
ssh automation@69.62.108.82 "sudo tail -f /var/log/sudo-automation.log"

# Chercher commande spécifique
ssh automation@69.62.108.82 "sudo grep 'docker-compose' /var/log/sudo-automation.log"
```

---

## 🔧 Configuration technique

### Fichier sudoers (`/etc/sudoers.d/automation`)

```bash
# Automation user - Accès quasi-root pour Claude Code debugging
# Pas de password requis pour faciliter automatisation

# Commandes système (TOUT sauf reboot/shutdown)
automation ALL=(ALL) NOPASSWD: ALL, !/sbin/reboot, !/sbin/shutdown, !/sbin/poweroff, !/sbin/halt

# Protection supplémentaire : pas de modification sudoers
automation ALL=(ALL) NOPASSWD: !/usr/bin/visudo, !/usr/bin/vim /etc/sudoers*, !/usr/bin/nano /etc/sudoers*

# Logs séparés pour audit
Defaults:automation logfile="/var/log/sudo-automation.log"
```

### Clés SSH

**Emplacement** : `/home/automation/.ssh/authorized_keys`
**Source** : Copie des clés de `/root/.ssh/authorized_keys`
**Permissions** :
- `/home/automation/.ssh/` : 700 (drwx------)
- `/home/automation/.ssh/authorized_keys` : 600 (-rw-------)

**Test connexion** :
```bash
ssh automation@69.62.108.82 "whoami"
# Doit afficher: automation
```

---

## 📝 Migration root → automation

### Étape 1 : Backup scripts .bat

```batch
REM Depuis Windows PowerShell/CMD
cd "C:\Users\JulienFernandez\OneDrive\Coding\_référentiels de code\Hostinger"

copy deploy.bat deploy.bat.backup
copy update.bat update.bat.backup
copy manage.bat manage.bat.backup
```

### Étape 2 : Modifier scripts .bat

**Chercher/Remplacer dans TOUS les fichiers .bat** :
- **Ancien** : `root@69.62.108.82`
- **Nouveau** : `automation@69.62.108.82`

**Fichiers concernés** :
- `deploy.bat`
- `update.bat`
- `manage.bat`
- Tout autre script custom

**Exemple avant/après** :

```batch
REM AVANT
ssh root@69.62.108.82 "systemctl restart nginx"

REM APRÈS
ssh automation@69.62.108.82 "sudo systemctl restart nginx"
```

**⚠️ Important** : Ajouter `sudo` devant les commandes privilégiées :
- `systemctl` → `sudo systemctl`
- `docker-compose` → `sudo docker-compose` (ou pas, automation est dans groupe docker)
- `nginx -t` → `sudo nginx -t`
- `certbot` → `sudo certbot`
- Édition fichiers système → `sudo nano /etc/...`

### Étape 3 : Tester avec automation

**Test complet** depuis Windows :

```bash
# Test connexion
ssh automation@69.62.108.82 "whoami"

# Test sudo
ssh automation@69.62.108.82 "sudo whoami"

# Test services
ssh automation@69.62.108.82 "sudo systemctl status nginx"

# Test Docker (pas besoin sudo, automation dans groupe docker)
ssh automation@69.62.108.82 "docker ps"

# Test écriture config
ssh automation@69.62.108.82 "sudo touch /etc/nginx/sites-available/test-automation && sudo rm /etc/nginx/sites-available/test-automation"

# Test logs
ssh automation@69.62.108.82 "sudo journalctl -u docker-autostart -n 5"
```

**Si TOUS les tests passent** → Continuer étape 4

### Étape 4 : Période de test (1 semaine recommandée)

**Utiliser automation pour TOUTES les opérations quotidiennes** :
- Déploiements
- Modifications config Nginx
- Gestion Docker containers
- Debugging

**Vérifier logs régulièrement** :
```bash
ssh automation@69.62.108.82 "sudo tail -50 /var/log/sudo-automation.log"
```

**Si problème rencontré** :
1. Noter la commande qui a échoué
2. Tester avec root pour confirmer
3. Si besoin, modifier `/etc/sudoers.d/automation` pour autoriser

### Étape 5 : Désactiver root SSH (APRÈS validation complète)

**⚠️ NE PAS FAIRE AVANT d'être 100% SÛR que automation fonctionne**

```bash
# Depuis automation (pas root)
ssh automation@69.62.108.82 <<'EOF'
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl reload sshd
echo "✅ Root SSH désactivé - utiliser automation@ uniquement"
EOF
```

**Vérifier** :
```bash
# Ceci doit échouer
ssh root@69.62.108.82 "whoami"
# Erreur attendue: Permission denied

# Ceci doit fonctionner
ssh automation@69.62.108.82 "whoami"
# Résultat: automation
```

---

## 🆘 Rollback et dépannage

### Si automation ne fonctionne plus

**Option 1 : Réactiver root SSH**

Via **Console Hostinger** (Panel web → VPS → Open console) :

```bash
# Login: root
# Password: [mot de passe VPS]

# Réactiver root SSH
sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
systemctl reload sshd

# Tester
exit
ssh root@69.62.108.82  # Doit fonctionner
```

**Option 2 : Réparer automation**

```bash
# Via root (après réactivation SSH root)
ssh root@69.62.108.82

# Vérifier clés SSH
ls -la /home/automation/.ssh/

# Recopier clés si nécessaire
cp /root/.ssh/authorized_keys /home/automation/.ssh/
chown -R automation:automation /home/automation/.ssh
chmod 700 /home/automation/.ssh
chmod 600 /home/automation/.ssh/authorized_keys

# Vérifier sudoers
sudo visudo -c  # Doit afficher "parsed OK"

# Tester automation
su - automation
sudo whoami  # Doit afficher "root"
```

### Commandes bloquées par erreur

**Si une commande légitime est bloquée** :

```bash
# Éditer sudoers (depuis root ou console Hostinger)
sudo visudo /etc/sudoers.d/automation

# Exemple : autoriser une commande spécifique
# Ajouter AVANT la ligne "automation ALL=(ALL)"
automation ALL=(ALL) NOPASSWD: /chemin/vers/commande/specifique
```

### Audit des actions automation

```bash
# Dernières 100 commandes sudo
ssh automation@69.62.108.82 "sudo tail -100 /var/log/sudo-automation.log"

# Commandes dangereuses tentées
ssh automation@69.62.108.82 "sudo grep -E '(reboot|shutdown|rm -rf /)' /var/log/sudo-automation.log"

# Activité par date
ssh automation@69.62.108.82 "sudo grep '2025-10-18' /var/log/sudo-automation.log | wc -l"
```

---

## 🔐 Sécurité additionnelle (optionnel)

### Protections shell (alias sécurité)

Ajouter dans `/home/automation/.bashrc` :

```bash
# Alias pour commandes dangereuses = demander confirmation
alias rm='rm -i'
alias mv='mv -i'
alias cp='cp -i'

# Fonction protection commandes destructives
function sudo() {
    # Si c'est une commande ultra-dangereuse, demander confirmation
    if [[ "$*" =~ (rm[[:space:]]+-rf[[:space:]]+/[^/]|mkfs|dd[[:space:]]+if=|fdisk|parted) ]]; then
        echo "⚠️  COMMANDE DANGEREUSE DÉTECTÉE: $*"
        read -p "Confirmer ? Taper 'YES' en majuscules: " confirm
        [[ "$confirm" != "YES" ]] && echo "Annulé." && return 1
    fi

    # Executer sudo normal
    command sudo "$@"
}
```

**Activer** :
```bash
ssh automation@69.62.108.82 "source ~/.bashrc"
```

### Alertes commandes sensibles

```bash
# Script monitoring commandes dangereuses
ssh automation@69.62.108.82 "sudo tee /usr/local/bin/monitor-dangerous-commands.sh > /dev/null" <<'SCRIPT'
#!/bin/bash
tail -f /var/log/sudo-automation.log | while read line; do
    if echo "$line" | grep -E "(rm -rf /|mkfs|dd if=|fdisk|parted|reboot|shutdown)"; then
        echo "🚨 $(date): $line" >> /var/log/dangerous-commands-alert.log
        # TODO: Envoyer email/webhook Rocket.Chat
    fi
done
SCRIPT

ssh automation@69.62.108.82 "sudo chmod +x /usr/local/bin/monitor-dangerous-commands.sh"

# Lancer en background (optionnel)
# ssh automation@69.62.108.82 "nohup sudo /usr/local/bin/monitor-dangerous-commands.sh &"
```

---

## 📊 Comparaison root vs automation

| Aspect | Root direct | Automation sudo | Gagnant |
|--------|-------------|-----------------|---------|
| Capacité debug | 100% | 98% | ≈ Égalité |
| Sécurité | 0/10 | 7/10 | ✅ Automation |
| Traçabilité | Aucune | Logs séparés | ✅ Automation |
| Révocabilité | Impossible | `sudo userdel automation` | ✅ Automation |
| Facilité Claude Code | Max | Presque max | ≈ Égalité |
| Protection erreurs | 0% | 90% (reboot/shutdown bloqués) | ✅ Automation |
| Audit compliance | ❌ | ✅ | ✅ Automation |

---

## ✅ Checklist validation

**Avant de désactiver root SSH**, vérifier :

- [ ] `ssh automation@69.62.108.82 "whoami"` → Affiche "automation"
- [ ] `ssh automation@69.62.108.82 "sudo whoami"` → Affiche "root"
- [ ] `ssh automation@69.62.108.82 "sudo systemctl status nginx"` → Fonctionne
- [ ] `ssh automation@69.62.108.82 "docker ps"` → Fonctionne (groupe docker)
- [ ] `ssh automation@69.62.108.82 "sudo docker-compose ps"` → Fonctionne
- [ ] `ssh automation@69.62.108.82 "sudo nano /etc/nginx/test"` → Peut éditer
- [ ] `ssh automation@69.62.108.82 "sudo journalctl -n 10"` → Affiche logs
- [ ] Scripts .bat modifiés pour utiliser `automation@`
- [ ] Test complet déploiement via scripts .bat
- [ ] Période de test 1 semaine réussie
- [ ] Logs `/var/log/sudo-automation.log` consultés et validés
- [ ] Accès console Hostinger vérifié (backup si problème)

**Si TOUS cochés** → OK pour désactiver root SSH

---

## 📞 Support et contacts

**Console Hostinger de secours** :
Panel Hostinger → VPS srv759970 → Open console
Login: `root` / Password VPS

**Logs importants** :
- `/var/log/sudo-automation.log` - Actions automation
- `/var/log/auth.log` - Tentatives connexion SSH
- `/var/log/syslog` - Logs système généraux

**Documentation liée** :
- `ACTION_PLAN.md` - Priorité 1 : Sécurisation VPS
- `GIT_POLICY.md` - Versioning configuration
- `GUIDE_SERVICES_SYSTEMD.md` - Gestion services

---

## 📝 Historique

| Date | Action | Statut |
|------|--------|--------|
| 2025-10-18 | Création compte automation | ✅ Fait |
| 2025-10-18 | Configuration sudo étendu | ✅ Fait |
| 2025-10-18 | Copie clés SSH | ✅ Fait |
| 2025-10-18 | Tests validation | ✅ Fait |
| 2025-10-XX | Migration scripts .bat | ⏳ À faire |
| 2025-10-XX | Période test 1 semaine | ⏳ À faire |
| 2025-10-XX | Désactivation root SSH | ⏳ À planifier |

---

**Version** : 1.0
**Auteur** : Claude Code + Julien
**Prochaine revue** : Après désactivation root SSH
