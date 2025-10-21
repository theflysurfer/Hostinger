# MemVid RAG V2 - Améliorations

## Corrections Apportées

### 1. Support OpenAI API ✅
- Modèle "openai" pour chat RAG
- Support GPT-3.5, GPT-4
- Support endpoints Azure

### 2. Timeout Nginx ✅  
- 300s → 600s (10 min)

### 3. Métriques Prometheus ✅
- prometheus-client==0.21.0
- Endpoint /metrics
- 15+ métriques disponibles

### 4. Indexation Incrémentale ⚠️
- Tracking compteur chunks amélioré
- Limitation MemVid v0.1.3 : pas de support natif

## Intégration Monitoring

### Prometheus Config
scrape_configs:
  - job_name: memvid-rag
    static_configs:
      - targets: [localhost:8506]
    scrape_interval: 15s
    metrics_path: /metrics

### RQ Integration  
- Redis pour queues
- Workers pour jobs asynchrones
- Dashboard RQ existant compatible

## Déploiement
./deploy-v2.sh
