@echo off
REM ========================================
REM Script de deploiement automatique VPS
REM ========================================

setlocal enabledelayedexpansion

set VPS_HOST=root@69.62.108.82

echo.
echo ========================================
echo   Deploiement automatique VPS Hostinger
echo ========================================
echo.

REM Verification connexion SSH
echo [CHECK] Verification connexion SSH...
ssh -o ConnectTimeout=5 %VPS_HOST% "echo 'OK'" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur: Impossible de se connecter au VPS
    echo     Verifiez votre connexion SSH
    pause
    exit /b 1
)
echo [+] Connexion SSH OK
echo.

REM Demander le type d'application
echo Quel type d'application voulez-vous deployer ?
echo.
echo   1. Streamlit (Dashboard/App Python)
echo   2. Flask (API Python)
echo   3. FastAPI (API Python moderne)
echo   4. Node.js / Express
echo   5. React (Frontend)
echo   6. Autre / Personnalise
echo.
set /p APP_TYPE="Votre choix (1-6): "

REM Demander le nom de l'application
echo.
set /p APP_NAME="Nom de l'application (ex: mon-dashboard): "

REM Validation du nom
echo %APP_NAME% | findstr /R "^[a-z0-9-]*$" >nul
if %errorlevel% neq 0 (
    echo [!] Erreur: Le nom doit contenir uniquement des lettres minuscules, chiffres et tirets
    pause
    exit /b 1
)

REM Demander le repertoire local
echo.
echo Repertoire du projet local ?
set /p PROJECT_DIR="Chemin complet (ex: C:\...\MonProjet): "

REM Verifier que le repertoire existe
if not exist "%PROJECT_DIR%" (
    echo [!] Erreur: Le repertoire n'existe pas
    pause
    exit /b 1
)

REM Trouver un port disponible
echo.
echo [*] Recherche d'un port disponible...
ssh %VPS_HOST% "docker ps --format '{{.Ports}}'" > temp_ports.txt

set PORT_BASE=8501
set PORT_FOUND=0

for /L %%i in (1,1,50) do (
    set /a TEST_PORT=!PORT_BASE! + %%i
    findstr /C:"!TEST_PORT!" temp_ports.txt >nul 2>&1
    if !errorlevel! neq 0 (
        set PORT_AVAILABLE=!TEST_PORT!
        set PORT_FOUND=1
        goto :port_found
    )
)

:port_found
del temp_ports.txt

if %PORT_FOUND%==0 (
    echo [!] Erreur: Aucun port disponible trouve
    pause
    exit /b 1
)

echo [+] Port disponible trouve: %PORT_AVAILABLE%
echo.

REM Resume
echo ========================================
echo RESUME DU DEPLOIEMENT
echo ========================================
echo.
echo Application : %APP_NAME%
echo Type        : %APP_TYPE%
echo Projet      : %PROJECT_DIR%
echo Port VPS    : %PORT_AVAILABLE%
echo URL finale  : http://69.62.108.82:%PORT_AVAILABLE%
echo.
set /p CONFIRM="Confirmer le deploiement ? (O/N): "

if /i not "%CONFIRM%"=="O" (
    echo Deploiement annule
    pause
    exit /b 0
)

echo.
echo ========================================
echo DEBUT DU DEPLOIEMENT
echo ========================================
echo.

REM Etape 1: Creer la structure sur le VPS
echo [1/7] Creation de la structure sur le VPS...
ssh %VPS_HOST% "mkdir -p /opt/%APP_NAME%" 2>nul
echo [+] Structure creee: /opt/%APP_NAME%
echo.

REM Etape 2: Generer les fichiers Docker selon le type
echo [2/7] Generation des fichiers Docker...

if "%APP_TYPE%"=="1" (
    call :create_streamlit_files
) else if "%APP_TYPE%"=="2" (
    call :create_flask_files
) else if "%APP_TYPE%"=="3" (
    call :create_fastapi_files
) else if "%APP_TYPE%"=="4" (
    call :create_nodejs_files
) else if "%APP_TYPE%"=="5" (
    call :create_react_files
) else (
    echo [!] Type personnalise - vous devez creer Dockerfile manuellement
    pause
    exit /b 1
)

echo [+] Fichiers Docker generes
echo.

REM Etape 3: Transferer les fichiers
echo [3/7] Transfert des fichiers vers le VPS...
cd /d "%PROJECT_DIR%"

scp Dockerfile %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
scp docker-compose.yml %VPS_HOST%:/opt/%APP_NAME%/ 2>nul

if exist "requirements.txt" (
    scp requirements.txt %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
)
if exist "package.json" (
    scp package.json %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
    scp package-lock.json %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
)

REM Transferer les fichiers source
if exist "*.py" (
    scp *.py %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
)
if exist "src" (
    scp -r src %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
)
if exist "data" (
    scp -r data %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
)
if exist "dashboard" (
    scp -r dashboard %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
)

echo [+] Fichiers transferes
echo.

REM Etape 4: Construire l'image Docker
echo [4/7] Construction de l'image Docker (peut prendre 2-5 min)...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose build" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur lors du build Docker
    echo     Verification des logs...
    ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose build"
    pause
    exit /b 1
)
echo [+] Image Docker construite
echo.

REM Etape 5: Lancer le conteneur
echo [5/7] Lancement du conteneur...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose up -d" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur au lancement
    pause
    exit /b 1
)
echo [+] Conteneur demarre
echo.

REM Etape 6: Attendre le demarrage
echo [6/7] Attente du demarrage de l'application (10s)...
timeout /t 10 /nobreak >nul
echo.

REM Etape 7: Verification
echo [7/7] Verification du deploiement...
ssh %VPS_HOST% "docker ps | grep %APP_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Le conteneur ne semble pas demarrer
    echo     Verification des logs...
    ssh %VPS_HOST% "docker logs %APP_NAME% --tail=20"
    pause
    exit /b 1
)

echo [+] Conteneur actif
echo.

REM Verification des logs
echo Verification des logs (20 dernieres lignes):
echo ========================================
ssh %VPS_HOST% "docker logs %APP_NAME% --tail=20"
echo ========================================
echo.

REM Succes !
echo.
echo ========================================
echo   DEPLOIEMENT TERMINE AVEC SUCCES !
echo ========================================
echo.
echo Application : %APP_NAME%
echo URL         : http://69.62.108.82:%PORT_AVAILABLE%
echo.
echo Commandes utiles:
echo   - Voir les logs       : ssh %VPS_HOST% "docker logs %APP_NAME%"
echo   - Redemarrer          : ssh %VPS_HOST% "docker restart %APP_NAME%"
echo   - Arreter             : ssh %VPS_HOST% "docker stop %APP_NAME%"
echo   - Voir tous conteneurs: ssh %VPS_HOST% "docker ps"
echo.

REM Ouvrir le navigateur ?
set /p OPEN_BROWSER="Ouvrir dans le navigateur ? (O/N): "
if /i "%OPEN_BROWSER%"=="O" (
    start http://69.62.108.82:%PORT_AVAILABLE%
)

echo.
pause
exit /b 0

REM ========================================
REM Fonctions de creation de fichiers
REM ========================================

:create_streamlit_files
(
echo FROM python:3.11-slim
echo.
echo WORKDIR /app
echo.
echo RUN apt-get update ^&^& apt-get install -y gcc ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo COPY . .
echo.
echo EXPOSE 8501
echo.
echo CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
) > "%PROJECT_DIR%\Dockerfile"

(
echo version: '3.8'
echo.
echo services:
echo   app:
echo     build: .
echo     container_name: %APP_NAME%
echo     ports:
echo       - "%PORT_AVAILABLE%:8501"
echo     restart: unless-stopped
echo     environment:
echo       - TZ=Europe/Paris
) > "%PROJECT_DIR%\docker-compose.yml"
goto :eof

:create_flask_files
(
echo FROM python:3.11-slim
echo.
echo WORKDIR /app
echo.
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo COPY . .
echo.
echo EXPOSE 5000
echo.
echo CMD ["python", "app.py"]
) > "%PROJECT_DIR%\Dockerfile"

(
echo version: '3.8'
echo.
echo services:
echo   app:
echo     build: .
echo     container_name: %APP_NAME%
echo     ports:
echo       - "%PORT_AVAILABLE%:5000"
echo     restart: unless-stopped
echo     environment:
echo       - TZ=Europe/Paris
) > "%PROJECT_DIR%\docker-compose.yml"
goto :eof

:create_fastapi_files
(
echo FROM python:3.11-slim
echo.
echo WORKDIR /app
echo.
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo COPY . .
echo.
echo EXPOSE 8000
echo.
echo CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
) > "%PROJECT_DIR%\Dockerfile"

(
echo version: '3.8'
echo.
echo services:
echo   app:
echo     build: .
echo     container_name: %APP_NAME%
echo     ports:
echo       - "%PORT_AVAILABLE%:8000"
echo     restart: unless-stopped
echo     environment:
echo       - TZ=Europe/Paris
) > "%PROJECT_DIR%\docker-compose.yml"
goto :eof

:create_nodejs_files
(
echo FROM node:18-slim
echo.
echo WORKDIR /app
echo.
echo COPY package*.json ./
echo RUN npm ci --only=production
echo.
echo COPY . .
echo.
echo EXPOSE 3000
echo.
echo CMD ["node", "server.js"]
) > "%PROJECT_DIR%\Dockerfile"

(
echo version: '3.8'
echo.
echo services:
echo   app:
echo     build: .
echo     container_name: %APP_NAME%
echo     ports:
echo       - "%PORT_AVAILABLE%:3000"
echo     restart: unless-stopped
echo     environment:
echo       - TZ=Europe/Paris
) > "%PROJECT_DIR%\docker-compose.yml"
goto :eof

:create_react_files
(
echo FROM node:18-slim AS build
echo.
echo WORKDIR /app
echo.
echo COPY package*.json ./
echo RUN npm ci
echo.
echo COPY . .
echo RUN npm run build
echo.
echo FROM nginx:alpine
echo COPY --from=build /app/build /usr/share/nginx/html
echo EXPOSE 80
echo CMD ["nginx", "-g", "daemon off;"]
) > "%PROJECT_DIR%\Dockerfile"

(
echo version: '3.8'
echo.
echo services:
echo   app:
echo     build: .
echo     container_name: %APP_NAME%
echo     ports:
echo       - "%PORT_AVAILABLE%:80"
echo     restart: unless-stopped
) > "%PROJECT_DIR%\docker-compose.yml"
goto :eof
