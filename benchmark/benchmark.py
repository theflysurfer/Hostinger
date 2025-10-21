#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark faster-whisper vs WhisperX

Mesure temps de traitement, tokens, et qualité de transcription.
"""
import sys
import io
import requests
import time
import json
import tiktoken
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Fix encoding pour Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION
# ============================================================================

FASTER_WHISPER_URL = "https://whisper.srv759970.hstgr.cloud/v1/audio/transcriptions"
WHISPERX_URL = "https://whisperx.srv759970.hstgr.cloud/transcribe"
WHISPERX_STATUS_URL = "https://whisperx.srv759970.hstgr.cloud/status"

# Basic auth Nginx credentials
AUTH = ("julien", "DevAccess2025")

MODELS = {
    "faster-whisper": "Systran/faster-whisper-small",
    "whisperx": "base"
}

# Fichiers audio à tester (auto-détectés dans audio_samples/)
AUDIO_SAMPLES_DIR = Path(__file__).parent / "audio_samples"

# Auto-start retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 10  # secondes entre chaque retry
AUTO_START_WAIT = 30  # temps d'attente initial si 503

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def count_tokens(text: str) -> int:
    """Compte le nombre de tokens GPT-4 (cl100k_base)"""
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception as e:
        print(f"    ⚠️  Erreur tiktoken: {e}")
        return 0

def format_duration(seconds: float) -> str:
    """Formate durée en MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def make_request_with_retry(url: str, files: dict, data: dict, service_name: str) -> requests.Response:
    """
    Effectue une requête HTTP avec retry logic pour gérer l'auto-start

    Args:
        url: URL de l'API
        files: Fichiers à envoyer
        data: Données du formulaire
        service_name: Nom du service pour les logs

    Returns:
        Response object ou raise Exception
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                auth=AUTH,
                timeout=600,
                verify=False  # Désactiver vérification SSL pour certificats auto-signés
            )

            # 503 = Service starting (auto-start)
            if response.status_code == 503:
                if attempt == 1:
                    print(f"⏳ Service démarrage (auto-start), attente {AUTO_START_WAIT}s...", end=" ", flush=True)
                    time.sleep(AUTO_START_WAIT)
                else:
                    print(f"⏳ Retry {attempt}/{MAX_RETRIES}, attente {RETRY_DELAY}s...", end=" ", flush=True)
                    time.sleep(RETRY_DELAY)
                continue

            # Autre erreur
            if response.status_code != 200:
                if attempt < MAX_RETRIES:
                    print(f"⚠️  {response.status_code}, retry {attempt}/{MAX_RETRIES}...", end=" ", flush=True)
                    time.sleep(RETRY_DELAY)
                    continue

            return response

        except requests.exceptions.SSLError as e:
            # Erreur SSL, désactiver la vérification
            print(f"⚠️  SSL error, retry sans vérification...", end=" ", flush=True)
            continue

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"⚠️  {str(e)[:50]}, retry {attempt}/{MAX_RETRIES}...", end=" ", flush=True)
                time.sleep(RETRY_DELAY)
                continue
            else:
                raise

    # Si tous les retries échouent
    raise Exception(f"Max retries ({MAX_RETRIES}) atteint pour {service_name}")

# ============================================================================
# BENCHMARK FASTER-WHISPER
# ============================================================================

def benchmark_faster_whisper(audio_path: Path) -> Dict:
    """
    Benchmark faster-whisper (OpenAI API compatible)

    Returns:
        Dict avec métriques: duration, tokens, text, etc.
    """
    print(f"  [faster-whisper] {audio_path.name}...", end=" ", flush=True)

    start = time.time()

    try:
        with open(audio_path, "rb") as f:
            files = {"file": f}
            data = {
                "model": MODELS["faster-whisper"],
                "language": "fr"
            }

            response = make_request_with_retry(
                FASTER_WHISPER_URL,
                files,
                data,
                "faster-whisper"
            )

        duration = time.time() - start

        if response.status_code != 200:
            print(f"❌ {response.status_code}")
            return {
                "error": response.text,
                "duration_seconds": duration,
                "service": "faster-whisper",
                "audio_file": audio_path.name
            }

        result = response.json()
        text = result.get("text", "")

        tokens = count_tokens(text)
        words = len(text.split())

        print(f"✅ {format_duration(duration)} | {tokens} tokens | {words} mots")

        return {
            "service": "faster-whisper",
            "audio_file": audio_path.name,
            "audio_size_mb": round(audio_path.stat().st_size / 1024 / 1024, 2),
            "duration_seconds": round(duration, 2),
            "text": text,
            "tokens": tokens,
            "words": words,
            "chars": len(text),
            "model": MODELS["faster-whisper"],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        duration = time.time() - start
        print(f"❌ Exception: {e}")
        return {
            "error": str(e),
            "duration_seconds": duration,
            "service": "faster-whisper",
            "audio_file": audio_path.name
        }

# ============================================================================
# BENCHMARK WHISPERX (ASYNC avec Queue)
# ============================================================================

def benchmark_whisperx_async(audio_path: Path, diarize: bool = False, poll_interval: int = 5) -> Dict:
    """
    Benchmark WhisperX en mode ASYNCHRONE avec queue RQ

    Args:
        audio_path: Chemin fichier audio
        diarize: Activer diarization (identification speakers)
        poll_interval: Intervalle de polling en secondes (défaut: 5s)

    Returns:
        Dict avec métriques + speakers si diarization
    """
    service_name = f"WhisperX{'(diar)' if diarize else ''}"
    print(f"  [{service_name}] {audio_path.name}...", end=" ", flush=True)

    start = time.time()

    try:
        # 1. SOUMETTRE LE JOB (Upload)
        with open(audio_path, "rb") as f:
            files = {"file": f}
            data = {
                "model": MODELS["whisperx"],
                "language": "fr",
                "diarize": str(diarize).lower()
            }

            submit_response = requests.post(
                WHISPERX_URL,
                files=files,
                data=data,
                auth=AUTH,
                timeout=30,  # Upload timeout court
                verify=False
            )

        if submit_response.status_code != 200:
            print(f"❌ Submit failed: {submit_response.status_code}")
            return {
                "error": f"Submit failed: {submit_response.text}",
                "duration_seconds": time.time() - start,
                "service": "whisperx",
                "audio_file": audio_path.name,
                "diarization": diarize
            }

        submit_data = submit_response.json()
        job_id = submit_data.get("job_id")

        if not job_id:
            print(f"❌ No job_id returned")
            return {
                "error": "No job_id in response",
                "duration_seconds": time.time() - start,
                "service": "whisperx",
                "audio_file": audio_path.name,
                "diarization": diarize
            }

        print(f"📤 Job {job_id[:8]}...", end=" ", flush=True)

        # 2. POLLING DU STATUT
        last_progress = -1
        max_wait_time = 7200  # 2 heures max
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(poll_interval)
            elapsed = time.time() - start

            try:
                status_response = requests.get(
                    f"{WHISPERX_STATUS_URL}/{job_id}",
                    auth=AUTH,
                    timeout=10,
                    verify=False
                )

                if status_response.status_code != 200:
                    continue

                status_data = status_response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)

                # Afficher progression si changement
                if progress != last_progress and progress % 20 == 0:
                    print(f"{progress}%...", end=" ", flush=True)
                    last_progress = progress

                # JOB TERMINÉ
                if status == "completed":
                    duration = time.time() - start
                    result = status_data.get("result", {})

                    # Reconstruire texte complet
                    if "segments" in result:
                        text = " ".join([seg.get("text", "") for seg in result["segments"]])
                        speakers = list(set([seg.get("speaker", "N/A") for seg in result["segments"]]))
                    else:
                        text = result.get("text", "")
                        speakers = []

                    tokens = count_tokens(text)
                    words = len(text.split())

                    if diarize:
                        print(f"✅ {format_duration(duration)} | {tokens} tokens | {len(speakers)} speakers")
                    else:
                        print(f"✅ {format_duration(duration)} | {tokens} tokens | {words} mots")

                    return {
                        "service": "whisperx",
                        "audio_file": audio_path.name,
                        "audio_size_mb": round(audio_path.stat().st_size / 1024 / 1024, 2),
                        "duration_seconds": round(duration, 2),
                        "text": text,
                        "tokens": tokens,
                        "words": words,
                        "chars": len(text),
                        "model": MODELS["whisperx"],
                        "diarization": diarize,
                        "speakers": speakers if diarize else None,
                        "num_speakers": len(speakers) if diarize else None,
                        "segments": len(result.get("segments", [])) if "segments" in result else None,
                        "job_id": job_id,
                        "timestamp": datetime.now().isoformat()
                    }

                # JOB ÉCHOUÉ
                elif status == "failed":
                    duration = time.time() - start
                    error_msg = status_data.get("error", "Unknown error")
                    print(f"❌ Failed: {error_msg}")
                    return {
                        "error": error_msg,
                        "duration_seconds": duration,
                        "service": "whisperx",
                        "audio_file": audio_path.name,
                        "diarization": diarize,
                        "job_id": job_id
                    }

            except Exception as poll_error:
                # Continuer à poller même en cas d'erreur temporaire
                continue

        # TIMEOUT
        print(f"❌ Timeout après {format_duration(max_wait_time)}")
        return {
            "error": f"Timeout after {max_wait_time}s",
            "duration_seconds": time.time() - start,
            "service": "whisperx",
            "audio_file": audio_path.name,
            "diarization": diarize,
            "job_id": job_id
        }

    except Exception as e:
        duration = time.time() - start
        print(f"❌ Exception: {e}")
        return {
            "error": str(e),
            "duration_seconds": duration,
            "service": "whisperx",
            "audio_file": audio_path.name,
            "diarization": diarize
        }

# ============================================================================
# BENCHMARK PRINCIPAL
# ============================================================================

def run_benchmark():
    """Lance le benchmark complet sur tous les fichiers audio"""

    # Découvrir fichiers audio
    audio_files = sorted(AUDIO_SAMPLES_DIR.glob("*.m4a"))

    if not audio_files:
        print("❌ Aucun fichier audio trouvé dans audio_samples/")
        return []

    print("=" * 80)
    print(f"🚀 BENCHMARK WHISPER SERVICES")
    print("=" * 80)
    print(f"\n📁 Fichiers à traiter: {len(audio_files)}")
    print(f"🔧 Services: faster-whisper, WhisperX (avec/sans diarization)\n")

    results = []
    total_start = time.time()

    for i, audio_path in enumerate(audio_files, 1):
        size_mb = audio_path.stat().st_size / 1024 / 1024

        print(f"\n[{i}/{len(audio_files)}] 📄 {audio_path.name} ({size_mb:.1f} MB)")
        print("-" * 80)

        # 1. faster-whisper
        try:
            result_fw = benchmark_faster_whisper(audio_path)
            results.append(result_fw)
        except Exception as e:
            print(f"  [faster-whisper] ❌ Erreur critique: {e}")

        # 2. WhisperX sans diarization (ASYNC)
        try:
            result_wx = benchmark_whisperx_async(audio_path, diarize=False)
            results.append(result_wx)
        except Exception as e:
            print(f"  [WhisperX] ❌ Erreur critique: {e}")

        # 3. WhisperX avec diarization (seulement si > 5MB) (ASYNC)
        if size_mb > 5:
            try:
                result_wx_diar = benchmark_whisperx_async(audio_path, diarize=True)
                results.append(result_wx_diar)
            except Exception as e:
                print(f"  [WhisperX(diar)] ❌ Erreur critique: {e}")

    total_duration = time.time() - total_start

    # Sauvegarder résultats
    output_file = Path(__file__).parent / "results" / "benchmark_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"✅ BENCHMARK TERMINÉ")
    print("=" * 80)
    print(f"📊 Résultats: {len(results)} transcriptions effectuées")
    print(f"⏱️  Durée totale: {format_duration(total_duration)} ({total_duration:.1f}s)")
    print(f"💾 Sauvegardé: {output_file}")
    print("\n💡 Prochaine étape: python analyze.py\n")

    return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = run_benchmark()
