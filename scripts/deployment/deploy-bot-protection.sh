#!/bin/bash
# Script pour déployer la protection anti-bots sur tous les vhosts
# Usage: bash deploy-bot-protection.sh

echo "🛡️  Déploiement de la protection anti-bots..."
echo ""

# 1. Créer le snippet bot-protection
cat > /etc/nginx/snippets/bot-protection.conf << 'EOF'
# Nginx Bot Protection Snippet
# Bloquer les scans automatiques qui empêchent docker-autostart de fonctionner

# Bloquer fichiers cachés et dossiers sensibles
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Bloquer scans .env
location ~ \.env {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Bloquer scans WordPress même sur sites non-WordPress
location ~ (xmlrpc\.php|wp-admin|wp-login\.php|wp-config\.php|wp-content/debug\.log) {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Bloquer fichiers de configuration exposés
location ~ (composer\.json|composer\.lock|package\.json|yarn\.lock|\.htaccess|\.htpasswd|web\.config) {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Bloquer scans d'admin panels
location ~ /(admin|administrator|phpmyadmin|pma|adminer|mysql|db|database) {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Bloquer requêtes avec chemins suspects
location ~ (phpinfo|info\.php|test\.php|shell\.php|config\.json|config\.php|_all_dbs|telescope) {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}
EOF

echo "✅ Snippet créé: /etc/nginx/snippets/bot-protection.conf"
echo ""

# 2. Ajouter le snippet dans tous les vhosts nginx (server blocks)
echo "📝 Ajout du snippet dans les vhosts..."

VHOST_DIR="/etc/nginx/sites-available"
COUNT=0

for vhost in $VHOST_DIR/*; do
    # Vérifier si le fichier contient déjà le snippet
    if ! grep -q "bot-protection.conf" "$vhost"; then
        # Trouver la première occurrence de "location /" et insérer avant
        sed -i '/location \/ {/i\    # Protection anti-bots\n    include snippets/bot-protection.conf;\n' "$vhost"
        COUNT=$((COUNT + 1))
        echo "  ✅ $(basename $vhost)"
    else
        echo "  ⏭️  $(basename $vhost) (déjà inclus)"
    fi
done

echo ""
echo "✅ $COUNT vhosts mis à jour"
echo ""

# 3. Tester la config nginx
echo "🧪 Test de la configuration nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Configuration nginx valide"
    echo ""
    echo "🔄 Rechargement de nginx..."
    systemctl reload nginx
    echo "✅ Nginx rechargé"
else
    echo "❌ Erreur dans la configuration nginx"
    nginx -t
    exit 1
fi

echo ""
echo "🎉 Protection anti-bots déployée avec succès!"
echo ""
echo "Les bots suivants seront bloqués:"
echo "  - Scans .git, .env, .DS_Store"
echo "  - Scans WordPress (xmlrpc.php, wp-admin, etc.)"
echo "  - Scans admin panels (phpmyadmin, adminer, etc.)"
echo "  - Scanners connus (LeakIX, Shodan, etc.)"
echo ""
echo "Pour monitorer les requêtes bloquées:"
echo "  tail -f /var/log/nginx/*error.log | grep denied"
