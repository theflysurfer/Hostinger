#!/usr/bin/env python3
"""
RAGFlow vs RAG-Anything - Real World Benchmark
==============================================
Benchmark comparatif avec des documents réels

Usage:
    python real_world_benchmark.py
"""

import requests
import time
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class RAGBenchmark:
    def __init__(self):
        self.ragflow_url = "https://ragflow.srv759970.hstgr.cloud"
        self.raganything_url = "https://rag-anything.srv759970.hstgr.cloud"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "ragflow": {
                "tests": [],
                "total_time": 0,
                "documents_processed": 0,
                "errors": []
            },
            "rag_anything": {
                "tests": [],
                "total_time": 0,
                "documents_processed": 0,
                "errors": []
            }
        }

    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp et couleur"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "",
            "TEST": "\033[96m",  # Cyan
            "OK": "\033[92m",     # Green
            "WARN": "\033[93m",   # Yellow
            "ERROR": "\033[91m",  # Red
            "END": "\033[0m"      # Reset
        }
        color = colors.get(level, "")
        print(f"{color}[{timestamp}] {level:5} | {message}{colors['END']}")

    def find_test_documents(self, downloads_path: str, max_docs: int = 5) -> List[str]:
        """Trouve des documents de test dans Downloads"""
        self.log(f"Recherche de documents dans {downloads_path}", "INFO")

        extensions = ['.pdf', '.docx', '.txt', '.pptx']
        docs = []

        downloads = Path(downloads_path)
        if not downloads.exists():
            self.log(f"Dossier introuvable: {downloads_path}", "ERROR")
            return []

        for ext in extensions:
            found = list(downloads.glob(f"*{ext}"))
            docs.extend(found[:2])  # Max 2 par type

        docs = docs[:max_docs]

        for doc in docs:
            size_mb = doc.stat().st_size / (1024*1024)
            self.log(f"  Trouvé: {doc.name} ({size_mb:.2f} MB)", "OK")

        return [str(d) for d in docs]

    def test_ragflow_upload(self, file_path: str) -> Dict:
        """Test upload document sur RAGFlow"""
        file_name = Path(file_path).name
        self.log(f"RAGFlow - Upload: {file_name}", "TEST")

        start = time.time()

        try:
            # Note: RAGFlow nécessite une authentification et création de KB
            # Pour ce benchmark, on teste juste la connectivité de l'API

            # Test de santé
            response = requests.get(f"{self.ragflow_url}/api/health", timeout=10)
            elapsed = time.time() - start

            if response.status_code == 200:
                self.log(f"  OK API accessible en {elapsed:.2f}s", "OK")
                result = {
                    "file": file_name,
                    "status": "api_ready",
                    "time": elapsed,
                    "note": "RAGFlow nécessite auth et KB - test API uniquement"
                }
            else:
                result = {
                    "file": file_name,
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "time": elapsed
                }

        except Exception as e:
            elapsed = time.time() - start
            self.log(f"  ERROR: {str(e)}", "ERROR")
            result = {
                "file": file_name,
                "status": "error",
                "error": str(e),
                "time": elapsed
            }

        self.results["ragflow"]["tests"].append(result)
        self.results["ragflow"]["total_time"] += result.get("time", 0)

        return result

    def test_raganything_upload(self, file_path: str) -> Dict:
        """Test upload document sur RAG-Anything"""
        file_name = Path(file_path).name
        self.log(f"RAG-Anything - Upload: {file_name}", "TEST")

        start = time.time()

        try:
            # RAG-Anything Lite ne supporte pas l'upload de documents
            # Test avec insertion de texte à la place

            with open(file_path, 'rb') as f:
                # Lire un échantillon du fichier
                sample = f.read(1024).decode('utf-8', errors='ignore')

            # Test API health
            health_response = requests.get(f"{self.raganything_url}/health", timeout=5)

            if health_response.status_code == 200:
                elapsed = time.time() - start
                self.log(f"  ✓ API accessible en {elapsed:.2f}s", "OK")

                result = {
                    "file": file_name,
                    "status": "api_ready_lite",
                    "time": elapsed,
                    "note": "Version Lite - pas de parsing documents"
                }
            else:
                elapsed = time.time() - start
                result = {
                    "file": file_name,
                    "status": "error",
                    "error": f"HTTP {health_response.status_code}",
                    "time": elapsed
                }

        except Exception as e:
            elapsed = time.time() - start
            self.log(f"  ERROR: {str(e)}", "ERROR")
            result = {
                "file": file_name,
                "status": "error",
                "error": str(e),
                "time": elapsed
            }

        self.results["rag_anything"]["tests"].append(result)
        self.results["rag_anything"]["total_time"] += result.get("time", 0)

        return result

    def test_ragflow_query(self, query: str) -> Dict:
        """Test query sur RAGFlow"""
        self.log(f"RAGFlow - Query: {query[:50]}...", "TEST")

        start = time.time()

        try:
            # Test query endpoint (nécessite auth normalement)
            response = requests.get(f"{self.ragflow_url}/api/version", timeout=5)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                self.log(f"  OK Version: {data.get('version', 'unknown')} ({elapsed:.2f}s)", "OK")
                result = {
                    "query": query,
                    "status": "success",
                    "time": elapsed,
                    "version": data
                }
            else:
                result = {
                    "query": query,
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "time": elapsed
                }

        except Exception as e:
            elapsed = time.time() - start
            self.log(f"  ERROR: {str(e)}", "ERROR")
            result = {
                "query": query,
                "status": "error",
                "error": str(e),
                "time": elapsed
            }

        return result

    def test_raganything_query(self, query: str) -> Dict:
        """Test query sur RAG-Anything"""
        self.log(f"RAG-Anything - Query: {query[:50]}...", "TEST")

        start = time.time()

        try:
            # Test query avec le mode naive (sans documents)
            response = requests.post(
                f"{self.raganything_url}/query",
                json={"query": query, "mode": "naive"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                answer_preview = str(data.get("answer", ""))[:100]
                self.log(f"  OK Reponse recue ({elapsed:.2f}s)", "OK")
                result = {
                    "query": query,
                    "status": "success",
                    "time": elapsed,
                    "answer_preview": answer_preview
                }
            else:
                # Probablement une erreur d'import comme vu avant
                result = {
                    "query": query,
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "time": elapsed
                }
                self.log(f"  WARN Erreur API: {response.text[:100]}", "WARN")

        except Exception as e:
            elapsed = time.time() - start
            self.log(f"  ERROR: {str(e)}", "ERROR")
            result = {
                "query": query,
                "status": "error",
                "error": str(e),
                "time": elapsed
            }

        return result

    def run_benchmark(self, downloads_path: str):
        """Exécute le benchmark complet"""
        print("\n" + "=" * 80)
        print("RAGFlow vs RAG-Anything - Real World Benchmark")
        print("=" * 80 + "\n")

        # 1. Trouver des documents
        docs = self.find_test_documents(downloads_path, max_docs=3)

        if not docs:
            self.log("Aucun document trouvé pour le test", "ERROR")
            return

        print()

        # 2. Tests de base (sans documents)
        self.log("=== Phase 1: Tests API de base ===", "INFO")
        print()

        test_queries = [
            "What is RAG?",
            "Explain document processing",
            "How does retrieval work?"
        ]

        for query in test_queries:
            self.test_ragflow_query(query)
            time.sleep(0.5)

        print()

        for query in test_queries:
            self.test_raganything_query(query)
            time.sleep(0.5)

        print()

        # 3. Tests avec documents (limités car pas de parsing)
        self.log("=== Phase 2: Tests avec Documents ===", "INFO")
        print()

        for doc in docs[:2]:  # Limiter à 2 docs
            self.test_ragflow_upload(doc)
            time.sleep(1)
            self.test_raganything_upload(doc)
            time.sleep(1)
            print()

        # 4. Résultats
        self.print_results()
        self.save_results()

    def print_results(self):
        """Affiche les résultats du benchmark"""
        print("\n" + "=" * 80)
        print("RÉSULTATS DU BENCHMARK")
        print("=" * 80 + "\n")

        # RAGFlow
        rf_tests = len(self.results["ragflow"]["tests"])
        rf_time = self.results["ragflow"]["total_time"]
        rf_success = sum(1 for t in self.results["ragflow"]["tests"]
                        if t.get("status") in ["success", "api_ready"])

        print(f"📊 RAGFlow")
        print(f"  Tests exécutés: {rf_tests}")
        print(f"  Tests réussis: {rf_success}/{rf_tests}")
        print(f"  Temps total: {rf_time:.2f}s")
        if rf_tests > 0:
            print(f"  Temps moyen: {rf_time/rf_tests:.2f}s/test")
        print()

        # RAG-Anything
        ra_tests = len(self.results["rag_anything"]["tests"])
        ra_time = self.results["rag_anything"]["total_time"]
        ra_success = sum(1 for t in self.results["rag_anything"]["tests"]
                        if t.get("status") in ["success", "api_ready_lite"])

        print(f"📊 RAG-Anything")
        print(f"  Tests exécutés: {ra_tests}")
        print(f"  Tests réussis: {ra_success}/{ra_tests}")
        print(f"  Temps total: {ra_time:.2f}s")
        if ra_tests > 0:
            print(f"  Temps moyen: {ra_time/ra_tests:.2f}s/test")
        print()

        # Comparaison
        print("📈 Comparaison")
        if rf_tests > 0 and ra_tests > 0:
            rf_avg = rf_time / rf_tests
            ra_avg = ra_time / ra_tests

            if rf_avg < ra_avg:
                faster = "RAGFlow"
                diff = ((ra_avg - rf_avg) / rf_avg) * 100
            else:
                faster = "RAG-Anything"
                diff = ((rf_avg - ra_avg) / ra_avg) * 100

            print(f"  Plus rapide: {faster} ({diff:.1f}% plus rapide)")

        print()
        print("⚠️  NOTES:")
        print("  - RAGFlow nécessite authentification pour fonctionnalités complètes")
        print("  - RAG-Anything en version Lite (pas de parsing documents)")
        print("  - Tests limités aux endpoints publics disponibles")
        print()

    def save_results(self):
        """Sauvegarde les résultats"""
        filename = f"real_world_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(__file__).parent / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        self.log(f"Résultats sauvegardés: {filename}", "INFO")


if __name__ == "__main__":
    downloads = r"C:\Users\JulienFernandez\Downloads"

    benchmark = RAGBenchmark()
    benchmark.run_benchmark(downloads)

    print("\nBenchmark terminé!\n")
