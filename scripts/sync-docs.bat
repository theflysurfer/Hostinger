@echo off
REM ========================================
REM Synchronisation Documentation Local -> Remote
REM ========================================

setlocal enabledelayedexpansion

set VPS_HOST=automation@69.62.108.82
set LOCAL_DOCS=%~dp0..\docs
set REMOTE_DOCS=/opt/mkdocs/docs

echo.
echo ========================================
echo   Synchronisation Documentation
echo   Local -^> Remote (srv759970)
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
echo [+] Connexion OK
echo.

REM Verification repertoire local
if not exist "%LOCAL_DOCS%" (
    echo [!] Erreur: Repertoire docs/ introuvable
    pause
    exit /b 1
)

echo [*] Source locale : %LOCAL_DOCS%
echo [*] Destination    : %VPS_HOST%:%REMOTE_DOCS%
echo.

REM Afficher les fichiers qui seront synchronises
echo Fichiers a synchroniser:
echo ----------------------------------------
cd /d "%LOCAL_DOCS%"
dir /S /B *.md 2>nul | find /V "node_modules"
echo ----------------------------------------
echo.

set /p CONFIRM="Confirmer la synchronisation ? (O/N): "
if /i not "%CONFIRM%"=="O" (
    echo Synchronisation annulee
    pause
    exit /b 0
)

echo.
echo [1/4] Synchronisation index.md...
scp "%LOCAL_DOCS%\index.md" %VPS_HOST%:%REMOTE_DOCS%/index.md
if %errorlevel% neq 0 (
    echo [!] Erreur lors de la synchronisation de index.md
    pause
    exit /b 1
)
echo [+] index.md synchronise

echo.
echo [2/4] Synchronisation dossier services/...
if exist "%LOCAL_DOCS%\services" (
    ssh %VPS_HOST% "mkdir -p %REMOTE_DOCS%/services"
    scp -r "%LOCAL_DOCS%\services\*" %VPS_HOST%:%REMOTE_DOCS%/services/
    echo [+] services/ synchronise
) else (
    echo [!] Dossier services/ introuvable localement
)

echo.
echo [3/4] Synchronisation dossier infrastructure/...
if exist "%LOCAL_DOCS%\infrastructure" (
    ssh %VPS_HOST% "mkdir -p %REMOTE_DOCS%/infrastructure"
    scp -r "%LOCAL_DOCS%\infrastructure\*" %VPS_HOST%:%REMOTE_DOCS%/infrastructure/
    echo [+] infrastructure/ synchronise
) else (
    echo [!] Dossier infrastructure/ introuvable localement
)

echo.
echo [4/4] Synchronisation dossier guides/...
if exist "%LOCAL_DOCS%\guides" (
    ssh %VPS_HOST% "mkdir -p %REMOTE_DOCS%/guides"
    scp -r "%LOCAL_DOCS%\guides\*" %VPS_HOST%:%REMOTE_DOCS%/guides/
    echo [+] guides/ synchronise
) else (
    echo [!] Dossier guides/ introuvable localement
)

echo.
echo [*] Redemarrage MkDocs pour appliquer les changements...
ssh %VPS_HOST% "cd /opt/mkdocs && docker-compose restart" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Avertissement: Impossible de redemarrer MkDocs
    echo     Redemarrez manuellement: ssh %VPS_HOST% 'cd /opt/mkdocs && docker-compose restart'
) else (
    echo [+] MkDocs redemarré
)

echo.
echo ========================================
echo   SYNCHRONISATION TERMINEE !
echo ========================================
echo.
echo Documentation disponible sur:
echo   https://docs.srv759970.hstgr.cloud
echo.
echo Commandes utiles:
echo   - Voir les logs MkDocs : ssh %VPS_HOST% "docker logs mkdocs"
echo   - Rebuild MkDocs       : ssh %VPS_HOST% "cd /opt/mkdocs && docker-compose down && docker-compose up -d"
echo.

pause
exit /b 0
