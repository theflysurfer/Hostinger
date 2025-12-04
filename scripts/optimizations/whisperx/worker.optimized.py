#!/usr/bin/env python3
"""
WhisperX Background Worker avec RQ - OPTIMISÉ
Version optimisée: large-v3 français uniquement + custom vocabulary
"""
import os
import json
import whisperx
import redis
from rq import Worker, Queue
from pathlib import Path
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================================================================
# CONFIGURATION OPTIMISÉE
# ===================================================================
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
DEVICE = 'cpu'
COMPUTE_TYPE = 'int8'
HF_TOKEN = os.getenv('HF_TOKEN', None)

# MODÈLE OPTIMISÉ: large-v3 français uniquement
DEFAULT_MODEL = "large-v3"
DEFAULT_LANGUAGE = "fr"

# Custom vocabulary - Mots techniques/spécifiques
CUSTOM_VOCABULARY_FILE = Path("/app/custom_vocabulary.txt")

def load_custom_vocabulary():
    """
    Charge le vocabulaire personnalisé depuis le fichier
    Returns: str - Prompt avec les mots personnalisés
    """
    if not CUSTOM_VOCABULARY_FILE.exists():
        logger.warning("Custom vocabulary file not found, using default")
        return None

    try:
        with open(CUSTOM_VOCABULARY_FILE, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if words:
            # Créer un prompt pour guider Whisper
            prompt = f"Vocabulaire technique: {', '.join(words[:50])}"  # Limiter à 50 mots
            logger.info(f"Loaded {len(words)} custom words for vocabulary guidance")
            return prompt
        else:
            logger.warning("Custom vocabulary file is empty")
            return None
    except Exception as e:
        logger.error(f"Error loading custom vocabulary: {e}")
        return None

# Charger le vocabulaire au démarrage
CUSTOM_PROMPT = load_custom_vocabulary()

# Connecter à Redis
redis_conn = redis.from_url(REDIS_URL)

# ===================================================================
# CACHE DU MODÈLE (Chargé une seule fois au démarrage)
# ===================================================================
MODEL_CACHE = {}

def get_model(model_name=DEFAULT_MODEL):
    """
    Récupère le modèle depuis le cache ou le charge
    """
    if model_name not in MODEL_CACHE:
        logger.info(f"Loading model '{model_name}' into cache...")
        MODEL_CACHE[model_name] = whisperx.load_model(
            model_name,
            DEVICE,
            compute_type=COMPUTE_TYPE
        )
        logger.info(f"✅ Model '{model_name}' loaded and cached")
    return MODEL_CACHE[model_name]


def process_transcription(
    job_id: str,
    audio_path: str,
    model_name: str = DEFAULT_MODEL,  # Forcer large-v3
    language: str = DEFAULT_LANGUAGE,  # Forcer français
    diarize: bool = False
):
    """
    Fonction qui traite la transcription en arrière-plan
    VERSION OPTIMISÉE: large-v3 + français + custom vocabulary

    Args:
        job_id: ID unique du job
        audio_path: Chemin vers le fichier audio
        model_name: Modèle Whisper (forcé à large-v3)
        language: Langue de transcription (forcé à fr)
        diarize: Activer la diarization
    """
    # FORCER LE MODÈLE ET LA LANGUE
    model_name = DEFAULT_MODEL
    language = DEFAULT_LANGUAGE

    logger.info(f"[Job {job_id}] Démarrage transcription optimisée")
    logger.info(f"[Job {job_id}] Modèle: {model_name}, Langue: {language}")

    try:
        # Vérifier que le fichier existe
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Mettre à jour le statut: processing
        redis_conn.hset(f"job:{job_id}", mapping={
            "status": "processing",
            "progress": "0",
            "step": "Loading model (large-v3)"
        })

        # 1. Charger le modèle DEPUIS LE CACHE
        logger.info(f"[Job {job_id}] Loading cached model: {model_name}")
        model_whisper = get_model(model_name)

        redis_conn.hset(f"job:{job_id}", "progress", "20")
        redis_conn.hset(f"job:{job_id}", "step", "Loading audio")

        # 2. Charger l'audio
        logger.info(f"[Job {job_id}] Loading audio")
        audio = whisperx.load_audio(audio_path)

        redis_conn.hset(f"job:{job_id}", "progress", "30")
        redis_conn.hset(f"job:{job_id}", "step", "Transcribing with custom vocabulary")

        # 3. Transcrire AVEC CUSTOM VOCABULARY
        logger.info(f"[Job {job_id}] Transcribing with large-v3 + custom vocab")

        transcribe_options = {
            "language": language,
            "task": "transcribe"
        }

        # Ajouter le custom prompt si disponible
        if CUSTOM_PROMPT:
            transcribe_options["initial_prompt"] = CUSTOM_PROMPT
            logger.info(f"[Job {job_id}] Using custom vocabulary prompt")

        result = model_whisper.transcribe(audio, **transcribe_options)

        redis_conn.hset(f"job:{job_id}", "progress", "60")
        redis_conn.hset(f"job:{job_id}", "step", "Aligning timestamps (French)")

        # 4. Aligner les timestamps POUR LE FRANÇAIS
        logger.info(f"[Job {job_id}] Aligning timestamps for French")
        model_a, metadata = whisperx.load_align_model(
            language_code=language,  # Forcé à 'fr'
            device=DEVICE
        )
        result = whisperx.align(
            result['segments'],
            model_a,
            metadata,
            audio,
            DEVICE,
            return_char_alignments=False
        )

        redis_conn.hset(f"job:{job_id}", "progress", "80")

        # 5. Diarization (optionnel)
        if diarize and HF_TOKEN:
            redis_conn.hset(f"job:{job_id}", "step", "Speaker diarization")
            logger.info(f"[Job {job_id}] Speaker diarization")

            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=HF_TOKEN,
                device=DEVICE
            )
            diarize_segments = diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)

            redis_conn.hset(f"job:{job_id}", "progress", "95")

        # 6. Sauvegarder le résultat
        logger.info(f"[Job {job_id}] Saving result")
        result_json = json.dumps(result, ensure_ascii=False)

        redis_conn.hset(f"job:{job_id}", mapping={
            "status": "completed",
            "progress": "100",
            "step": "Done",
            "result": result_json,
            "model_used": model_name,
            "language_used": language,
            "custom_vocab": "yes" if CUSTOM_PROMPT else "no"
        })

        # Nettoyer le fichier audio temporaire
        try:
            os.remove(audio_path)
            logger.info(f"[Job {job_id}] Cleaned up temporary file: {audio_path}")
        except Exception as e:
            logger.warning(f"[Job {job_id}] Could not delete temp file: {e}")

        logger.info(f"[Job {job_id}] ✅ Transcription completed successfully (large-v3 French)")
        return result

    except Exception as e:
        logger.error(f"[Job {job_id}] ❌ Error: {str(e)}", exc_info=True)

        # Sauvegarder l'erreur
        redis_conn.hset(f"job:{job_id}", mapping={
            "status": "failed",
            "error": str(e),
            "step": "Error"
        })

        # Nettoyer le fichier même en cas d'erreur
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass

        raise


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Starting WhisperX RQ Worker - OPTIMIZED VERSION")
    logger.info("=" * 60)
    logger.info(f"Redis URL: {REDIS_URL}")
    logger.info(f"Device: {DEVICE}")
    logger.info(f"Model: {DEFAULT_MODEL} (French optimized)")
    logger.info(f"Language: {DEFAULT_LANGUAGE} (forced)")
    logger.info(f"Custom Vocabulary: {'Yes' if CUSTOM_PROMPT else 'No'}")
    logger.info(f"HF Token configured: {'Yes' if HF_TOKEN else 'No'}")
    logger.info("=" * 60)

    # PRÉ-CHARGER LE MODÈLE large-v3 AU DÉMARRAGE
    logger.info("⏳ Pre-loading model large-v3 into cache...")
    try:
        get_model(DEFAULT_MODEL)
        logger.info("✅ Model pre-loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to pre-load model: {e}")
        logger.error("Worker will continue but first transcription will be slower")

    logger.info("=" * 60)

    # Créer le worker
    worker = Worker(['transcription'], connection=redis_conn)
    logger.info("✅ Worker ready, waiting for jobs...")
    worker.work()
