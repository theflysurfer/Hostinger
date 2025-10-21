@echo off
REM ========================================
REM Recuperation Documentation Remote -> Local
REM ========================================

setlocal enabledelayedexpansion

set VPS_HOST=root@69.62.108.82
set LOCAL_DOCS=%~dp0..\docs
set REMOTE_DOCS=/opt/mkdocs/docs

echo.
echo ========================================
echo   Recuperation Documentation
echo   Remote (srv759970) -^> Local
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

REM Creer le repertoire local s'il n'existe pas
if not exist "%LOCAL_DOCS%" (
    mkdir "%LOCAL_DOCS%"
    echo [+] Repertoire docs/ cree
)

echo [*] Source distante : %VPS_HOST%:%REMOTE_DOCS%
echo [*] Destination     : %LOCAL_DOCS%
echo.

REM Avertissement si fichiers locaux existent
if exist "%LOCAL_DOCS%\*.md" (
    echo [!] ATTENTION: Des fichiers .md existent deja localement
    echo     Ils seront ecrases par les fichiers du serveur
    echo.
    set /p CONFIRM="Continuer ? (O/N): "
    if /i not "!CONFIRM!"=="O" (
        echo Operation annulee
        pause
        exit /b 0
    )
)

echo.
echo [1/5] Recuperation index.md...
scp %VPS_HOST%:%REMOTE_DOCS%/index.md "%LOCAL_DOCS%\index.md"
if %errorlevel% neq 0 (
    echo [!] Erreur lors de la recuperation de index.md
) else (
    echo [+] index.md recupere
)

echo.
echo [2/5] Recuperation dossier services/...
if not exist "%LOCAL_DOCS%\services" mkdir "%LOCAL_DOCS%\services"
scp -r %VPS_HOST%:%REMOTE_DOCS%/services/* "%LOCAL_DOCS%\services\"
if %errorlevel% neq 0 (
    echo [!] Erreur lors de la recuperation de services/
) else (
    echo [+] services/ recupere
)

echo.
echo [3/5] Recuperation dossier infrastructure/...
if not exist "%LOCAL_DOCS%\infrastructure" mkdir "%LOCAL_DOCS%\infrastructure"
scp -r %VPS_HOST%:%REMOTE_DOCS%/infrastructure/* "%LOCAL_DOCS%\infrastructure\"
if %errorlevel% neq 0 (
    echo [!] Erreur lors de la recuperation de infrastructure/
) else (
    echo [+] infrastructure/ recupere
)

echo.
echo [4/5] Recuperation dossier guides/...
if not exist "%LOCAL_DOCS%\guides" mkdir "%LOCAL_DOCS%\guides"
scp -r %VPS_HOST%:%REMOTE_DOCS%/guides/* "%LOCAL_DOCS%\guides\"
if %errorlevel% neq 0 (
    echo [!] Erreur lors de la recuperation de guides/
) else (
    echo [+] guides/ recupere
)

echo.
echo [5/5] Inventaire des fichiers recuperes...
cd /d "%LOCAL_DOCS%"
dir /S /B *.md 2>nul | find /V "node_modules"

echo.
echo ========================================
echo   RECUPERATION TERMINEE !
echo ========================================
echo.
echo Fichiers dans: %LOCAL_DOCS%
echo.
echo Prochaines etapes:
echo   - Editez les fichiers localement
echo   - Utilisez sync-docs.bat pour renvoyer vers le serveur
echo   - Committez dans Git pour versionner
echo.

pause
exit /b 0
