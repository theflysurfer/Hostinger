# Ollama - Inférence LLM Locale

## Vue d'ensemble

Ollama permet d'exécuter des modèles de langage (LLM) localement sur le serveur.

## Accès

- **API**: https://ollama.srv759970.hstgr.cloud
- **Port**: 11434

## Modèles disponibles

- **Llama 3**: Modèle général performant
- **Mistral**: Modèle français optimisé
- **Qwen**: Modèle multilingue
- **Code Llama**: Spécialisé pour le code

## Endpoints

### POST /api/generate
Génération de texte.

**Exemple:**
```bash
curl https://ollama.srv759970.hstgr.cloud/api/generate   -d '{
    "model": "mistral",
    "prompt": "Explique-moi le machine learning"
  }'
```

### POST /api/chat
Mode conversation.

**Exemple:**
```bash
curl https://ollama.srv759970.hstgr.cloud/api/chat   -d '{
    "model": "llama3",
    "messages": [
      {"role": "user", "content": "Bonjour!"}
    ]
  }'
```

### POST /api/embeddings
Génération d'embeddings pour recherche sémantique.

**Exemple:**
```bash
curl https://ollama.srv759970.hstgr.cloud/api/embeddings   -d '{
    "model": "nomic-embed-text",
    "prompt": "Texte à vectoriser"
  }'
```

## Gestion des modèles

### Lister les modèles
```bash
curl https://ollama.srv759970.hstgr.cloud/api/tags
```

### Télécharger un modèle
```bash
ssh root@srv759970.hstgr.cloud "ollama pull llama3"
```

## Configuration

- **GPU**: Aucun (CPU uniquement)
- **RAM**: 8 GB recommandés
- **Stockage modèles**: /root/.ollama/models

## Performance

| Modèle | Taille | Vitesse (tokens/s) |
|--------|--------|-------------------|
| Llama 3 8B | 4.7 GB | ~15 |
| Mistral 7B | 4.1 GB | ~20 |
| Qwen 7B | 4.4 GB | ~18 |

## Ressources

- [Ollama Documentation](https://ollama.com/)
- [Liste des modèles](https://ollama.com/library)
