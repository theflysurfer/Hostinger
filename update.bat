@echo off
REM ========================================
REM Script de mise a jour application VPS
REM ========================================

setlocal enabledelayedexpansion

set VPS_HOST=root@69.62.108.82

echo.
echo ========================================
echo   Mise a jour application VPS
echo ========================================
echo.

REM Verification connexion SSH
echo [CHECK] Verification connexion SSH...
ssh -o ConnectTimeout=5 %VPS_HOST% "echo 'OK'" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur: Impossible de se connecter au VPS
    pause
    exit /b 1
)
echo [+] Connexion SSH OK
echo.

REM Lister les applications deployees
echo Applications deployees:
echo ========================================
ssh %VPS_HOST% "ls -1 /opt/ 2>/dev/null | grep -v 'lost+found'" > temp_apps.txt

set /a COUNT=0
for /f "delims=" %%a in (temp_apps.txt) do (
    set /a COUNT+=1
    echo   !COUNT!. %%a
    set APP_!COUNT!=%%a
)

del temp_apps.txt

if %COUNT%==0 (
    echo [!] Aucune application trouvee
    pause
    exit /b 1
)

echo ========================================
echo.

REM Choisir l'application
set /p APP_CHOICE="Numero de l'application a mettre a jour: "

if not defined APP_%APP_CHOICE% (
    echo [!] Choix invalide
    pause
    exit /b 1
)

call set APP_NAME=%%APP_%APP_CHOICE%%%

echo.
echo Application selectionnee: %APP_NAME%
echo.

REM Demander le repertoire local
set /p PROJECT_DIR="Repertoire local du projet: "

if not exist "%PROJECT_DIR%" (
    echo [!] Erreur: Le repertoire n'existe pas
    pause
    exit /b 1
)

REM Options de mise a jour
echo.
echo Que voulez-vous mettre a jour ?
echo.
echo   1. Tout (code + rebuild complet)
echo   2. Code seulement (sans rebuild)
echo   3. Base de donnees seulement
echo   4. Redemarrer sans changement
echo.
set /p UPDATE_TYPE="Votre choix (1-4): "

echo.
echo ========================================
echo DEBUT DE LA MISE A JOUR
echo ========================================
echo.

if "%UPDATE_TYPE%"=="1" goto :full_update
if "%UPDATE_TYPE%"=="2" goto :code_only
if "%UPDATE_TYPE%"=="3" goto :db_only
if "%UPDATE_TYPE%"=="4" goto :restart_only

echo [!] Choix invalide
pause
exit /b 1

:full_update
echo [*] Mise a jour complete (code + rebuild)
echo.

echo [1/5] Arret du conteneur...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose down" >nul 2>&1
echo [+] Conteneur arrete
echo.

echo [2/5] Transfert des fichiers...
cd /d "%PROJECT_DIR%"

scp -r * %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
echo [+] Fichiers transferes
echo.

echo [3/5] Rebuild de l'image (peut prendre 2-5 min)...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose build --no-cache" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur lors du build
    ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose build"
    pause
    exit /b 1
)
echo [+] Image rebuildee
echo.

echo [4/5] Demarrage du conteneur...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose up -d" >nul 2>&1
echo [+] Conteneur demarre
echo.

echo [5/5] Attente et verification...
timeout /t 10 /nobreak >nul
goto :verify

:code_only
echo [*] Mise a jour du code uniquement
echo.

echo [1/3] Transfert des fichiers...
cd /d "%PROJECT_DIR%"
scp -r * %VPS_HOST%:/opt/%APP_NAME%/ 2>nul
echo [+] Fichiers transferes
echo.

echo [2/3] Redemarrage du conteneur...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose restart" >nul 2>&1
echo [+] Conteneur redemarre
echo.

echo [3/3] Attente et verification...
timeout /t 5 /nobreak >nul
goto :verify

:db_only
echo [*] Mise a jour base de donnees uniquement
echo.

echo [1/3] Transfert de la base de donnees...
cd /d "%PROJECT_DIR%"

if exist "data\*.db" (
    scp data\*.db %VPS_HOST%:/opt/%APP_NAME%/data/ 2>nul
    echo [+] Base de donnees transferee
) else (
    echo [!] Aucune base de donnees trouvee dans data\
    pause
    exit /b 1
)
echo.

echo [2/3] Redemarrage du conteneur...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose restart" >nul 2>&1
echo [+] Conteneur redemarre
echo.

echo [3/3] Attente et verification...
timeout /t 5 /nobreak >nul
goto :verify

:restart_only
echo [*] Redemarrage sans changement
echo.

echo [1/2] Redemarrage du conteneur...
ssh %VPS_HOST% "cd /opt/%APP_NAME% && docker-compose restart" >nul 2>&1
echo [+] Conteneur redemarre
echo.

echo [2/2] Attente et verification...
timeout /t 5 /nobreak >nul
goto :verify

:verify
echo.
echo ========================================
echo VERIFICATION
echo ========================================
echo.

ssh %VPS_HOST% "docker ps | grep %APP_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Le conteneur ne semble pas actif
    echo     Logs:
    ssh %VPS_HOST% "docker logs %APP_NAME% --tail=30"
    pause
    exit /b 1
)

echo [+] Conteneur actif
echo.

echo Logs (20 dernieres lignes):
echo ========================================
ssh %VPS_HOST% "docker logs %APP_NAME% --tail=20"
echo ========================================
echo.

REM Recuperer le port
for /f "tokens=2 delims=:" %%p in ('ssh %VPS_HOST% "docker ps --filter name=%APP_NAME% --format {{.Ports}}" ^| findstr /C:"->"') do (
    for /f "tokens=1 delims=/" %%a in ("%%p") do set APP_PORT=%%a
)

echo.
echo ========================================
echo   MISE A JOUR TERMINEE AVEC SUCCES !
echo ========================================
echo.
echo Application : %APP_NAME%
echo URL         : http://69.62.108.82:%APP_PORT%
echo.

set /p OPEN_BROWSER="Ouvrir dans le navigateur ? (O/N): "
if /i "%OPEN_BROWSER%"=="O" (
    start http://69.62.108.82:%APP_PORT%
)

echo.
pause
exit /b 0
