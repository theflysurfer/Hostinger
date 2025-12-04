# 🤖 Guide - MCP Servers (Model Context Protocol)

## 🎯 Architecture

Le serveur Hostinger héberge deux serveurs MCP :
- **Node.js MCP Server** (port 3000)
- **Python MCP Server** (port 8000)

Accessible via : `https://mcp.srv759970.hstgr.cloud`

---

## 📋 Serveurs déployés

### 1. Node.js MCP Server

**URL** : https://mcp.srv759970.hstgr.cloud/nodejs/
**Port interne** : 3000
**Service** : `mcp-nodejs.service`
**Localisation** : `/var/www/mcp-servers/nodejs/`

**Technologies** :
- Node.js 22.20.0 LTS
- Express.js
- @modelcontextprotocol/sdk

**Endpoints** :
- `GET /health` - Health check
- `GET /mcp/tools` - Liste des outils disponibles
- `POST /mcp/execute` - Exécuter un outil

### 2. Python MCP Server

**URL** : https://mcp.srv759970.hstgr.cloud/python/
**Port interne** : 8000
**Service** : `mcp-python.service`
**Localisation** : `/var/www/mcp-servers/python/`

**Technologies** :
- Python 3.12.3
- FastAPI
- Uvicorn
- mcp (pip package)
- uv (package manager)

**Endpoints** :
- `GET /health` - Health check
- `GET /mcp/tools` - Liste des outils disponibles
- `POST /mcp/execute` - Exécuter un outil
- `GET /docs` - Documentation Swagger automatique

---

## 🔧 Configuration serveur

### Structure des fichiers

```
/var/www/mcp-servers/
├── nodejs/
│   ├── server.js
│   ├── package.json
│   └── node_modules/
└── python/
    ├── main.py
    ├── .venv/
    └── pyproject.toml
```

### Services systemd

```bash
# Statut des services
systemctl status mcp-nodejs
systemctl status mcp-python

# Redémarrer
systemctl restart mcp-nodejs
systemctl restart mcp-python

# Logs
journalctl -u mcp-nodejs -f
journalctl -u mcp-python -f
```

---

## 💻 Utilisation côté client

### Avec npx (Node.js / TypeScript)

#### Installation rapide

```bash
# Pas d'installation locale nécessaire !
# npx télécharge et exécute automatiquement
```

#### Exemple d'utilisation

```bash
# Appeler le serveur MCP Node.js
npx node-fetch https://mcp.srv759970.hstgr.cloud/nodejs/health \
  --user julien:DevAccess2025
```

#### Script client Node.js

```javascript
// client-mcp-nodejs.js
import fetch from 'node-fetch';

const MCP_BASE_URL = 'https://mcp.srv759970.hstgr.cloud/nodejs';
const AUTH = 'Basic ' + Buffer.from('julien:DevAccess2025').toString('base64');

async function callMCP(tool, parameters) {
  const response = await fetch(`${MCP_BASE_URL}/mcp/execute`, {
    method: 'POST',
    headers: {
      'Authorization': AUTH,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ tool, parameters })
  });

  return await response.json();
}

// Utilisation
callMCP('example-tool', { param1: 'value1', param2: 'value2' })
  .then(result => console.log(result))
  .catch(err => console.error(err));
```

#### Exécution

```bash
npx node client-mcp-nodejs.js
```

---

### Avec uvx (Python)

#### Installation rapide

```bash
# Installer uv (si pas déjà fait)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ajouter au PATH
export PATH="$HOME/.local/bin:$PATH"
```

#### Script client Python

```python
# client_mcp_python.py
import httpx
import asyncio
from base64 import b64encode

MCP_BASE_URL = "https://mcp.srv759970.hstgr.cloud/python"
AUTH_USER = "julien"
AUTH_PASS = "DevAccess2025"

async def call_mcp(tool: str, parameters: dict):
    # Créer le header Basic Auth
    credentials = b64encode(f"{AUTH_USER}:{AUTH_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MCP_BASE_URL}/mcp/execute",
            headers=headers,
            json={"tool": tool, "parameters": parameters}
        )
        return response.json()

# Utilisation
async def main():
    result = await call_mcp(
        "example-python-tool",
        {"param1": "value1", "param2": "value2"}
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Créer un pyproject.toml

```toml
[project]
name = "mcp-client"
version = "0.1.0"
dependencies = [
    "httpx",
]
```

#### Exécution avec uvx

```bash
# Option 1 : Exécuter directement avec uvx
uvx --with httpx python client_mcp_python.py

# Option 2 : Créer un environnement et exécuter
uv venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows
uv pip install httpx
python client_mcp_python.py
```

---

## 🔐 Authentification

Tous les serveurs MCP nécessitent **HTTP Basic Authentication** :
- **Username** : `julien`
- **Password** : `DevAccess2025`

### Exemples d'auth

#### cURL

```bash
curl -u julien:DevAccess2025 https://mcp.srv759970.hstgr.cloud/nodejs/health
```

#### Python (requests)

```python
import requests

response = requests.get(
    'https://mcp.srv759970.hstgr.cloud/python/health',
    auth=('julien', 'DevAccess2025')
)
print(response.json())
```

#### JavaScript (fetch)

```javascript
const credentials = btoa('julien:DevAccess2025');
fetch('https://mcp.srv759970.hstgr.cloud/nodejs/health', {
  headers: {
    'Authorization': `Basic ${credentials}`
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 📊 Endpoints disponibles

### GET /health

**Description** : Health check du serveur

**Réponse** :
```json
{
  "status": "healthy",
  "service": "MCP Node.js Server"
}
```

### GET /mcp/tools

**Description** : Liste tous les outils MCP disponibles

**Réponse** :
```json
{
  "tools": [
    {
      "name": "example-tool",
      "description": "Example MCP tool",
      "parameters": ["param1", "param2"]
    }
  ]
}
```

### POST /mcp/execute

**Description** : Exécute un outil MCP

**Request Body** :
```json
{
  "tool": "example-tool",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Réponse** :
```json
{
  "success": true,
  "tool": "example-tool",
  "result": "Executed example-tool with parameters",
  "timestamp": "2025-10-16T19:30:00.000Z"
}
```

---

## 🛠️ Développement de nouveaux outils MCP

### Ajouter un outil Node.js

1. SSH sur le serveur :
```bash
ssh root@69.62.108.82
cd /var/www/mcp-servers/nodejs
```

2. Modifier `server.js` :
```javascript
// Ajouter un nouvel endpoint
app.post('/mcp/custom-tool', (req, res) => {
  const { param1, param2 } = req.body;

  // Votre logique ici
  const result = doSomething(param1, param2);

  res.json({
    success: true,
    result: result
  });
});
```

3. Redémarrer le service :
```bash
systemctl restart mcp-nodejs
```

### Ajouter un outil Python

1. SSH sur le serveur :
```bash
ssh root@69.62.108.82
cd /var/www/mcp-servers/python
source .venv/bin/activate
```

2. Modifier `main.py` :
```python
@app.post("/mcp/custom-tool")
def custom_tool(param1: str, param2: str):
    # Votre logique ici
    result = do_something(param1, param2)

    return {
        "success": True,
        "result": result
    }
```

3. Redémarrer le service :
```bash
systemctl restart mcp-python
```

---

## 📚 Exemples d'intégration

### Dans Claude Desktop

**Configuration** (`claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "hostinger-nodejs": {
      "url": "https://mcp.srv759970.hstgr.cloud/nodejs",
      "auth": {
        "type": "basic",
        "username": "julien",
        "password": "DevAccess2025"
      }
    },
    "hostinger-python": {
      "url": "https://mcp.srv759970.hstgr.cloud/python",
      "auth": {
        "type": "basic",
        "username": "julien",
        "password": "DevAccess2025"
      }
    }
  }
}
```

### Dans un workflow n8n

1. Ajouter node **HTTP Request**
2. Configuration :
   - **Method** : POST
   - **URL** : `https://mcp.srv759970.hstgr.cloud/python/mcp/execute`
   - **Authentication** : Basic Auth
   - **Body** : JSON `{"tool": "my-tool", "parameters": {...}}`

---

## 🧪 Tests

### Test Node.js MCP

```bash
curl -u julien:DevAccess2025 \
  -X POST https://mcp.srv759970.hstgr.cloud/nodejs/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "example-tool",
    "parameters": {"param1": "test", "param2": "value"}
  }'
```

### Test Python MCP

```bash
curl -u julien:DevAccess2025 \
  -X POST https://mcp.srv759970.hstgr.cloud/python/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "example-python-tool",
    "parameters": {"param1": "test", "param2": "value"}
  }'
```

### Test avec Python uvx

```bash
# Créer un script de test rapide
cat > test_mcp.py << 'EOF'
import httpx
from base64 import b64encode

credentials = b64encode(b"julien:DevAccess2025").decode()
headers = {"Authorization": f"Basic {credentials}"}

response = httpx.get(
    "https://mcp.srv759970.hstgr.cloud/python/health",
    headers=headers
)
print(response.json())
EOF

# Exécuter avec uvx
uvx --with httpx python test_mcp.py
```

---

## 🔄 Commandes utiles

### Gestion des services

```bash
# Status
systemctl status mcp-nodejs
systemctl status mcp-python

# Redémarrer
systemctl restart mcp-nodejs
systemctl restart mcp-python

# Logs en temps réel
journalctl -u mcp-nodejs -f
journalctl -u mcp-python -f

# Derniers logs
journalctl -u mcp-nodejs -n 50
journalctl -u mcp-python -n 50
```

### Mise à jour des dépendances

#### Node.js

```bash
cd /var/www/mcp-servers/nodejs
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
npm update
systemctl restart mcp-nodejs
```

#### Python

```bash
cd /var/www/mcp-servers/python
export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate
uv pip install --upgrade fastapi uvicorn mcp
systemctl restart mcp-python
```

---

## 🔒 Sécurité

- **Basic Auth** : Tous les endpoints protégés
- **HTTPS uniquement** : SSL via Let's Encrypt
- **Firewall** : Ports 3000 et 8000 non exposés directement (proxy Nginx)
- **Services systemd** : Redémarrage automatique en cas de crash

---

## 📊 Monitoring

### Vérifier si les services fonctionnent

```bash
# Node.js
curl -u julien:DevAccess2025 https://mcp.srv759970.hstgr.cloud/nodejs/health

# Python
curl -u julien:DevAccess2025 https://mcp.srv759970.hstgr.cloud/python/health
```

### Logs d'accès Nginx

```bash
tail -f /var/log/nginx/mcp-access.log
```

---

## 📚 Ressources

- **Model Context Protocol** : https://modelcontextprotocol.io/
- **FastAPI Docs** : https://fastapi.tiangolo.com/
- **Express.js Docs** : https://expressjs.com/
- **uv Docs** : https://docs.astral.sh/uv/
- **npx Docs** : https://docs.npmjs.com/cli/v10/commands/npx

---

**Créé le** : 2025-10-16
**URLs** :
- Node.js : https://mcp.srv759970.hstgr.cloud/nodejs/
- Python : https://mcp.srv759970.hstgr.cloud/python/
**Auth** : julien / DevAccess2025
