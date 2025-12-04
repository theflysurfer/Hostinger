#!/bin/bash
# Update dynamic documentation sections from server
# Run this locally to refresh server-status.md and services-status.md

set -e

SERVER="automation@69.62.108.82"
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../docs/docs/99-dynamic && pwd)"

echo "🔄 Updating dynamic documentation sections..."

# Generate server-status.md
echo "📊 Generating server-status.md..."
cat > "$DOCS_DIR/server-status.md" << 'HEADER'
# Server Status - srv759970.hstgr.cloud

**Auto-généré** : Mis à jour automatiquement depuis le serveur.

---

## 💻 Informations Système

HEADER

ssh $SERVER "
echo '**Hostname**: \`'$(hostname)'\`'
echo '**IP**: 69.62.108.82'
echo '**OS**: '$(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2)
echo '**Kernel**: '$(uname -r)
echo '**Uptime**: '$(uptime -p)
echo ''
echo '## 🧠 RAM'
echo ''
echo '\`\`\`'
free -h
echo '\`\`\`'
echo ''
echo '## 💾 Disque'
echo ''
echo '\`\`\`'
df -h | head -10
echo '\`\`\`'
echo ''
echo '## 📊 Load Average'
echo ''
echo '\`\`\`'
uptime
echo '\`\`\`'
" >> "$DOCS_DIR/server-status.md"

echo "✓ server-status.md updated"

# Generate services-status.md
echo "🐳 Generating services-status.md..."
cat > "$DOCS_DIR/services-status.md" << 'HEADER'
# Services Status - Docker Containers

**Auto-généré** : État actuel des conteneurs Docker sur srv759970.

---

## 🟢 Conteneurs Actifs

HEADER

ssh $SERVER "
echo '\`\`\`'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | head -30
echo '\`\`\`'
echo ''
echo '**Total conteneurs actifs**: '$(docker ps -q | wc -l)
echo ''
echo '## 📊 Statistiques'
echo ''
echo '\`\`\`'
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | head -20
echo '\`\`\`'
echo ''
echo '## 🔴 Conteneurs Arrêtés (5 derniers)'
echo ''
echo '\`\`\`'
docker ps -a --filter 'status=exited' --format 'table {{.Names}}\t{{.Status}}' | head -6
echo '\`\`\`'
" >> "$DOCS_DIR/services-status.md"

echo "✓ services-status.md updated"

echo ""
echo "✅ Dynamic sections updated successfully!"
echo "📍 Location: $DOCS_DIR"
echo ""
echo "Next steps:"
echo "  1. Review the generated files"
echo "  2. Rebuild MkDocs: cd docs && mkdocs build"
echo "  3. Commit changes if satisfied"
