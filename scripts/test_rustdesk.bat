@echo off
REM Script de test RustDesk
REM Verifie que le serveur RustDesk est operationnel

echo ========================================
echo    TEST RUSTDESK SERVER
echo ========================================
echo.

echo [1/4] Test connexion SSH...
ssh automation@69.62.108.82 "echo 'SSH OK'" || (echo ERREUR SSH && exit /b 1)
echo.

echo [2/4] Verification conteneurs...
ssh automation@69.62.108.82 "sudo docker ps | grep rustdesk"
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Conteneurs RustDesk non actifs
    exit /b 1
)
echo.

echo [3/4] Test ports...
ssh automation@69.62.108.82 "timeout 3 bash -c '</dev/tcp/127.0.0.1/21116' && echo 'Port 21116: OK' || echo 'Port 21116: FAIL'"
ssh automation@69.62.108.82 "timeout 3 bash -c '</dev/tcp/127.0.0.1/21117' && echo 'Port 21117: OK' || echo 'Port 21117: FAIL'"
echo.

echo [4/4] Affichage cle publique...
ssh automation@69.62.108.82 "sudo cat /opt/rustdesk/data/id_ed25519.pub"
echo.

echo ========================================
echo    INFORMATIONS DE CONFIGURATION
echo ========================================
echo.
echo Serveur ID : rustdesk.srv759970.hstgr.cloud
echo Port ID    : 21116 (ou laisser vide)
echo Relay      : rustdesk.srv759970.hstgr.cloud
echo Port Relay : 21117 (ou laisser vide)
echo.
echo Page web   : https://rustdesk.srv759970.hstgr.cloud
echo SSL        : Let's Encrypt (renouvele automatiquement)
echo.
echo Copier la cle publique ci-dessus dans votre client RustDesk
echo.

pause
