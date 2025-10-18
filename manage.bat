@echo off
REM ========================================
REM Script de gestion applications VPS
REM ========================================

setlocal enabledelayedexpansion

set VPS_HOST=root@69.62.108.82

:menu
cls
echo.
echo ========================================
echo   Gestion Applications VPS Hostinger
echo ========================================
echo.

REM Verification connexion SSH
ssh -o ConnectTimeout=5 %VPS_HOST% "echo 'OK'" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur: Impossible de se connecter au VPS
    pause
    exit /b 1
)

echo Status serveur:
echo ========================================
ssh %VPS_HOST% "uptime"
echo.
ssh %VPS_HOST% "df -h / | tail -1"
echo ========================================
echo.

REM Lister les conteneurs actifs
echo Conteneurs actifs:
echo ========================================
ssh %VPS_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" 2>nul
echo ========================================
echo.

echo Actions disponibles:
echo.
echo   1. Voir les logs d'une application
echo   2. Redemarrer une application
echo   3. Arreter une application
echo   4. Demarrer une application
echo   5. Supprimer une application
echo   6. Voir les ressources (CPU/RAM)
echo   7. Nettoyer Docker (images inutilisees)
echo   8. Lister toutes les applications (/opt/)
echo   9. Quitter
echo.
set /p ACTION="Votre choix (1-9): "

if "%ACTION%"=="1" goto :show_logs
if "%ACTION%"=="2" goto :restart_app
if "%ACTION%"=="3" goto :stop_app
if "%ACTION%"=="4" goto :start_app
if "%ACTION%"=="5" goto :delete_app
if "%ACTION%"=="6" goto :show_resources
if "%ACTION%"=="7" goto :clean_docker
if "%ACTION%"=="8" goto :list_all_apps
if "%ACTION%"=="9" goto :quit

echo [!] Choix invalide
timeout /t 2 /nobreak >nul
goto :menu

:show_logs
cls
echo.
echo ========================================
echo   VOIR LES LOGS
echo ========================================
echo.

call :select_app
if "%SELECTED_APP%"=="" goto :menu

echo.
echo Logs de %SELECTED_APP% (50 dernieres lignes):
echo ========================================
ssh %VPS_HOST% "docker logs %SELECTED_APP% --tail=50"
echo ========================================
echo.

echo [F] Suivre les logs en temps reel
echo [R] Retour au menu
echo.
set /p LOG_ACTION="Votre choix: "

if /i "%LOG_ACTION%"=="F" (
    echo.
    echo Appuyez sur Ctrl+C pour arreter...
    ssh %VPS_HOST% "docker logs -f %SELECTED_APP%"
)

pause
goto :menu

:restart_app
cls
echo.
echo ========================================
echo   REDEMARRER UNE APPLICATION
echo ========================================
echo.

call :select_app
if "%SELECTED_APP%"=="" goto :menu

echo.
set /p CONFIRM="Confirmer le redemarrage de %SELECTED_APP% ? (O/N): "
if /i not "%CONFIRM%"=="O" goto :menu

echo.
echo [*] Redemarrage de %SELECTED_APP%...
ssh %VPS_HOST% "docker restart %SELECTED_APP%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur lors du redemarrage
) else (
    echo [+] Application redemarre
)

timeout /t 2 /nobreak >nul
goto :menu

:stop_app
cls
echo.
echo ========================================
echo   ARRETER UNE APPLICATION
echo ========================================
echo.

call :select_app
if "%SELECTED_APP%"=="" goto :menu

echo.
set /p CONFIRM="Confirmer l'arret de %SELECTED_APP% ? (O/N): "
if /i not "%CONFIRM%"=="O" goto :menu

echo.
echo [*] Arret de %SELECTED_APP%...
ssh %VPS_HOST% "docker stop %SELECTED_APP%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur lors de l'arret
) else (
    echo [+] Application arretee
)

timeout /t 2 /nobreak >nul
goto :menu

:start_app
cls
echo.
echo ========================================
echo   DEMARRER UNE APPLICATION
echo ========================================
echo.

REM Lister les conteneurs arretes
echo Conteneurs arretes:
echo ========================================
ssh %VPS_HOST% "docker ps -a --filter status=exited --format 'table {{.Names}}\t{{.Status}}'" 2>nul
echo ========================================
echo.

set /p APP_NAME="Nom de l'application a demarrer: "

echo.
echo [*] Demarrage de %APP_NAME%...
ssh %VPS_HOST% "docker start %APP_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Erreur lors du demarrage
    echo     Essayez: cd /opt/%APP_NAME% ^&^& docker-compose up -d
) else (
    echo [+] Application demarree
)

pause
goto :menu

:delete_app
cls
echo.
echo ========================================
echo   SUPPRIMER UNE APPLICATION
echo ========================================
echo.
echo [!] ATTENTION: Cette action est irreversible
echo.

call :select_app
if "%SELECTED_APP%"=="" goto :menu

echo.
echo Que voulez-vous supprimer ?
echo.
echo   1. Conteneur seulement (garder les fichiers)
echo   2. Tout (conteneur + fichiers dans /opt/)
echo   3. Annuler
echo.
set /p DELETE_TYPE="Votre choix (1-3): "

if "%DELETE_TYPE%"=="3" goto :menu
if "%DELETE_TYPE%"=="" goto :menu

echo.
set /p CONFIRM="CONFIRMER LA SUPPRESSION de %SELECTED_APP% ? (tapez OUI): "
if /i not "%CONFIRM%"=="OUI" (
    echo Suppression annulee
    pause
    goto :menu
)

echo.
if "%DELETE_TYPE%"=="1" (
    echo [*] Suppression du conteneur...
    ssh %VPS_HOST% "docker stop %SELECTED_APP% && docker rm %SELECTED_APP%" >nul 2>&1
    echo [+] Conteneur supprime
)

if "%DELETE_TYPE%"=="2" (
    echo [*] Suppression complete...
    ssh %VPS_HOST% "docker stop %SELECTED_APP% && docker rm %SELECTED_APP% && rm -rf /opt/%SELECTED_APP%" >nul 2>&1
    echo [+] Application completement supprimee
)

timeout /t 3 /nobreak >nul
goto :menu

:show_resources
cls
echo.
echo ========================================
echo   RESSOURCES SYSTEME
echo ========================================
echo.

echo Utilisation CPU/RAM par conteneur:
echo ========================================
ssh %VPS_HOST% "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'"
echo ========================================
echo.

echo Espace disque:
echo ========================================
ssh %VPS_HOST% "df -h /"
echo ========================================
echo.

echo Espace Docker:
echo ========================================
ssh %VPS_HOST% "docker system df"
echo ========================================
echo.

pause
goto :menu

:clean_docker
cls
echo.
echo ========================================
echo   NETTOYAGE DOCKER
echo ========================================
echo.

echo Espace actuel:
ssh %VPS_HOST% "docker system df"
echo.

set /p CONFIRM="Nettoyer les images inutilisees ? (O/N): "
if /i not "%CONFIRM%"=="O" goto :menu

echo.
echo [*] Nettoyage en cours...
ssh %VPS_HOST% "docker system prune -a -f"
echo.
echo [+] Nettoyage termine
echo.

echo Nouvel espace:
ssh %VPS_HOST% "docker system df"
echo.

pause
goto :menu

:list_all_apps
cls
echo.
echo ========================================
echo   TOUTES LES APPLICATIONS
echo ========================================
echo.

echo Applications dans /opt/:
echo ========================================
ssh %VPS_HOST% "ls -lh /opt/ | grep -v 'total' | grep -v 'lost+found'"
echo ========================================
echo.

echo Tous les conteneurs (actifs + arretes):
echo ========================================
ssh %VPS_HOST% "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
echo ========================================
echo.

pause
goto :menu

:select_app
echo Applications disponibles:
echo ========================================
ssh %VPS_HOST% "docker ps -a --format '{{.Names}}'" > temp_apps.txt

set /a COUNT=0
for /f "delims=" %%a in (temp_apps.txt) do (
    set /a COUNT+=1
    echo   !COUNT!. %%a
    set APP_!COUNT!=%%a
)

del temp_apps.txt

if %COUNT%==0 (
    echo [!] Aucune application trouvee
    set SELECTED_APP=
    pause
    exit /b
)

echo ========================================
echo.

set /p APP_CHOICE="Numero de l'application: "

if not defined APP_%APP_CHOICE% (
    echo [!] Choix invalide
    set SELECTED_APP=
    pause
    exit /b
)

call set SELECTED_APP=%%APP_%APP_CHOICE%%%
exit /b

:quit
cls
echo.
echo Au revoir !
echo.
timeout /t 1 /nobreak >nul
exit /b 0
