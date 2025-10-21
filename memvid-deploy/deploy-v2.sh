#!/bin/bash
# Deploy MemVid RAG V2 to server

set -e

SERVER="root@69.62.108.82"
REMOTE_DIR="/opt/memvid"

echo "🚀 Deploying MemVid RAG V2..."

# 1. Transfer files
echo "📦 Transferring files to server..."
tar czf - . | ssh $SERVER "cd $REMOTE_DIR && tar xzf -"

# 2. Backup v1 if exists
echo "💾 Backing up V1..."
ssh $SERVER "cd $REMOTE_DIR && if [ -f docker-compose.yml ]; then cp docker-compose.yml docker-compose.v1.yml.bak; fi"

# 3. Switch to V2
echo "🔄 Switching to V2..."
ssh $SERVER "cd $REMOTE_DIR && cp docker-compose.v2.yml docker-compose.yml"

# 4. Stop v1
echo "⏹️  Stopping V1..."
ssh $SERVER "cd $REMOTE_DIR && docker-compose down || true"

# 5. Build and start V2
echo "🏗️  Building V2..."
ssh $SERVER "cd $REMOTE_DIR && docker-compose build"

echo "▶️  Starting V2..."
ssh $SERVER "cd $REMOTE_DIR && docker-compose up -d"

# 6. Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# 7. Check status
echo "✅ Checking status..."
ssh $SERVER "cd $REMOTE_DIR && docker-compose ps"

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 Services:"
echo "  - API:  https://memvid.srv759970.hstgr.cloud"
echo "  - UI:   https://memvid-ui.srv759970.hstgr.cloud"
echo ""
echo "📝 Next steps:"
echo "  1. Configure Nginx for UI (port 8505)"
echo "  2. Setup SSL for UI subdomain"
echo "  3. Add to auto-start system"
echo ""
