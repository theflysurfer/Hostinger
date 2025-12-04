"""
Script 9: Capture des requêtes API ENTSO-E via Playwright
Objectif: Intercepter et enregistrer les vraies requêtes HTTP pour comprendre le format exact
"""
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR

def main():
    """
    Instructions pour capturer les requêtes API avec Playwright
    """
    print("=" * 80)
    print("CAPTURE DES REQUETES API ENTSO-E")
    print("=" * 80)
    print()
    print("[i] Ce script doit être exécuté avec Playwright MCP par Claude")
    print("[i] Il va intercepter les requêtes HTTP pour comprendre le format")
    print()
    print("=" * 80)
    print("INSTRUCTIONS:")
    print("=" * 80)
    print()
    print("1. Ouvrir le navigateur Playwright avec network monitoring activé")
    print("2. Naviguer vers: https://newtransparency.entsoe.eu/market/energyPrices")
    print("3. Accepter les cookies")
    print("4. Sélectionner France (BZN|FR)")
    print("5. Sélectionner une date (ex: 2022-01-01)")
    print("6. Passer en vue Table")
    print("7. Capturer toutes les requêtes POST vers /market/energyPrices/load")
    print()
    print("Pour chaque requête capturée, enregistrer:")
    print("   - URL complète")
    print("   - Headers (surtout Authorization, Cookie, Content-Type)")
    print("   - Payload JSON")
    print("   - Response JSON")
    print()
    print(f"Sauvegarder dans: {RAW_DATA_DIR}/api_capture.json")
    print()
    print("=" * 80)

    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    capture_file = f"{RAW_DATA_DIR}/api_capture.json"
    print(f"\n[i] Fichier de capture: {capture_file}")
    print("[i] Prêt pour l'exécution avec Playwright MCP")

if __name__ == "__main__":
    main()
