# Analyse: Stratégie d'Authentification - OAuth vs Basic Auth

**Date:** 2025-01-21
**Serveur:** srv759970.hstgr.cloud
**Auteur:** Analyse technique
**Status:** Recommandation

## Contexte

Actuellement, **13 services** sur srv759970.hstgr.cloud sont protégés par HTTP Basic Authentication via Nginx. Cette analyse évalue l'opportunité de migrer vers OAuth2/OIDC ou d'adopter une approche alternative.

## Inventaire des Services Protégés

### Services par Catégorie

| Catégorie | Services | Count |
|-----------|----------|-------|
| **Web/CMS** | clemence, cristina, admin.cristina (Strapi), wordpress | 4 |
| **APIs** | whisper, tika, ollama | 3 |
| **Monitoring** | grafana, dozzle, whisperx-dashboard | 3 |
| **Portails** | dashboard, sharepoint, portal | 3 |
| **TOTAL** | | **13** |

### Configuration Actuelle

**Méthode:** HTTP Basic Authentication (Nginx)
**Credentials:**
- Username: `julien`
- Password: `DevAccess2025`

**Fichier:** `/etc/nginx/.htpasswd` (APR1 hash)
**Snippet:** `/etc/nginx/snippets/basic-auth.conf`

```nginx
auth_basic "Restricted Access - srv759970";
auth_basic_user_file /etc/nginx/.htpasswd;
```

## Comparaison Détaillée

### Tableau Comparatif Global

| Critère | OAuth2/OIDC | Basic Auth | Gagnant |
|---------|-------------|------------|---------|
| **Sécurité** | Tokens révocables, expiration | Credentials statiques | 🏆 OAuth2 |
| **Granularité** | Scopes/permissions par service | Tout ou rien | 🏆 OAuth2 |
| **Audit** | Logs détaillés par utilisateur | Logs basiques | 🏆 OAuth2 |
| **SSO** | Single Sign-On entre services | Login par service | 🏆 OAuth2 |
| **UX** | UI moderne, pas de popup | Popup browser basic | 🏆 OAuth2 |
| **MFA** | Supporté nativement | Non supporté | 🏆 OAuth2 |
| **Session Management** | Révocation instantanée | Cache browser difficile à invalider | 🏆 OAuth2 |
| **Complexité** | Configuration complexe | 2 lignes nginx | 🏆 Basic Auth |
| **Maintenance** | Service additionnel | Fichier statique | 🏆 Basic Auth |
| **Ressources** | 300-800MB RAM | 0MB | 🏆 Basic Auth |
| **Setup** | 2-6 heures | 5 minutes | 🏆 Basic Auth |
| **Point de défaillance** | Auth server = SPOF | Aucune dépendance | 🏆 Basic Auth |
| **API simple** | Token management | `curl -u user:pass` | 🏆 Basic Auth |

**Score:** OAuth2 = 7/13 | Basic Auth = 6/13

## Solutions OAuth2 Disponibles

### 1. Authentik ⭐ RECOMMANDÉ (Self-Hosted)

**Type:** Open-source, self-hosted
**Ressources:** ~300MB RAM, 1 conteneur Docker
**Protocols:** OAuth2, OIDC, SAML, LDAP

**Avantages:**
- ✅ UI moderne et intuitive
- ✅ MFA intégré (TOTP, WebAuthn)
- ✅ User/Group management
- ✅ Integration Nginx via oauth2-proxy
- ✅ Monitoring intégré
- ✅ Gratuit

**Inconvénients:**
- ❌ 300MB RAM requis
- ❌ Setup 3-4 heures
- ❌ Maintenance ~1h/mois
- ❌ Point de défaillance (SPOF)

**URL:** https://goauthentik.io

### 2. Keycloak (Self-Hosted)

**Type:** Open-source, RedHat
**Ressources:** ~500-800MB RAM (Java)
**Protocols:** OAuth2, OIDC, SAML

**Avantages:**
- ✅ Enterprise-grade
- ✅ User federation (LDAP, AD)
- ✅ Fine-grained permissions
- ✅ Gratuit

**Inconvénients:**
- ❌ Lourd en ressources (600-800MB)
- ❌ Setup 4-6 heures
- ❌ Complexe pour petit serveur

### 3. oauth2-proxy + External Provider

**Type:** Lightweight reverse proxy
**Ressources:** ~20MB RAM
**Providers:** Google, GitHub, Azure AD, Authentik, Keycloak

**Avantages:**
- ✅ Très léger (20MB)
- ✅ Setup rapide (1-2h)
- ✅ Intégration nginx parfaite
- ✅ Gratuit (si provider gratuit)

**Inconvénients:**
- ❌ Dépend d'un provider externe
- ❌ Limité aux providers supportés

**Exemple:** GitHub OAuth pour authentification

### 4. Cloudflare Access 💰

**Type:** Managed (SaaS)
**Ressources:** 0 (cloud)
**Protocols:** OIDC, SAML, One-time PIN

**Avantages:**
- ✅ Zero Trust Network Access
- ✅ Pas de maintenance
- ✅ Logs et analytics
- ✅ Setup 30 minutes

**Inconvénients:**
- ❌ Coût: Free (50 users) ou $7/user/month
- ❌ Vendor lock-in
- ❌ Minimum 30 users en payant = $210/mois

### 5. Authelia

**Type:** Open-source, self-hosted
**Ressources:** ~50MB RAM
**Protocols:** OAuth2, OIDC

**Avantages:**
- ✅ Très léger (50MB)
- ✅ MFA (TOTP, U2F, Duo)
- ✅ Rules-based access control
- ✅ Gratuit

**Inconvénients:**
- ❌ Setup 2-3 heures
- ❌ Documentation moins complète qu'Authentik

### 6. Auth0 / Okta 💰

**Type:** Managed (SaaS)
**Coût:**
- Auth0: $23/mois (1,000 active users)
- Okta: $2/user/mois (minimum 25 users)

**Avantages:**
- ✅ Enterprise-grade
- ✅ Pas de maintenance

**Inconvénients:**
- ❌ Coût mensuel
- ❌ Vendor lock-in

## Comparaison des Coûts

| Solution | Setup Time | Monthly Cost | RAM Usage | Maintenance/mois |
|----------|------------|--------------|-----------|------------------|
| **Basic Auth (actuel)** | 0h | €0 | 0MB | 0h |
| **Tailscale VPN** | 0.5h | €0 | 0MB | 0h |
| **Authentik** | 4h | €0 | 300MB | 1h |
| **Keycloak** | 6h | €0 | 600MB | 2h |
| **oauth2-proxy + GitHub** | 2h | €0 | 20MB | 0.5h |
| **Authelia** | 3h | €0 | 50MB | 1h |
| **Cloudflare Access** | 0.5h | €0-210 | 0MB | 0h |
| **Auth0** | 2h | €23 | 0MB | 0h |

## Analyse par Type de Service

### APIs (whisper, tika, ollama)

**Usage:** Accès programmatique fréquent, scripts, intégrations

| Solution | Score | Rationale |
|----------|-------|-----------|
| **Basic Auth** | ⭐⭐⭐⭐ | Simple, fonctionne parfaitement |
| **API Keys custom** | ⭐⭐⭐⭐⭐ | Meilleur: révocables, par-client |
| **OAuth2 Client Credentials** | ⭐⭐⭐ | Overkill pour usage interne |

**Recommandation:** **Garder Basic Auth** ou migrer vers **API Keys custom**

**Exemple API Key Implementation:**
```python
# Simple API key validation in FastAPI
@app.get("/transcribe")
async def transcribe(api_key: str = Header(None)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(401, "Invalid API key")
```

### Monitoring (grafana, dozzle, whisperx-dashboard)

**Usage:** Accès occasionnel via browser, dashboards

| Solution | Score | Rationale |
|----------|-------|-----------|
| **Basic Auth** | ⭐⭐⭐ | Fonctionne mais pas de SSO |
| **OAuth2 (Authentik)** | ⭐⭐⭐⭐⭐ | SSO unifié, MFA, meilleure UX |
| **Tailscale VPN** | ⭐⭐⭐⭐⭐ | Sécurité maximale, pas de config app |
| **Cloudflare Access** | ⭐⭐⭐⭐ | Simple mais coût potentiel |

**Recommandation:** **Tailscale VPN** (meilleur rapport sécurité/simplicité)

### Web/CMS (clemence, cristina, wordpress, strapi)

**Usage:** Sites client, administration CMS

| Solution | Score | Rationale |
|----------|-------|-----------|
| **Basic Auth** | ⭐⭐⭐⭐ | Parfait pour staging/dev |
| **Application Auth native** | ⭐⭐⭐⭐⭐ | WordPress/Strapi ont déjà leur auth |
| **OAuth2** | ⭐⭐⭐ | Utile seulement si SSO requis |

**Recommandation:**
- **Sites en production:** Retirer Basic Auth, utiliser auth native
- **Sites en staging/dev:** Garder Basic Auth

### Portails (dashboard, sharepoint, portal)

**Usage:** Accès admin fréquent, gestion

| Solution | Score | Rationale |
|----------|-------|-----------|
| **Basic Auth** | ⭐⭐ | UX médiocre, pas de MFA |
| **OAuth2 (Authentik)** | ⭐⭐⭐⭐⭐ | SSO, MFA, audit |
| **Tailscale VPN** | ⭐⭐⭐⭐⭐ | Network-level, très sécurisé |

**Recommandation:** **Tailscale VPN** + optionnel Authentik OAuth2

## Recommandation Finale: Stratégie Hybride

### 🏆 Architecture Recommandée (Defense in Depth)

```
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 1: Tailscale VPN (Network Layer)                    │
│ ══════════════════════════════════════════════════════════  │
│ Services: grafana, dozzle, whisperx-dashboard,             │
│           portal, dashboard, sharepoint                     │
│ ──────────────────────────────────────────────────────────  │
│ Avantages:                                                  │
│ ✅ Sécurité maximale (Zero Trust Network)                  │
│ ✅ Setup: 30 minutes                                        │
│ ✅ Coût: Gratuit (20 devices)                              │
│ ✅ Maintenance: 0h/mois                                     │
│ ✅ MFA via Tailscale app                                    │
│ ✅ Pas de modification des services                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 2: Auth Native / Basic Auth (Application Layer)     │
│ ══════════════════════════════════════════════════════════  │
│ WordPress/Strapi: Utiliser leur système d'auth intégré     │
│ APIs: Garder Basic Auth ou migrer vers API Keys            │
│ Sites staging: Garder Basic Auth nginx                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 3 (Optionnel): Authentik OAuth2                     │
│ ══════════════════════════════════════════════════════════  │
│ SEULEMENT si besoin de:                                     │
│ - SSO unifié entre tous les services                        │
│ - Accès externe aux dashboards (hors VPN)                  │
│ - Audit logging avancé                                      │
│ ──────────────────────────────────────────────────────────  │
│ Setup: 3-4h | Coût: €0 | RAM: 300MB | Maintenance: 1h/mois │
└─────────────────────────────────────────────────────────────┘
```

### Plan de Migration Recommandé

#### ✅ Phase 1: Tailscale VPN (PRIORITÉ HAUTE)

**Objectif:** Sécuriser tous les dashboards/portails via VPN

**Services concernés:**
- monitoring.srv759970.hstgr.cloud (Grafana)
- dozzle.srv759970.hstgr.cloud
- whisperx-dashboard.srv759970.hstgr.cloud
- portal.srv759970.hstgr.cloud
- dashboard.srv759970.hstgr.cloud
- sharepoint.srv759970.hstgr.cloud

**Actions:**
1. Installer Tailscale sur srv759970
2. Configurer Nginx pour écouter sur Tailscale IP uniquement
3. Retirer Basic Auth nginx sur ces services
4. Ajouter appareils autorisés au réseau Tailscale

**Effort:** 30-60 minutes
**Impact:** 6 services retirés de l'internet public
**Sécurité:** ⬆️⬆️ (VPN >> Basic Auth)

#### ⚡ Phase 2: Cleanup Auth Native (PRIORITÉ MOYENNE)

**Objectif:** Utiliser l'auth native des CMS

**Services concernés:**
- wordpress.srv759970.hstgr.cloud
- admin.cristina.srv759970.hstgr.cloud (Strapi)

**Actions:**
1. Retirer `include snippets/basic-auth.conf;` de nginx
2. S'appuyer sur WordPress login / Strapi admin login
3. Optionnel: Configurer MFA dans WordPress/Strapi

**Effort:** 15 minutes
**Impact:** UX améliorée, moins de double-auth

#### 🔑 Phase 3: API Keys pour APIs (PRIORITÉ BASSE)

**Objectif:** Remplacer Basic Auth par API Keys custom

**Services concernés:**
- whisper.srv759970.hstgr.cloud
- tika.srv759970.hstgr.cloud
- ollama.srv759970.hstgr.cloud

**Actions:**
1. Implémenter validation API Key dans FastAPI
2. Générer keys par client/projet
3. Stockage dans Redis ou fichier JSON
4. Endpoint `/api/keys` pour gestion

**Effort:** 2-3 heures
**Impact:** Révocation par client, meilleur audit

#### 🎫 Phase 4 (Optionnelle): Authentik OAuth2

**Objectif:** SSO unifié si besoin d'accès externe

**Quand l'utiliser:**
- ❌ **NON recommandé** si Phase 1 (Tailscale) suffit
- ✅ Recommandé si besoin d'accès externe aux dashboards
- ✅ Recommandé si équipe > 5 personnes
- ✅ Recommandé si audit compliance requis

**Setup:**
1. Docker Compose Authentik
2. Configuration oauth2-proxy
3. Nginx integration
4. User/Group setup

**Effort:** 3-4 heures

## Matrice de Décision

### Critères de Choix

| Besoin | Solution Recommandée | Justification |
|--------|---------------------|---------------|
| **Sécurité maximale** | Tailscale VPN | Network-level, Zero Trust |
| **Simplicité** | Basic Auth | 2 lignes nginx, 0 maintenance |
| **SSO entre services** | Authentik OAuth2 | Standard OIDC |
| **Accès API** | API Keys ou Basic Auth | Simple, révocable |
| **Budget €0** | Tailscale + Authentik | 100% gratuit, self-hosted |
| **Pas de maintenance** | Tailscale ou Cloudflare | Set & forget |
| **Audit compliance** | Authentik ou Keycloak | Logs détaillés |
| **Équipe > 10** | Keycloak | Enterprise-grade |

## Impact Serveur

### Configuration Actuelle

**Ressources utilisées:**
- RAM: 0MB (Basic Auth = nginx natif)
- Maintenance: 0h/mois
- Complexité: Minimale

### Avec Tailscale (Recommandé)

**Ressources utilisées:**
- RAM: ~30MB (Tailscale daemon)
- Maintenance: 0h/mois
- Complexité: Minimale
- **Gain sécurité:** ⬆️⬆️

### Avec Authentik

**Ressources utilisées:**
- RAM: ~300MB (Authentik + PostgreSQL + Redis)
- Maintenance: 1h/mois
- Complexité: Moyenne
- **Gain fonctionnel:** SSO, MFA, audit

### Avec Keycloak

**Ressources utilisées:**
- RAM: ~600-800MB (Java)
- Maintenance: 2h/mois
- Complexité: Élevée
- **Gain fonctionnel:** Enterprise features

## Tableau de Synthèse Final

| Critère | Basic Auth | Tailscale | Authentik | Keycloak | Cloudflare |
|---------|------------|-----------|-----------|----------|------------|
| **Sécurité** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Simplicité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Coût** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Maintenance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Fonctionnalités** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **UX** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **TOTAL** | 17/30 | 26/30 | 25/30 | 22/30 | 24/30 |

## Conclusion

### ✅ Recommandation Officielle pour srv759970.hstgr.cloud

**NE PAS migrer vers OAuth2 complet.** Adopter une **approche hybride** progressive:

1. **Court terme (semaine 1):** Déployer Tailscale VPN
   - Retire 6 services de l'internet public
   - Coût: €0, Setup: 30 min, Sécurité: ++

2. **Court terme (semaine 1):** Cleanup auth native
   - WordPress, Strapi: retirer Basic Auth nginx
   - Utiliser leur système intégré

3. **Moyen terme (mois 1):** API Keys custom
   - whisper, tika, ollama
   - Meilleure gestion que Basic Auth

4. **Long terme (optionnel):** Authentik OAuth2
   - Seulement si besoin SSO ou accès externe
   - Évaluer après déploiement Tailscale

### Résultat Final

| Métrique | Avant | Après (Tailscale) | Δ |
|----------|-------|-------------------|---|
| **Sécurité** | Basic Auth (3/5) | VPN (5/5) | ⬆️⬆️ |
| **Complexité** | Minimale | Minimale | ➡️ |
| **Coût** | €0 | €0 | ➡️ |
| **UX** | Popup basic | Transparent | ⬆️ |
| **Maintenance** | 0h/mois | 0h/mois | ➡️ |
| **Services publics** | 13 | 7 | ⬇️⬇️ |

**Verdict:** Tailscale VPN offre le meilleur ROI (Return On Investment) en termes de sécurité, sans augmenter la complexité ni les coûts.

## Prochaines Étapes

1. **Valider** cette analyse avec l'équipe
2. **Planifier** la migration Tailscale (1 semaine)
3. **Documenter** la procédure de setup
4. **Tester** l'accès via VPN avant de retirer Basic Auth
5. **Monitorer** les accès post-migration

## Références

- [Infrastructure > Security](../infrastructure/security.md) - Sécurité actuelle
- [Guide > Basic Auth](../guides/GUIDE_BASIC_AUTH.md) - Configuration actuelle
- [Reference > Basic Auth Setup](../reference/security/basic-auth-setup.md) - Technique
- [Tailscale Documentation](https://tailscale.com/kb/) - VPN setup
- [Authentik Documentation](https://goauthentik.io/docs/) - OAuth2 setup

---

**Dernière mise à jour:** 2025-01-21
**Prochaine révision:** Après déploiement Phase 1 (Tailscale)
