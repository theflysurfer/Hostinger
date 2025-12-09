#!/usr/bin/env python3
"""
Script d'analyse avancée des images Docker
Génère un rapport détaillé au format JSON et texte
"""

import subprocess
import json
import sys
from datetime import datetime
from typing import List, Dict, Any
import re

class DockerImageAnalyzer:
    def __init__(self):
        self.images = []
        self.containers = []
        self.dangling_images = []
        self.unused_images = []

    def run_command(self, cmd: List[str]) -> str:
        """Exécute une commande shell et retourne le résultat"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de {' '.join(cmd)}: {e}", file=sys.stderr)
            return ""

    def parse_size(self, size_str: str) -> float:
        """Convertit une taille Docker (ex: 1.5GB, 500MB) en MB"""
        if not size_str:
            return 0.0

        match = re.match(r'([\d.]+)\s*(GB|MB|KB|B)', size_str.upper())
        if not match:
            return 0.0

        value, unit = match.groups()
        value = float(value)

        conversions = {
            'GB': 1024,
            'MB': 1,
            'KB': 1/1024,
            'B': 1/(1024*1024)
        }

        return value * conversions.get(unit, 0)

    def get_all_images(self):
        """Récupère toutes les images Docker"""
        output = self.run_command([
            'docker', 'images',
            '--format', '{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedAt}}'
        ])

        for line in output.split('\n'):
            if not line:
                continue

            parts = line.split('|')
            if len(parts) == 5:
                repo, tag, image_id, size, created = parts
                self.images.append({
                    'repository': repo,
                    'tag': tag,
                    'id': image_id,
                    'size': size,
                    'size_mb': self.parse_size(size),
                    'created': created,
                    'is_dangling': repo == '<none>' and tag == '<none>'
                })

    def get_all_containers(self):
        """Récupère tous les conteneurs"""
        output = self.run_command([
            'docker', 'ps', '-a',
            '--format', '{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}'
        ])

        for line in output.split('\n'):
            if not line:
                continue

            parts = line.split('|')
            if len(parts) == 4:
                container_id, image, status, name = parts
                self.containers.append({
                    'id': container_id,
                    'image': image,
                    'status': status,
                    'name': name,
                    'is_running': 'Up' in status
                })

    def identify_dangling_images(self):
        """Identifie les images dangling"""
        self.dangling_images = [img for img in self.images if img['is_dangling']]

    def identify_unused_images(self):
        """Identifie les images non utilisées par aucun conteneur"""
        used_images = set()

        for container in self.containers:
            # Ajouter l'image exacte utilisée
            used_images.add(container['image'])

            # Trouver l'ID de l'image correspondante
            for img in self.images:
                img_ref = f"{img['repository']}:{img['tag']}"
                if img_ref == container['image'] or img['id'][:12] == container['image'][:12]:
                    used_images.add(img['id'])
                    used_images.add(img_ref)

        # Les images inutilisées sont celles qui ne sont pas dans used_images
        for img in self.images:
            img_ref = f"{img['repository']}:{img['tag']}"
            if img['id'] not in used_images and img_ref not in used_images and not img['is_dangling']:
                self.unused_images.append(img)

    def get_system_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques système Docker"""
        output = self.run_command(['docker', 'system', 'df', '--format', 'json'])

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {}

    def calculate_statistics(self) -> Dict[str, Any]:
        """Calcule les statistiques globales"""
        total_images = len(self.images)
        dangling_count = len(self.dangling_images)
        unused_count = len(self.unused_images)

        total_size_mb = sum(img['size_mb'] for img in self.images)
        dangling_size_mb = sum(img['size_mb'] for img in self.dangling_images)
        unused_size_mb = sum(img['size_mb'] for img in self.unused_images)

        # Top 10 des plus grosses images
        top_images = sorted(self.images, key=lambda x: x['size_mb'], reverse=True)[:10]

        # Grouper par projet/repository
        projects = {}
        for img in self.images:
            repo = img['repository'].split('/')[0].split('_')[0]
            if repo == '<none>':
                repo = 'dangling'

            if repo not in projects:
                projects[repo] = {'count': 0, 'size_mb': 0}

            projects[repo]['count'] += 1
            projects[repo]['size_mb'] += img['size_mb']

        return {
            'total_images': total_images,
            'dangling_count': dangling_count,
            'unused_count': unused_count,
            'total_size_mb': total_size_mb,
            'total_size_gb': total_size_mb / 1024,
            'dangling_size_mb': dangling_size_mb,
            'dangling_size_gb': dangling_size_mb / 1024,
            'unused_size_mb': unused_size_mb,
            'unused_size_gb': unused_size_mb / 1024,
            'top_images': top_images,
            'projects': projects,
            'containers_total': len(self.containers),
            'containers_running': sum(1 for c in self.containers if c['is_running']),
            'containers_stopped': sum(1 for c in self.containers if not c['is_running'])
        }

    def generate_report(self, output_format='text') -> str:
        """Génère le rapport dans le format spécifié"""
        stats = self.calculate_statistics()

        if output_format == 'json':
            report = {
                'timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'dangling_images': self.dangling_images,
                'unused_images': self.unused_images,
                'all_images': self.images,
                'containers': self.containers
            }
            return json.dumps(report, indent=2)

        else:  # text format
            lines = []
            lines.append("=" * 60)
            lines.append("  RAPPORT D'ANALYSE DES IMAGES DOCKER")
            lines.append("=" * 60)
            lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

            lines.append("STATISTIQUES GLOBALES")
            lines.append("-" * 60)
            lines.append(f"Images totales: {stats['total_images']}")
            lines.append(f"Espace total: {stats['total_size_gb']:.2f} GB ({stats['total_size_mb']:.0f} MB)")
            lines.append("")

            lines.append(f"Images dangling: {stats['dangling_count']}")
            lines.append(f"Espace dangling: {stats['dangling_size_gb']:.2f} GB ({stats['dangling_size_mb']:.0f} MB)")
            lines.append("")

            lines.append(f"Images inutilisées: {stats['unused_count']}")
            lines.append(f"Espace inutilisé: {stats['unused_size_gb']:.2f} GB ({stats['unused_size_mb']:.0f} MB)")
            lines.append("")

            lines.append(f"Conteneurs totaux: {stats['containers_total']}")
            lines.append(f"  - En cours: {stats['containers_running']}")
            lines.append(f"  - Arrêtés: {stats['containers_stopped']}")
            lines.append("")

            lines.append("TOP 10 DES PLUS GROSSES IMAGES")
            lines.append("-" * 60)
            for i, img in enumerate(stats['top_images'], 1):
                repo_tag = f"{img['repository']}:{img['tag']}"
                lines.append(f"{i:2d}. {repo_tag:50s} {img['size']:>10s}")
            lines.append("")

            lines.append("IMAGES PAR PROJET")
            lines.append("-" * 60)
            sorted_projects = sorted(stats['projects'].items(),
                                    key=lambda x: x[1]['size_mb'], reverse=True)
            for project, data in sorted_projects[:15]:
                size_gb = data['size_mb'] / 1024
                lines.append(f"{project:30s} {data['count']:3d} images  {size_gb:6.2f} GB")
            lines.append("")

            if stats['dangling_count'] > 0:
                lines.append("⚠ RECOMMANDATION: Nettoyez les images dangling")
                lines.append(f"  Commande: docker image prune -f")
                lines.append(f"  Espace récupérable: {stats['dangling_size_gb']:.2f} GB")
                lines.append("")

            if stats['unused_count'] > 10:
                lines.append("⚠ RECOMMANDATION: Vérifiez les images inutilisées")
                lines.append(f"  {stats['unused_count']} images inutilisées détectées")
                lines.append(f"  Espace récupérable: {stats['unused_size_gb']:.2f} GB")
                lines.append("")

            lines.append("=" * 60)

            return '\n'.join(lines)

    def run_analysis(self, output_format='text'):
        """Exécute l'analyse complète"""
        print("Récupération des images Docker...", file=sys.stderr)
        self.get_all_images()

        print("Récupération des conteneurs...", file=sys.stderr)
        self.get_all_containers()

        print("Identification des images dangling...", file=sys.stderr)
        self.identify_dangling_images()

        print("Identification des images inutilisées...", file=sys.stderr)
        self.identify_unused_images()

        print("Génération du rapport...", file=sys.stderr)
        return self.generate_report(output_format)


def main():
    output_format = 'text'
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--json', '-j']:
            output_format = 'json'
        elif sys.argv[1] in ['--help', '-h']:
            print("Usage: docker-images-report.py [--json|-j] [--help|-h]")
            print("")
            print("Options:")
            print("  --json, -j    Génère le rapport au format JSON")
            print("  --help, -h    Affiche ce message d'aide")
            print("")
            print("Exemples:")
            print("  docker-images-report.py")
            print("  docker-images-report.py --json > report.json")
            sys.exit(0)

    analyzer = DockerImageAnalyzer()
    report = analyzer.run_analysis(output_format)
    print(report)


if __name__ == '__main__':
    main()
