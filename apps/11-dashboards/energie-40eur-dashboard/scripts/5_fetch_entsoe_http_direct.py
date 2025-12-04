"""
Script 5: Extraction données ENTSO-E via requêtes HTTP directes (sans token)
Récupère: Flux physiques transfrontaliers France
Période: 2022-2024
Méthode: Requêtes HTTP directes vers l'API REST publique
"""
import requests
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
import time
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import START_DATE, END_DATE, RAW_DATA_DIR, REQUEST_TIMEOUT

# API REST ENTSO-E (certaines données sont publiques)
ENTSOE_API_URL = "https://web-api.tp.entsoe.eu/api"

# Code EIC pour la France
FRANCE_EIC = "10YFR-RTE------C"

# Codes des pays frontaliers
BORDER_COUNTRIES = {
    "BE": "10YBE----------2",  # Belgique
    "DE": "10Y1001A1001A83F",  # Allemagne
    "CH": "10YCH-SWISSGRIDZ",  # Suisse
    "IT": "10YIT-GRTN-----B",  # Italie
    "ES": "10YES-REE------0",  # Espagne
    "GB": "10YGB----------A",  # UK
}

def parse_physical_flows_xml(xml_content):
    """
    Parse le XML retourné par ENTSO-E pour les flux physiques

    Args:
        xml_content: Contenu XML brut

    Returns:
        Liste de dictionnaires avec les données
    """
    try:
        root = ET.fromstring(xml_content)

        # Namespace ENTSO-E
        ns = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}

        records = []

        # Parser chaque TimeSeries
        for ts in root.findall('.//ns:TimeSeries', ns):
            # Zone in/out
            in_domain = ts.find('.//ns:in_Domain.mRID', ns)
            out_domain = ts.find('.//ns:out_Domain.mRID', ns)

            if in_domain is not None and out_domain is not None:
                in_code = in_domain.text
                out_code = out_domain.text

                # Parser chaque Period
                for period in ts.findall('.//ns:Period', ns):
                    start_time = period.find('.//ns:timeInterval/ns:start', ns)

                    if start_time is not None:
                        start = datetime.strptime(start_time.text, "%Y-%m-%dT%H:%MZ")

                        # Parser chaque Point
                        for point in period.findall('.//ns:Point', ns):
                            position = point.find('.//ns:position', ns)
                            quantity = point.find('.//ns:quantity', ns)

                            if position is not None and quantity is not None:
                                # Position 1 = première heure
                                hour_offset = int(position.text) - 1
                                timestamp = start + timedelta(hours=hour_offset)

                                record = {
                                    'datetime': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                    'from': out_code,
                                    'to': in_code,
                                    'flow_mw': float(quantity.text)
                                }
                                records.append(record)

        return records

    except Exception as e:
        print(f"[!] Erreur parsing XML: {e}")
        return []

def fetch_physical_flows_no_token(from_country, to_country, start_date, end_date):
    """
    Tente de récupérer les flux physiques sans token
    (certaines données ENTSO-E sont publiques)

    Args:
        from_country: Code EIC pays d'origine
        to_country: Code EIC pays de destination
        start_date: Date de début (YYYYMMDD)
        end_date: Date de fin (YYYYMMDD)

    Returns:
        DataFrame avec les flux
    """
    params = {
        'documentType': 'A11',  # Cross-border physical flow
        'in_Domain': to_country,
        'out_Domain': from_country,
        'periodStart': f"{start_date}0000",
        'periodEnd': f"{end_date}2300"
    }

    try:
        response = requests.get(
            ENTSOE_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            # Parser le XML
            records = parse_physical_flows_xml(response.content)
            return pd.DataFrame(records)

        elif response.status_code == 401:
            print(f"[!] 401 Unauthorized - Token requis pour cette donnee")
            return pd.DataFrame()

        else:
            print(f"[!] Erreur HTTP {response.status_code}")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"[!] Erreur requete: {e}")
        return pd.DataFrame()

def fetch_all_french_borders():
    """
    Récupère les flux pour toutes les frontières françaises

    Returns:
        DataFrame combiné avec tous les flux
    """
    print("\n[>>] Tentative de telechargement sans token ENTSO-E...")
    print("[i] Certaines donnees peuvent necessiter un token API\n")

    start_year = int(START_DATE.split("-")[0])
    end_year = int(END_DATE.split("-")[0])

    all_data = []

    for country_code, country_eic in BORDER_COUNTRIES.items():
        print(f"\n[>>] France <-> {country_code}")

        # Télécharger année par année pour éviter les timeouts
        for year in range(start_year, end_year + 1):
            start_date = f"{year}0101"
            end_date = f"{year}1231"

            print(f"   [>>] Annee {year}...", end=" ")

            # FR -> Pays
            df_export = fetch_physical_flows_no_token(
                FRANCE_EIC, country_eic, start_date, end_date
            )

            if not df_export.empty:
                df_export['direction'] = f'FR->{country_code}'
                all_data.append(df_export)
                print(f"[+] Export: {len(df_export)} lignes", end=" ")
            else:
                print("[!] Export: 0", end=" ")

            time.sleep(1)  # Pause entre requêtes

            # Pays -> FR
            df_import = fetch_physical_flows_no_token(
                country_eic, FRANCE_EIC, start_date, end_date
            )

            if not df_import.empty:
                df_import['direction'] = f'{country_code}->FR'
                all_data.append(df_import)
                print(f"/ Import: {len(df_import)} lignes")
            else:
                print("/ Import: 0")

            time.sleep(1)  # Pause entre requêtes

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("EXTRACTION ENTSO-E via HTTP DIRECT (sans token)")
    print("=" * 80)
    print(f"Periode: {START_DATE} a {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()
    print("[i] ATTENTION: La plupart des donnees ENTSO-E necessitent un token API")
    print("[i] Ce script tente d'acceder aux donnees publiques uniquement")
    print()

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    try:
        # Télécharger les flux physiques
        df_flows = fetch_all_french_borders()

        if df_flows.empty:
            print("\n[X] Aucune donnee recuperee")
            print("\n[i] Les donnees ENTSO-E necessitent probablement un token API")
            print("[i] Pour obtenir un token:")
            print("   1. Allez sur https://transparency.entsoe.eu/")
            print("   2. Creez un compte")
            print("   3. Envoyez un email a transparency@entsoe.eu")
            print("   4. Sujet: 'Restful API access'")
            print("   5. Delai: ~3 jours")
            return

        print(f"\n[+] Total recupere: {len(df_flows)} lignes")

        # Sauvegarder
        output_file = f"{RAW_DATA_DIR}/entsoe_physical_flows_http.csv"
        df_flows.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n[>>] Donnees sauvegardees: {output_file}")

        # Aperçu
        print("\n[i] Apercu des donnees:")
        print(f"   Lignes: {len(df_flows)}")
        print(f"   Colonnes: {list(df_flows.columns)}")

        if 'direction' in df_flows.columns:
            print(f"\n   Flux par direction:")
            for direction, count in df_flows['direction'].value_counts().items():
                print(f"      {direction}: {count} lignes")

        print("\n[+] Extraction terminee avec succes!")

    except Exception as e:
        print(f"\n[X] Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
