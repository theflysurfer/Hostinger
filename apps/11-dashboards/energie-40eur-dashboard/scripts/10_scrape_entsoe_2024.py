"""
Script 10: Scraping ENTSO-E 2024 avec Playwright - ON VA JUSQU'AU BOUT!
Extraction COMPLETE de toutes les données 2024 (366 jours)
"""
import sys
import os
from datetime import datetime, timedelta
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR

def generate_date_range_2024():
    """Génère toutes les dates de 2024"""
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

def main():
    """
    SCRAPING COMPLET 2024 - AUCUNE EXCUSE!

    Ce script va être exécuté par Claude avec Playwright MCP
    Il va scraper TOUS les jours de 2024 (366 jours)
    Avec sauvegardes toutes les 50 dates
    """
    print("=" * 80)
    print("SCRAPING ENTSO-E 2024 COMPLET - ON ABANDONNE PAS!")
    print("=" * 80)

    dates = generate_date_range_2024()
    print(f"\nNombre de dates à scraper: {len(dates)} jours")
    print(f"Première date: {dates[0]}")
    print(f"Dernière date: {dates[-1]}")
    print()

    # Créer le fichier de sortie
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    output_file = f"{RAW_DATA_DIR}/entsoe_2024_scraped.jsonl"

    print(f"Fichier de sortie: {output_file}")
    print()
    print("[!] INSTRUCTIONS POUR CLAUDE:")
    print("    1. Ouvrir Playwright")
    print("    2. Pour CHAQUE date dans la liste:")
    print("       - Naviguer vers l'URL avec la date")
    print("       - Attendre 3 secondes (chargement)")
    print("       - Extraire le tableau avec JavaScript")
    print("       - Sauvegarder en JSONL")
    print("       - Pause de 2 secondes entre requêtes")
    print("    3. Sauvegarder tous les 50 jours")
    print()
    print("URL pattern:")
    print("https://newtransparency.entsoe.eu/market/energyPrices?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%22YYYY-MM-DD%22%2C%22tz%22%3A%22CET%22%7D")
    print()
    print("JavaScript extraction:")
    print("""
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 2) {
    const timeRange = cells[0]?.textContent?.trim();
    const price = cells[1]?.textContent?.trim();
    if (timeRange && price && timeRange.includes('/')) {
      data.push({
        timeRange: timeRange,
        price: parseFloat(price)
      });
    }
  }
});
return data;
""")
    print()
    print("=" * 80)
    print("ON Y VA! AUCUNE EXCUSE!")
    print("=" * 80)

    # Sauvegarder la liste des dates
    dates_file = f"{RAW_DATA_DIR}/dates_2024_to_scrape.txt"
    with open(dates_file, 'w') as f:
        for date in dates:
            f.write(f"{date}\n")

    print(f"\n[+] Liste des dates sauvegardée: {dates_file}")
    print(f"[+] Prêt pour le scraping avec Playwright MCP")
    print(f"[+] Estimation: ~20-30 minutes pour 366 jours (2 sec/jour)")

if __name__ == "__main__":
    main()
