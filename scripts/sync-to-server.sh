#!/bin/bash
#
# sync-to-server.sh
# Script pour déployer les configurations du repo local vers le serveur srv759970
#
# Usage: ./scripts/sync-to-server.sh [--dry-run] [--service SERVICE_NAME]
#

set -e

SERVER="root@69.62.108.82"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_CONFIGS="$REPO_ROOT/server-configs"

DRY_RUN=false
SPECIFIC_SERVICE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--dry-run] [--service SERVICE_NAME]"
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    echo "🔍 MODE DRY-RUN: Aucune modification ne sera effectuée"
    echo ""
fi

echo "📤 Déploiement des configurations vers srv759970.hstgr.cloud..."
echo "📂 Source: $SERVER_CONFIGS"
echo ""

# Function to execute or display command
exec_or_dry() {
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] $@"
    else
        eval "$@"
    fi
}

# ============================================================================
# 1. DOCKER COMPOSE FILES
# ============================================================================
if [[ -z "$SPECIFIC_SERVICE" ]] || [[ "$SPECIFIC_SERVICE" == "docker-compose" ]]; then
    echo "📦 [1/4] Déploiement Docker Compose files..."

    for compose_file in "$SERVER_CONFIGS/docker-compose"/*.yml; do
        if [ -f "$compose_file" ]; then
            service_name=$(basename "$compose_file" .yml)
            echo "  → $service_name"

            # Backup de l'ancien fichier
            exec_or_dry "ssh $SERVER 'if [ -f /opt/$service_name/docker-compose.yml ]; then cp /opt/$service_name/docker-compose.yml /opt/$service_name/docker-compose.yml.backup-\$(date +%Y%m%d-%H%M%S); fi'"

            # Upload nouveau fichier
            exec_or_dry "scp $compose_file $SERVER:/opt/$service_name/docker-compose.yml"
            echo "    ✓ Déployé"
        fi
    done
    echo ""
fi

# ============================================================================
# 2. NGINX CONFIGURATIONS
# ============================================================================
if [[ -z "$SPECIFIC_SERVICE" ]] || [[ "$SPECIFIC_SERVICE" == "nginx" ]]; then
    echo "🌐 [2/4] Déploiement Nginx configurations..."

    # Sites
    if [ -d "$SERVER_CONFIGS/nginx/sites-available" ]; then
        echo "  → Sites disponibles..."
        for site_file in "$SERVER_CONFIGS/nginx/sites-available"/*; do
            if [ -f "$site_file" ]; then
                site_name=$(basename "$site_file")
                echo "    • $site_name"

                # Backup
                exec_or_dry "ssh $SERVER 'if [ -f /etc/nginx/sites-available/$site_name ]; then cp /etc/nginx/sites-available/$site_name /etc/nginx/sites-available/$site_name.backup-\$(date +%Y%m%d-%H%M%S); fi'"

                # Upload
                exec_or_dry "scp $site_file $SERVER:/etc/nginx/sites-available/$site_name"
            fi
        done
    fi

    # Snippets
    if [ -d "$SERVER_CONFIGS/nginx/snippets" ]; then
        echo "  → Snippets..."
        for snippet_file in "$SERVER_CONFIGS/nginx/snippets"/*; do
            if [ -f "$snippet_file" ]; then
                snippet_name=$(basename "$snippet_file")
                echo "    • $snippet_name"
                exec_or_dry "scp $snippet_file $SERVER:/etc/nginx/snippets/$snippet_name"
            fi
        done
    fi

    # Test nginx config
    if [ "$DRY_RUN" = false ]; then
        echo "  → Test de la configuration Nginx..."
        if ssh $SERVER "nginx -t 2>&1"; then
            echo "    ✅ Configuration valide"

            # Reload nginx
            read -p "  Recharger Nginx maintenant? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ssh $SERVER "systemctl reload nginx"
                echo "    ✓ Nginx rechargé"
            fi
        else
            echo "    ❌ Erreur de configuration Nginx!"
            echo "    ⚠️  Les fichiers ont été uploadés mais Nginx n'a PAS été rechargé"
            exit 1
        fi
    fi

    echo ""
fi

# ============================================================================
# 3. DASHY CONFIGURATION
# ============================================================================
if [[ -z "$SPECIFIC_SERVICE" ]] || [[ "$SPECIFIC_SERVICE" == "dashy" ]]; then
    echo "📊 [3/4] Déploiement Dashy configuration..."

    if [ -f "$SERVER_CONFIGS/dashy/conf.yml" ]; then
        # Backup
        exec_or_dry "ssh $SERVER 'if [ -f /opt/dashy/conf.yml ]; then cp /opt/dashy/conf.yml /opt/dashy/conf.yml.backup-\$(date +%Y%m%d-%H%M%S); fi'"

        # Upload
        exec_or_dry "scp $SERVER_CONFIGS/dashy/conf.yml $SERVER:/opt/dashy/conf.yml"
        echo "  ✓ conf.yml déployé"

        # Restart Dashy
        if [ "$DRY_RUN" = false ]; then
            read -p "  Redémarrer Dashy maintenant? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ssh $SERVER "cd /opt/dashy && docker-compose restart"
                echo "  ✓ Dashy redémarré"
            fi
        fi
    fi

    echo ""
fi

# ============================================================================
# 4. SYSTEMD SERVICES
# ============================================================================
if [[ -z "$SPECIFIC_SERVICE" ]] || [[ "$SPECIFIC_SERVICE" == "systemd" ]]; then
    echo "⚙️  [4/4] Déploiement Systemd services..."

    if [ -d "$SERVER_CONFIGS/systemd" ]; then
        for service_file in "$SERVER_CONFIGS/systemd"/*.service; do
            if [ -f "$service_file" ]; then
                service_name=$(basename "$service_file")
                echo "  → $service_name"

                # Upload
                exec_or_dry "scp $service_file $SERVER:/etc/systemd/system/$service_name"

                # Reload daemon
                if [ "$DRY_RUN" = false ]; then
                    ssh $SERVER "systemctl daemon-reload"
                    echo "    ✓ Daemon rechargé"
                fi
            fi
        done
    fi

    echo ""
fi

echo "============================================================================"
if [ "$DRY_RUN" = true ]; then
    echo "✅ Dry-run terminé! Aucune modification effectuée."
    echo ""
    echo "Pour déployer réellement, relancez sans --dry-run:"
    echo "  ./scripts/sync-to-server.sh"
else
    echo "✅ Déploiement terminé!"
    echo ""
    echo "📋 Services déployés:"
    [ -d "$SERVER_CONFIGS/docker-compose" ] && echo "  ✓ Docker Compose: $(ls -1 $SERVER_CONFIGS/docker-compose/*.yml 2>/dev/null | wc -l) fichiers"
    [ -d "$SERVER_CONFIGS/nginx/sites-available" ] && echo "  ✓ Nginx Sites: $(ls -1 $SERVER_CONFIGS/nginx/sites-available/* 2>/dev/null | wc -l) sites"
    [ -f "$SERVER_CONFIGS/dashy/conf.yml" ] && echo "  ✓ Dashy: conf.yml"
    echo ""
    echo "⚠️  N'oubliez pas de:"
    echo "  1. Vérifier les services: ssh root@69.62.108.82 'docker ps'"
    echo "  2. Vérifier Nginx: ssh root@69.62.108.82 'nginx -t'"
    echo "  3. Vérifier les logs si problème"
fi
echo "============================================================================"
echo ""
