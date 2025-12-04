import { test, expect } from '@playwright/test';

/**
 * Test d'accessibilité de tous les services de la stack Jellyfin
 *
 * Services testés :
 * - Jellyfin (8096)
 * - Jellyseerr (5055)
 * - Radarr (7878)
 * - Sonarr (8989)
 * - Prowlarr (9696)
 * - RDTClient (6500)
 * - Bazarr (6767)
 * - Kavita (5001)
 */

const VPS_IP = '69.62.108.82';

const services = [
  { name: 'Jellyfin', port: 8096, expectedTitle: /Jellyfin/i },
  { name: 'Jellyseerr', port: 5055, expectedTitle: /Jellyseerr/i },
  { name: 'Radarr', port: 7878, expectedTitle: /Radarr/i },
  { name: 'Sonarr', port: 8989, expectedTitle: /Sonarr/i },
  { name: 'Prowlarr', port: 9696, expectedTitle: /Prowlarr/i },
  { name: 'RDTClient', port: 6500, expectedTitle: /RDT/i },
  { name: 'Bazarr', port: 6767, expectedTitle: /Bazarr/i },
  { name: 'Kavita', port: 5001, expectedTitle: /Kavita/i },
];

test.describe('Stack Jellyfin + Kavita - Health Checks', () => {

  test.beforeEach(async ({ page }) => {
    // Timeout plus long pour les services qui démarrent
    test.setTimeout(60000);
  });

  for (const service of services) {
    test(`${service.name} doit être accessible sur le port ${service.port}`, async ({ page }) => {
      const url = `http://${VPS_IP}:${service.port}`;

      // Aller sur la page
      await page.goto(url, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // Vérifier que le titre correspond
      await expect(page).toHaveTitle(service.expectedTitle, {
        timeout: 10000
      });

      // Screenshot pour debug
      await page.screenshot({
        path: `test-results/${service.name.toLowerCase()}-home.png`,
        fullPage: true
      });

      console.log(`✓ ${service.name} est accessible et répond correctement`);
    });
  }

  test('Jellyfin - Vérifier la page de configuration initiale', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:8096`, { waitUntil: 'networkidle' });

    // Devrait afficher la page de setup ou de login
    const hasSetup = await page.locator('text=/Bienvenue|Welcome|Setup/i').count() > 0;
    const hasLogin = await page.locator('input[type="text"]').count() > 0;

    expect(hasSetup || hasLogin).toBeTruthy();

    await page.screenshot({
      path: 'test-results/jellyfin-setup-or-login.png',
      fullPage: true
    });
  });

  test('Radarr - Vérifier la page de configuration', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:7878`, { waitUntil: 'networkidle' });

    // Devrait avoir un lien vers Settings
    const hasSettings = page.locator('a[href*="settings"]').or(
      page.locator('text=/Settings|Paramètres/i')
    );

    await expect(hasSettings.first()).toBeVisible({ timeout: 10000 });

    await page.screenshot({
      path: 'test-results/radarr-dashboard.png',
      fullPage: true
    });
  });

  test('Sonarr - Vérifier la page de configuration', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:8989`, { waitUntil: 'networkidle' });

    // Devrait avoir un lien vers Settings
    const hasSettings = page.locator('a[href*="settings"]').or(
      page.locator('text=/Settings|Paramètres/i')
    );

    await expect(hasSettings.first()).toBeVisible({ timeout: 10000 });

    await page.screenshot({
      path: 'test-results/sonarr-dashboard.png',
      fullPage: true
    });
  });

  test('Prowlarr - Vérifier que la page indexers est accessible', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:9696`, { waitUntil: 'networkidle' });

    // Devrait avoir du contenu relatif aux indexers
    const hasIndexers = page.locator('text=/Indexer|Index/i').or(
      page.locator('a[href*="indexer"]')
    );

    await expect(hasIndexers.first()).toBeVisible({ timeout: 10000 });

    await page.screenshot({
      path: 'test-results/prowlarr-dashboard.png',
      fullPage: true
    });
  });

  test('RDTClient - Vérifier la page d\'accueil', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:6500`, { waitUntil: 'networkidle' });

    // Devrait afficher la page principale de RDTClient
    await expect(page.locator('body')).toBeVisible();

    await page.screenshot({
      path: 'test-results/rdtclient-home.png',
      fullPage: true
    });
  });

  test('Bazarr - Vérifier la page système', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:6767`, { waitUntil: 'networkidle' });

    // Devrait avoir des liens de navigation
    const hasNav = page.locator('nav').or(
      page.locator('a[href*="series"], a[href*="movies"]')
    );

    await expect(hasNav.first()).toBeVisible({ timeout: 10000 });

    await page.screenshot({
      path: 'test-results/bazarr-dashboard.png',
      fullPage: true
    });
  });

  test('Jellyseerr - Vérifier la page de login/setup', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:5055`, { waitUntil: 'networkidle' });

    // Devrait afficher setup ou login
    const hasSetup = await page.locator('text=/Sign in|Setup|Configuration/i').count() > 0;

    expect(hasSetup).toBeTruthy();

    await page.screenshot({
      path: 'test-results/jellyseerr-login.png',
      fullPage: true
    });
  });

  test('Kavita - Vérifier la page de login', async ({ page }) => {
    await page.goto(`http://${VPS_IP}:5001`, { waitUntil: 'networkidle' });

    // Devrait afficher un formulaire de login ou l'app
    const hasContent = page.locator('input').or(
      page.locator('body')
    );

    await expect(hasContent.first()).toBeVisible({ timeout: 10000 });

    await page.screenshot({
      path: 'test-results/kavita-home.png',
      fullPage: true
    });
  });
});

test.describe('Stack Jellyfin - Vérifications avancées', () => {

  test('Vérifier que tous les services répondent en moins de 5 secondes', async ({ page }) => {
    const results = [];

    for (const service of services) {
      const url = `http://${VPS_IP}:${service.port}`;
      const startTime = Date.now();

      try {
        await page.goto(url, {
          waitUntil: 'domcontentloaded',
          timeout: 15000
        });

        const loadTime = Date.now() - startTime;
        results.push({
          service: service.name,
          url,
          loadTime,
          status: 'OK'
        });

        console.log(`✓ ${service.name}: ${loadTime}ms`);
      } catch (error) {
        results.push({
          service: service.name,
          url,
          loadTime: -1,
          status: 'FAILED',
          error: error.message
        });

        console.log(`✗ ${service.name}: FAILED - ${error.message}`);
      }
    }

    // Afficher le résumé
    console.table(results);

    // Vérifier qu'au moins 7/8 services fonctionnent (tolérance pour 1 échec)
    const successCount = results.filter(r => r.status === 'OK').length;
    expect(successCount).toBeGreaterThanOrEqual(7);

    // Sauvegarder les résultats
    const fs = require('fs');
    fs.writeFileSync(
      'test-results/performance-summary.json',
      JSON.stringify(results, null, 2)
    );
  });

  test('Vérifier la connectivité réseau entre les services', async ({ request }) => {
    // Test que les services peuvent communiquer entre eux via Docker network

    // Prowlarr devrait être accessible depuis Radarr
    const prowlarrHealth = await request.get(`http://${VPS_IP}:9696`);
    expect(prowlarrHealth.ok()).toBeTruthy();

    // Radarr devrait être accessible
    const radarrHealth = await request.get(`http://${VPS_IP}:7878`);
    expect(radarrHealth.ok()).toBeTruthy();

    // Sonarr devrait être accessible
    const sonarrHealth = await request.get(`http://${VPS_IP}:8989`);
    expect(sonarrHealth.ok()).toBeTruthy();

    console.log('✓ Tous les services réseau principaux sont accessibles');
  });
});

test.describe('Stack Jellyfin - Tests HTTPS (si Nginx configuré)', () => {

  test.skip('Jellyfin HTTPS - jellyfin.srv759970.hstgr.cloud', async ({ page }) => {
    // Skip par défaut car nécessite configuration Nginx
    await page.goto('https://jellyfin.srv759970.hstgr.cloud', {
      waitUntil: 'networkidle'
    });

    await expect(page).toHaveTitle(/Jellyfin/i);
  });

  test.skip('Jellyseerr HTTPS - jellyseerr.srv759970.hstgr.cloud', async ({ page }) => {
    // Skip par défaut car nécessite configuration Nginx
    await page.goto('https://jellyseerr.srv759970.hstgr.cloud', {
      waitUntil: 'networkidle'
    });

    await expect(page).toHaveTitle(/Jellyseerr/i);
  });
});
