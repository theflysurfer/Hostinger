#!/usr/bin/env python3
"""
RAGFlow Benchmark Script
========================
Tests complets de performance et fonctionnalités pour RAGFlow

Usage:
    python ragflow_benchmark.py
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class RAGFlowBenchmark:
    def __init__(self, base_url: str = "https://ragflow.srv759970.hstgr.cloud"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": []
        }

    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level:5} | {message}")

    def test_connectivity(self) -> Tuple[bool, float]:
        """Test 1: Connectivité de base"""
        self.log("Test 1/6: Connectivité de base", "TEST")
        start = time.time()

        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            elapsed = time.time() - start

            success = response.status_code == 200
            self.log(f"  HTTP {response.status_code} - {elapsed:.3f}s", "OK" if success else "FAIL")

            self.results["tests"].append({
                "name": "connectivity",
                "success": success,
                "status_code": response.status_code,
                "response_time": elapsed,
                "timestamp": datetime.now().isoformat()
            })

            return success, elapsed

        except Exception as e:
            elapsed = time.time() - start
            self.log(f"  Erreur: {str(e)}", "ERROR")
            self.results["tests"].append({
                "name": "connectivity",
                "success": False,
                "error": str(e),
                "response_time": elapsed
            })
            return False, elapsed

    def test_response_times(self, iterations: int = 5) -> Dict:
        """Test 2: Temps de réponse (moyenne sur plusieurs requêtes)"""
        self.log(f"Test 2/6: Temps de réponse ({iterations} requêtes)", "TEST")

        times = []
        for i in range(iterations):
            start = time.time()
            try:
                response = requests.get(f"{self.base_url}/", timeout=10)
                elapsed = time.time() - start
                times.append(elapsed)
                self.log(f"  Requête {i+1}/{iterations}: {elapsed:.3f}s", "OK")
            except Exception as e:
                self.log(f"  Requête {i+1}/{iterations}: ERREUR - {str(e)}", "ERROR")

            time.sleep(0.5)  # Petit délai entre les requêtes

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            self.log(f"  Moyenne: {avg_time:.3f}s | Min: {min_time:.3f}s | Max: {max_time:.3f}s", "INFO")

            result = {
                "name": "response_times",
                "iterations": iterations,
                "average": avg_time,
                "min": min_time,
                "max": max_time,
                "all_times": times
            }
        else:
            result = {
                "name": "response_times",
                "iterations": iterations,
                "error": "Aucune requête réussie"
            }

        self.results["tests"].append(result)
        return result

    def test_api_endpoints(self) -> Dict:
        """Test 3: Endpoints API disponibles"""
        self.log("Test 3/6: Exploration des endpoints API", "TEST")

        endpoints = {
            "/": "Page d'accueil",
            "/api/health": "Health check",
            "/api/version": "Version info",
            "/api/user": "User info",
            "/api/kb": "Knowledge bases",
        }

        results = {}
        for endpoint, description in endpoints.items():
            try:
                start = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                elapsed = time.time() - start

                results[endpoint] = {
                    "description": description,
                    "status_code": response.status_code,
                    "response_time": elapsed,
                    "success": response.status_code < 400
                }

                status = "OK" if response.status_code < 400 else "FAIL"
                self.log(f"  {endpoint:20} | HTTP {response.status_code} | {elapsed:.3f}s | {description}", status)

            except Exception as e:
                results[endpoint] = {
                    "description": description,
                    "error": str(e),
                    "success": False
                }
                self.log(f"  {endpoint:20} | ERREUR: {str(e)}", "ERROR")

        self.results["tests"].append({
            "name": "api_endpoints",
            "endpoints": results
        })

        return results

    def test_concurrent_requests(self, num_requests: int = 10) -> Dict:
        """Test 4: Requêtes concurrentes"""
        self.log(f"Test 4/6: {num_requests} requêtes concurrentes", "TEST")

        import concurrent.futures

        def make_request(i):
            start = time.time()
            try:
                response = requests.get(f"{self.base_url}/", timeout=10)
                elapsed = time.time() - start
                return {
                    "request_id": i,
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": elapsed
                }
            except Exception as e:
                elapsed = time.time() - start
                return {
                    "request_id": i,
                    "success": False,
                    "error": str(e),
                    "response_time": elapsed
                }

        start_total = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            request_results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_time = time.time() - start_total

        successful = [r for r in request_results if r.get("success")]
        failed = [r for r in request_results if not r.get("success")]

        if successful:
            avg_response = sum(r["response_time"] for r in successful) / len(successful)
        else:
            avg_response = 0

        self.log(f"  Réussies: {len(successful)}/{num_requests}", "INFO")
        self.log(f"  Échouées: {len(failed)}/{num_requests}", "INFO" if not failed else "WARN")
        self.log(f"  Temps total: {total_time:.3f}s", "INFO")
        self.log(f"  Temps moyen par requête: {avg_response:.3f}s", "INFO")
        self.log(f"  Requêtes/seconde: {num_requests/total_time:.2f}", "INFO")

        result = {
            "name": "concurrent_requests",
            "num_requests": num_requests,
            "successful": len(successful),
            "failed": len(failed),
            "total_time": total_time,
            "avg_response_time": avg_response,
            "requests_per_second": num_requests / total_time,
            "details": request_results
        }

        self.results["tests"].append(result)
        return result

    def test_resource_usage(self) -> Dict:
        """Test 5: Utilisation des ressources (via SSH)"""
        self.log("Test 5/6: Utilisation des ressources", "TEST")

        import subprocess

        try:
            # Docker stats pour RAGFlow
            result = subprocess.run(
                ['ssh', 'root@69.62.108.82',
                 'docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" | grep ragflow'],
                capture_output=True,
                text=True,
                timeout=10
            )

            resources = {}
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(',')
                        if len(parts) == 3:
                            name, cpu, mem = parts
                            resources[name] = {
                                "cpu_percent": cpu,
                                "memory_usage": mem
                            }
                            self.log(f"  {name:20} | CPU: {cpu:8} | MEM: {mem}", "INFO")

            self.results["tests"].append({
                "name": "resource_usage",
                "resources": resources
            })

            return resources

        except Exception as e:
            self.log(f"  Erreur: {str(e)}", "ERROR")
            self.results["tests"].append({
                "name": "resource_usage",
                "error": str(e)
            })
            return {}

    def test_elasticsearch_health(self) -> Dict:
        """Test 6: Santé Elasticsearch"""
        self.log("Test 6/6: Santé Elasticsearch", "TEST")

        import subprocess

        try:
            result = subprocess.run(
                ['ssh', 'root@69.62.108.82',
                 'curl -s -u elastic:infini_rag_flow http://localhost:1220/_cluster/health'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.stdout:
                health_data = json.loads(result.stdout)

                self.log(f"  Cluster: {health_data.get('cluster_name')}", "INFO")
                self.log(f"  Status: {health_data.get('status')}", "INFO")
                self.log(f"  Nodes: {health_data.get('number_of_nodes')}", "INFO")
                self.log(f"  Active shards: {health_data.get('active_shards')}", "INFO")

                self.results["tests"].append({
                    "name": "elasticsearch_health",
                    "health": health_data
                })

                return health_data

        except Exception as e:
            self.log(f"  Erreur: {str(e)}", "ERROR")
            self.results["tests"].append({
                "name": "elasticsearch_health",
                "error": str(e)
            })
            return {}

    def run_all_tests(self):
        """Exécute tous les tests"""
        self.log("=" * 70, "INFO")
        self.log("RAGFlow Benchmark - Début des tests", "INFO")
        self.log("=" * 70, "INFO")

        start_time = time.time()

        # Test 1: Connectivité
        self.test_connectivity()
        print()

        # Test 2: Temps de réponse
        self.test_response_times(iterations=5)
        print()

        # Test 3: Endpoints API
        self.test_api_endpoints()
        print()

        # Test 4: Requêtes concurrentes
        self.test_concurrent_requests(num_requests=10)
        print()

        # Test 5: Ressources
        self.test_resource_usage()
        print()

        # Test 6: Elasticsearch
        self.test_elasticsearch_health()
        print()

        total_time = time.time() - start_time

        self.log("=" * 70, "INFO")
        self.log(f"Tests terminés en {total_time:.2f}s", "INFO")
        self.log("=" * 70, "INFO")

        # Résumé
        self.print_summary()

        # Sauvegarder les résultats
        self.save_results()

    def print_summary(self):
        """Affiche un résumé des résultats"""
        print("\n" + "=" * 70)
        print("RÉSUMÉ DES TESTS")
        print("=" * 70 + "\n")

        total_tests = len(self.results["tests"])
        successful_tests = sum(1 for t in self.results["tests"] if t.get("success", True))

        print(f"Tests exécutés: {total_tests}")
        print(f"Tests réussis: {successful_tests}")
        print(f"Tests échoués: {total_tests - successful_tests}")
        print()

        # Performance globale
        conn_test = next((t for t in self.results["tests"] if t["name"] == "connectivity"), None)
        if conn_test and conn_test.get("success"):
            print(f"✓ RAGFlow est accessible")
            print(f"  Temps de réponse initial: {conn_test['response_time']:.3f}s")
        else:
            print(f"✗ RAGFlow n'est pas accessible")

        # Temps de réponse
        rt_test = next((t for t in self.results["tests"] if t["name"] == "response_times"), None)
        if rt_test and "average" in rt_test:
            print(f"\n✓ Temps de réponse moyen: {rt_test['average']:.3f}s")
            print(f"  Min: {rt_test['min']:.3f}s | Max: {rt_test['max']:.3f}s")

        # Concurrence
        conc_test = next((t for t in self.results["tests"] if t["name"] == "concurrent_requests"), None)
        if conc_test:
            print(f"\n✓ Requêtes concurrentes: {conc_test['successful']}/{conc_test['num_requests']} réussies")
            print(f"  Throughput: {conc_test['requests_per_second']:.2f} req/s")

        print("\n" + "=" * 70 + "\n")

    def save_results(self):
        """Sauvegarde les résultats en JSON"""
        filename = f"ragflow_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"C:\\Users\\JulienFernandez\\OneDrive\\Coding\\_référentiels de code\\Hostinger\\benchmark\\{filename}"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)

            self.log(f"Résultats sauvegardés: {filename}", "INFO")
        except Exception as e:
            self.log(f"Erreur lors de la sauvegarde: {str(e)}", "ERROR")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RAGFlow Performance Benchmark")
    print("=" * 70 + "\n")

    benchmark = RAGFlowBenchmark()
    benchmark.run_all_tests()

    print("\nBenchmark terminé !\n")
