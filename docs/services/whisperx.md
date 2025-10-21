# WhisperX - Transcription avec Diarization

Service de transcription audio avec diarization (identification des locuteurs).

## Accès

- **URL API**: https://whisperx.srv759970.hstgr.cloud
- **Documentation**: https://whisperx.srv759970.hstgr.cloud/docs
- **Port interne**: 8002

## Caractéristiques

- Modèle: `large-v2`
- Diarization: ✅ (qui parle quand)
- Alignment: ✅ (timestamps précis)
- Device: CUDA (GPU)
- Queue: Redis DB 0 ("transcription")

## Endpoints Principaux

### POST /transcribe
Upload audio file for transcription with diarization.

### GET /job/{job_id}
Check job status and retrieve results.

See [API Documentation](https://whisperx.srv759970.hstgr.cloud/docs) for complete reference.

## Guides Complets

- [Guide Whisper Services](../guides/GUIDE_WHISPER_SERVICES.md) - Déploiement et configuration des deux services
- [Faster-Whisper Queue](faster-whisper-queue.md) - Alternative async avec queue RQ
- [Monitoring WhisperX](../guides/GUIDE_MONITORING_WHISPERX.md) - Stack Grafana + Prometheus + Loki

## Voir Aussi

- [Docker](../infrastructure/docker.md) - Gestion des conteneurs
- [Nginx](../infrastructure/nginx.md) - Reverse proxy configuration
