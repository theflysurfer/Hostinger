#!/bin/bash

#######################################
# Setup rclone for OneDrive sync
#
# Ce script installe et configure rclone
# pour synchroniser OneDrive vers le VPS
#######################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Rclone OneDrive Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. Installer rclone si nécessaire
if command -v rclone &> /dev/null; then
    echo -e "${GREEN}✓${NC} rclone est déjà installé"
    rclone version
else
    echo -e "${YELLOW}→${NC} Installation de rclone..."
    curl https://rclone.org/install.sh | sudo bash
    echo -e "${GREEN}✓${NC} rclone installé"
fi

echo ""
echo -e "${BLUE}Configuration de OneDrive${NC}"
echo ""
echo "Tu dois configurer rclone sur ton PC Windows d'abord, puis copier la config sur le VPS."
echo ""
echo -e "${YELLOW}Étapes sur ton PC Windows:${NC}"
echo ""
echo "1. Ouvre PowerShell et tape:"
echo "   rclone config"
echo ""
echo "2. Choisis:"
echo "   n) New remote"
echo "   name> onedrive"
echo "   Storage> microsoft onedrive"
echo "   client_id> (laisse vide, appuie sur Enter)"
echo "   client_secret> (laisse vide)"
echo "   region> 1 (Microsoft Cloud Global)"
echo "   Edit advanced config? n"
echo "   Use web browser to automatically authenticate? y"
echo ""
echo "3. Ton navigateur va s'ouvrir, connecte-toi à OneDrive"
echo ""
echo "4. Une fois configuré, copie le fichier de config:"
echo "   Windows: C:\\Users\\julien\\.config\\rclone\\rclone.conf"
echo ""
echo "5. Copie ce fichier sur le VPS:"
echo "   scp C:\\Users\\julien\\.config\\rclone\\rclone.conf automation@69.62.108.82:~/.config/rclone/"
echo ""
echo -e "${YELLOW}Ou utilise cette méthode alternative:${NC}"
echo ""
echo "1. Sur Windows, affiche la config:"
echo "   rclone config show"
echo ""
echo "2. Copie toute la section [onedrive]"
echo ""
echo "3. Sur le VPS, crée le fichier:"
echo "   mkdir -p ~/.config/rclone"
echo "   nano ~/.config/rclone/rclone.conf"
echo ""
echo "4. Colle la config et sauvegarde (Ctrl+O, Enter, Ctrl+X)"
echo ""

read -p "As-tu déjà configuré rclone ? (y/n): " CONFIGURED

if [ "$CONFIGURED" = "y" ] || [ "$CONFIGURED" = "Y" ]; then
    echo ""
    echo -e "${BLUE}Test de la connexion OneDrive...${NC}"

    if rclone lsd onedrive: &> /dev/null; then
        echo -e "${GREEN}✓${NC} Connexion OneDrive OK"
        echo ""
        echo "Dossiers disponibles:"
        rclone lsd onedrive: | head -10
    else
        echo -e "${RED}✗${NC} Impossible de se connecter à OneDrive"
        echo "Vérifie ta configuration avec: rclone config"
        exit 1
    fi

    # Vérifier que le dossier Calibre existe
    echo ""
    echo -e "${BLUE}Vérification du dossier Calibre...${NC}"

    if rclone lsd "onedrive:Calibre" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Dossier Calibre trouvé"

        if rclone lsd "onedrive:Calibre/Calibre Library" &> /dev/null; then
            echo -e "${GREEN}✓${NC} Calibre Library trouvé"
        else
            echo -e "${RED}✗${NC} Calibre Library introuvable"
            echo "Chemins disponibles:"
            rclone lsd "onedrive:Calibre"
        fi
    else
        echo -e "${RED}✗${NC} Dossier Calibre introuvable"
        echo "Chemins disponibles:"
        rclone lsd "onedrive:" | head -10
    fi

    # Installer le script de sync dans crontab
    echo ""
    read -p "Installer le script de sync automatique ? (y/n): " INSTALL_CRON

    if [ "$INSTALL_CRON" = "y" ] || [ "$INSTALL_CRON" = "Y" ]; then
        SCRIPT_PATH="$HOME/scripts/sync-calibre-onedrive.sh"

        # Créer cron job (toutes les heures)
        CRON_JOB="0 * * * * $SCRIPT_PATH >> $HOME/logs/calibre-sync-cron.log 2>&1"

        (crontab -l 2>/dev/null | grep -v "sync-calibre-onedrive.sh"; echo "$CRON_JOB") | crontab -

        echo -e "${GREEN}✓${NC} Cron job installé (sync toutes les heures)"
        echo "Voir les logs: tail -f $HOME/logs/calibre-sync-cron.log"
    fi

    # Proposer un premier sync
    echo ""
    read -p "Lancer un premier sync maintenant ? (y/n): " RUN_SYNC

    if [ "$RUN_SYNC" = "y" ] || [ "$RUN_SYNC" = "Y" ]; then
        bash ~/scripts/sync-calibre-onedrive.sh
    fi

    echo ""
    echo -e "${GREEN}✓${NC} Setup terminé !"
    echo ""
    echo "Commandes utiles:"
    echo "  - Sync manuel: bash ~/scripts/sync-calibre-onedrive.sh"
    echo "  - Test OneDrive: rclone lsd onedrive:"
    echo "  - Voir logs: tail -f ~/logs/calibre-sync.log"
else
    echo ""
    echo -e "${YELLOW}Configuration rclone nécessaire${NC}"
    echo "Suis les étapes ci-dessus puis relance ce script"
fi
