"""
Script 96: Analyse des Dépendances Docker
Génère un rapport détaillé des conteneurs, réseaux, volumes et leurs dépendances
Usage: python scripts/96_analyze_docker_dependencies.py
"""

import subprocess
import json
from collections import defaultdict
from datetime import datetime

def run_ssh_command(command):
    """Execute SSH command on remote server"""
    full_cmd = f'ssh root@srv759970.hstgr.cloud "{command}"'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_containers():
    """Get all containers with their info"""
    cmd = "docker ps -a --format '{{json .}}'"
    output = run_ssh_command(cmd)
    containers = []
    for line in output.split('\n'):
        if line.strip():
            try:
                containers.append(json.loads(line))
            except:
                pass
    return containers

def get_container_details(container_name):
    """Get detailed container info"""
    cmd = f"docker inspect {container_name}"
    output = run_ssh_command(cmd)
    try:
        return json.loads(output)[0]
    except:
        return None

def get_networks():
    """Get all Docker networks"""
    cmd = "docker network ls --format '{{json .}}'"
    output = run_ssh_command(cmd)
    networks = []
    for line in output.split('\n'):
        if line.strip():
            try:
                networks.append(json.loads(line))
            except:
                pass
    return networks

def get_volumes():
    """Get all Docker volumes"""
    cmd = "docker volume ls --format '{{json .}}'"
    output = run_ssh_command(cmd)
    volumes = []
    for line in output.split('\n'):
        if line.strip():
            try:
                volumes.append(json.loads(line))
            except:
                pass
    return volumes

def analyze_dependencies():
    """Analyze all dependencies"""
    print("=" * 80)
    print("ANALYSE DES DÉPENDANCES DOCKER")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get data
    print("[INFO] Récupération des conteneurs...")
    containers = get_containers()
    print(f"[OK] {len(containers)} conteneurs trouvés")

    print("[INFO] Récupération des réseaux...")
    networks = get_networks()
    print(f"[OK] {len(networks)} réseaux trouvés")

    print("[INFO] Récupération des volumes...")
    volumes = get_volumes()
    print(f"[OK] {len(volumes)} volumes trouvés")

    # Analyze by status
    print("\n" + "=" * 80)
    print("ÉTAT DES CONTENEURS")
    print("=" * 80)

    status_counts = defaultdict(int)
    running = []
    stopped = []
    unhealthy = []

    for c in containers:
        status = c['Status']
        status_counts[status.split()[0]] = status_counts.get(status.split()[0], 0) + 1

        if 'Up' in status:
            running.append(c['Names'])
            if 'unhealthy' in status.lower():
                unhealthy.append(c['Names'])
        else:
            stopped.append(c['Names'])

    print(f"🟢 Actifs: {len(running)}")
    print(f"🔴 Arrêtés: {len(stopped)}")
    print(f"⚠️  Unhealthy: {len(unhealthy)}")

    if unhealthy:
        print("\n⚠️  CONTENEURS UNHEALTHY:")
        for name in unhealthy:
            print(f"   - {name}")

    # Analyze networks
    print("\n" + "=" * 80)
    print("RÉSEAUX ET CONTENEURS")
    print("=" * 80)

    network_containers = defaultdict(list)

    for c in containers:
        details = get_container_details(c['Names'])
        if details and 'NetworkSettings' in details:
            for net_name, net_info in details['NetworkSettings']['Networks'].items():
                network_containers[net_name].append(c['Names'])

    # Sort networks by number of containers
    sorted_networks = sorted(network_containers.items(), key=lambda x: len(x[1]), reverse=True)

    for net_name, containers_in_net in sorted_networks:
        if net_name in ['bridge', 'host', 'none']:
            continue
        print(f"\n📡 {net_name} ({len(containers_in_net)} conteneurs)")
        for container in sorted(containers_in_net):
            status = next((c['Status'] for c in containers if c['Names'] == container), 'unknown')
            icon = "🟢" if "Up" in status else "🔴"
            print(f"   {icon} {container}")

    # Find multi-network containers
    print("\n" + "=" * 80)
    print("CONTENEURS MULTI-RÉSEAUX")
    print("=" * 80)

    multi_network = {}
    for c in containers:
        details = get_container_details(c['Names'])
        if details and 'NetworkSettings' in details:
            nets = list(details['NetworkSettings']['Networks'].keys())
            if len(nets) > 1:
                multi_network[c['Names']] = [n for n in nets if n not in ['bridge', 'host', 'none']]

    if multi_network:
        for container, nets in sorted(multi_network.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"🔗 {container}")
            for net in nets:
                print(f"   ├─ {net}")
    else:
        print("Aucun conteneur multi-réseau trouvé")

    # Analyze volumes
    print("\n" + "=" * 80)
    print("VOLUMES DOCKER")
    print("=" * 80)

    # Get volume usage
    cmd = "docker system df -v --format '{{json .Volumes}}'"
    output = run_ssh_command(cmd)

    volume_usage = {}
    try:
        for line in output.split('\n'):
            if 'Name' in line:
                parts = line.split()
                if len(parts) >= 4:
                    vol_name = parts[0]
                    size = parts[2] if len(parts) > 2 else 'unknown'
                    volume_usage[vol_name] = size
    except:
        pass

    # Categorize volumes by project
    projects = defaultdict(list)
    for vol in volumes:
        name = vol['Name']
        if '_' in name:
            project = name.split('_')[0]
            projects[project].append(name)
        else:
            projects['other'].append(name)

    for project, vols in sorted(projects.items()):
        print(f"\n📦 {project.upper()}")
        for vol_name in sorted(vols):
            size = volume_usage.get(vol_name, 'unknown')
            print(f"   - {vol_name} ({size})")

    # Find potentially orphaned volumes
    print("\n" + "=" * 80)
    print("VOLUMES POTENTIELLEMENT ORPHELINS")
    print("=" * 80)

    orphan_projects = [
        'invidious', 'paperless-ai', 'paperless-ngx', 'rag-anything',
        'open-webui', 'deploy', 'wordpress-jesuishyperphagique',
        'wordpress-panneauxsolidaires', 'wordpress-solidarlink',
        'wordpress-shared-db'
    ]

    orphan_volumes = []
    for project in orphan_projects:
        if project in projects:
            orphan_volumes.extend(projects[project])

    if orphan_volumes:
        total_size = 0
        print("⚠️  Volumes de projets supprimés/arrêtés:\n")
        for vol in sorted(orphan_volumes):
            size_str = volume_usage.get(vol, '0B')
            print(f"   - {vol} ({size_str})")
        print(f"\n💡 Ces volumes peuvent probablement être supprimés")
    else:
        print("Aucun volume orphelin détecté")

    # Summary
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"📊 Conteneurs: {len(containers)} total")
    print(f"   🟢 Actifs: {len(running)}")
    print(f"   🔴 Arrêtés: {len(stopped)}")
    print(f"   ⚠️  Unhealthy: {len(unhealthy)}")
    print(f"\n📡 Réseaux: {len([n for n in networks if n['Name'] not in ['bridge', 'host', 'none']])} customs")
    print(f"📦 Volumes: {len(volumes)} total")
    print(f"   ⚠️  Potentiellement orphelins: {len(orphan_volumes)}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    import sys
    import io

    # Force UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    try:
        analyze_dependencies()
    except KeyboardInterrupt:
        print("\n\n[STOP] Analyse interrompue")
    except Exception as e:
        print(f"\n[ERREUR] {e}")
