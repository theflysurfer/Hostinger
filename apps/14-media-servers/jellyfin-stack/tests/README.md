# Tests Playwright - Stack Jellyfin

Tests automatisés pour vérifier que tous les services de la stack fonctionnent correctement.

## Installation

```bash
cd C:\Users\julien\OneDrive\Coding\_référentiels\ de\ code\Hostinger\apps\14-media-servers\jellyfin-stack

# Installer les dépendances
npm install

# Installer le navigateur Chromium
npm run install-browsers
```

## Lancer les tests

```bash
# Lancer tous les tests
npm test

# Lancer avec l'interface UI
npm run test:ui

# Lancer en mode debug
npm run test:debug

# Voir le rapport HTML
npm run test:report
```

## Tests inclus

### Health Checks (8 services)

- ✅ Jellyfin (8096)
- ✅ Jellyseerr (5055)
- ✅ Radarr (7878)
- ✅ Sonarr (8989)
- ✅ Prowlarr (9696)
- ✅ RDTClient (6500)
- ✅ Bazarr (6767)
- ✅ Kavita (5001)

### Tests avancés

- Temps de chargement de chaque service
- Connectivité réseau entre services
- Vérification des pages de configuration
- Screenshots automatiques en cas d'échec

### Tests HTTPS (skip par défaut)

- Jellyfin HTTPS (nécessite Nginx configuré)
- Jellyseerr HTTPS (nécessite Nginx configuré)

## Résultats

Les résultats sont sauvegardés dans `test-results/` :

```
test-results/
├── html-report/           # Rapport HTML interactif
├── results.json           # Résultats JSON
├── performance-summary.json  # Résumé des performances
└── *.png                  # Screenshots de chaque service
```

## Exemples de commandes

```bash
# Lancer seulement les health checks
npx playwright test --grep "doit être accessible"

# Lancer seulement Jellyfin
npx playwright test --grep "Jellyfin"

# Lancer en mode headed (voir le navigateur)
npm run test:headed

# Lancer un seul fichier
npx playwright test tests/check-services.spec.ts
```

## CI/CD

Ces tests peuvent être intégrés dans une pipeline CI/CD pour vérifier automatiquement que la stack fonctionne après un déploiement.

```yaml
# Exemple GitHub Actions
- name: Run Playwright tests
  run: |
    npm install
    npm run install-browsers
    npm test
```
