#!/usr/bin/env python3
"""
Analyse résultats benchmark Whisper

Compare faster-whisper vs WhisperX sur:
- Temps de traitement
- Nombre de tokens
- Efficacité par taille de fichier
"""
import json
import pandas as pd
from pathlib import Path
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_FILE = Path(__file__).parent / "results" / "benchmark_results.json"

# ============================================================================
# CHARGEMENT RÉSULTATS
# ============================================================================

def load_results() -> pd.DataFrame:
    """Charge résultats JSON en DataFrame pandas"""

    if not RESULTS_FILE.exists():
        print(f"❌ Fichier résultats introuvable: {RESULTS_FILE}")
        print("💡 Lancez d'abord: python benchmark.py")
        sys.exit(1)

    with open(RESULTS_FILE, encoding="utf-8") as f:
        results = json.load(f)

    if not results:
        print("❌ Aucun résultat dans le fichier JSON")
        sys.exit(1)

    df = pd.DataFrame(results)

    # Filtrer erreurs
    errors = df[df["error"].notna()] if "error" in df.columns else pd.DataFrame()

    if not errors.empty:
        print(f"⚠️  {len(errors)} erreurs détectées:")
        for _, row in errors.iterrows():
            print(f"   - {row['audio_file']} ({row['service']}): {row.get('error', 'Unknown')[:100]}")
        print()

    # Garder seulement résultats valides
    df_valid = df[df["error"].isna()] if "error" in df.columns else df

    return df_valid

# ============================================================================
# CATÉGORISATION
# ============================================================================

def categorize_files(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute catégories de taille fichier"""

    df = df.copy()

    df["size_category"] = pd.cut(
        df["audio_size_mb"],
        bins=[0, 2, 10, 200],
        labels=["Court (<2MB)", "Moyen (2-10MB)", "Long (>10MB)"]
    )

    return df

# ============================================================================
# ANALYSES
# ============================================================================

def print_header(title: str):
    """Affiche un header stylisé"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def analyze_processing_time(df: pd.DataFrame):
    """Analyse temps de traitement"""

    print_header("⏱️  TEMPS DE TRAITEMENT")

    # Par service
    time_stats = df.groupby("service")["duration_seconds"].agg([
        ("Moyenne", "mean"),
        ("Min", "min"),
        ("Max", "max"),
        ("Std Dev", "std")
    ]).round(2)

    print("📊 Statistiques par service:\n")
    print(time_stats)

    # Calcul speedup
    if "faster-whisper" in df["service"].values and "whisperx" in df["service"].values:
        fw_mean = df[df["service"] == "faster-whisper"]["duration_seconds"].mean()
        wx_mean = df[df["service"] == "whisperx"]["duration_seconds"].mean()

        speedup = ((wx_mean - fw_mean) / fw_mean) * 100

        print(f"\n💡 WhisperX est {abs(speedup):.1f}% {'plus lent' if speedup > 0 else 'plus rapide'} que faster-whisper")

def analyze_tokens(df: pd.DataFrame):
    """Analyse nombre de tokens"""

    print_header("🔢 NOMBRE DE TOKENS")

    token_stats = df.groupby("service")["tokens"].agg([
        ("Moyenne", "mean"),
        ("Min", "min"),
        ("Max", "max"),
        ("Total", "sum")
    ]).round(0).astype(int)

    print("📊 Statistiques par service:\n")
    print(token_stats)

    # Tokens par MB
    df_temp = df.copy()
    df_temp["tokens_per_mb"] = df_temp["tokens"] / df_temp["audio_size_mb"]

    tokens_per_mb = df_temp.groupby("service")["tokens_per_mb"].mean().round(0).astype(int)

    print("\n📏 Tokens par MB d'audio:\n")
    print(tokens_per_mb)

def analyze_by_file_size(df: pd.DataFrame):
    """Analyse par taille de fichier"""

    print_header("📏 PERFORMANCE PAR TAILLE DE FICHIER")

    # Temps moyen par catégorie
    time_by_size = df.pivot_table(
        values="duration_seconds",
        index="size_category",
        columns="service",
        aggfunc="mean"
    ).round(2)

    print("⏱️  Temps moyen (secondes) par catégorie:\n")
    print(time_by_size)

    # Tokens par catégorie
    tokens_by_size = df.pivot_table(
        values="tokens",
        index="size_category",
        columns="service",
        aggfunc="mean"
    ).round(0).astype(int)

    print("\n🔢 Tokens moyens par catégorie:\n")
    print(tokens_by_size)

def analyze_diarization(df: pd.DataFrame):
    """Analyse impact diarization (WhisperX uniquement)"""

    print_header("🎤 IMPACT DIARIZATION (WhisperX)")

    df_wx = df[df["service"] == "whisperx"].copy()

    if df_wx.empty or "diarization" not in df_wx.columns:
        print("⚠️  Pas de données WhisperX disponibles")
        return

    # Comparer avec/sans diarization
    diar_stats = df_wx.groupby("diarization").agg({
        "duration_seconds": ["mean", "count"],
        "num_speakers": "mean"
    }).round(2)

    print("📊 Statistiques diarization:\n")
    print(diar_stats)

    # Overhead diarization
    if True in df_wx["diarization"].values and False in df_wx["diarization"].values:
        time_with = df_wx[df_wx["diarization"] == True]["duration_seconds"].mean()
        time_without = df_wx[df_wx["diarization"] == False]["duration_seconds"].mean()

        overhead = ((time_with - time_without) / time_without) * 100

        print(f"\n💡 Overhead diarization: +{overhead:.1f}% de temps de traitement")

    # Speakers détectés
    if "num_speakers" in df_wx.columns:
        avg_speakers = df_wx[df_wx["diarization"] == True]["num_speakers"].mean()
        if pd.notna(avg_speakers):
            print(f"👥 Moyenne speakers détectés: {avg_speakers:.1f}")

def analyze_efficiency(df: pd.DataFrame):
    """Analyse efficacité (secondes de traitement par MB)"""

    print_header("⚡ EFFICACITÉ (Temps / Taille)")

    df_temp = df.copy()
    df_temp["seconds_per_mb"] = df_temp["duration_seconds"] / df_temp["audio_size_mb"]

    efficiency = df_temp.groupby("service")["seconds_per_mb"].agg([
        ("Moyenne", "mean"),
        ("Min", "min"),
        ("Max", "max")
    ]).round(2)

    print("📊 Secondes de traitement par MB d'audio:\n")
    print(efficiency)

    best_service = efficiency["Moyenne"].idxmin()
    print(f"\n💡 Service le plus efficace: {best_service}")

# ============================================================================
# RECOMMANDATIONS
# ============================================================================

def generate_recommendations(df: pd.DataFrame):
    """Génère recommandations basées sur résultats"""

    print_header("💡 RECOMMANDATIONS")

    # Service le plus rapide
    fastest = df.groupby("service")["duration_seconds"].mean().idxmin()
    print(f"🏆 Service le plus rapide: {fastest}")

    # Service avec le plus de tokens (plus verbeux)
    most_tokens = df.groupby("service")["tokens"].mean().idxmax()
    print(f"📝 Service le plus verbeux: {most_tokens}")

    # Meilleure efficacité
    df_temp = df.copy()
    df_temp["seconds_per_mb"] = df_temp["duration_seconds"] / df_temp["audio_size_mb"]
    most_efficient = df_temp.groupby("service")["seconds_per_mb"].mean().idxmin()
    print(f"⚡ Service le plus efficace: {most_efficient}")

    print("\n📋 Cas d'usage recommandés:\n")
    print("   faster-whisper:")
    print("   ✅ Transcription simple sans speakers")
    print("   ✅ Performance maximale requise")
    print("   ✅ API compatible OpenAI\n")

    print("   WhisperX:")
    print("   ✅ Identification speakers (meetings, interviews)")
    print("   ✅ Timestamps précis (±50ms)")
    print("   ✅ Audio multi-locuteurs")

# ============================================================================
# EXPORT
# ============================================================================

def export_csv(df: pd.DataFrame):
    """Exporte résultats en CSV"""

    output_file = Path(__file__).parent / "results" / "benchmark_analysis.csv"

    # Supprimer colonne texte (trop longue)
    df_export = df.drop(columns=["text"], errors="ignore")

    df_export.to_csv(output_file, index=False, encoding="utf-8")

    print(f"\n💾 Analyse exportée: {output_file}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Fonction principale"""

    print("=" * 80)
    print("  📊 ANALYSE BENCHMARK WHISPER")
    print("=" * 80)

    # Charger résultats
    df = load_results()

    print(f"\n✅ {len(df)} résultats chargés")

    # Catégoriser
    df = categorize_files(df)

    # Analyses
    analyze_processing_time(df)
    analyze_tokens(df)
    analyze_by_file_size(df)
    analyze_diarization(df)
    analyze_efficiency(df)

    # Recommandations
    generate_recommendations(df)

    # Export
    export_csv(df)

    print("\n" + "=" * 80)
    print("  ✅ ANALYSE TERMINÉE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
