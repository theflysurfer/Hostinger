# Apache Tika - Parsing de Documents

## Vue d'ensemble

Apache Tika est un service de parsing de documents universel supportant plus de 1000 formats de fichiers.

## Accès

- **API**: https://tika.srv759970.hstgr.cloud
- **Port**: 9998

## Formats supportés

- **Documents**: PDF, DOC, DOCX, ODT, RTF
- **Feuilles de calcul**: XLS, XLSX, ODS, CSV
- **Présentations**: PPT, PPTX, ODP
- **Images**: JPEG, PNG, TIFF, BMP (avec OCR)
- **Archives**: ZIP, TAR, 7Z, RAR
- **Audio/Vidéo**: MP3, MP4, AVI, MKV
- **Emails**: MSG, EML, MBOX

## Endpoints

### POST /tika
Parse un document et retourne le texte brut.

**Exemple:**
```bash
curl -X PUT https://tika.srv759970.hstgr.cloud/tika   --upload-file document.pdf   -H "Accept: text/plain"
```

### POST /meta
Extrait les métadonnées d'un fichier.

**Exemple:**
```bash
curl -X PUT https://tika.srv759970.hstgr.cloud/meta   --upload-file photo.jpg   -H "Accept: application/json"
```

### POST /detect/stream
Détecte le type MIME d'un fichier.

## Configuration

- **Version**: Apache Tika 3.2.3
- **OCR**: Tesseract intégré
- **Langues OCR**: Français, Anglais, Espagnol, etc.
- **Taille max**: 100 MB par fichier

## Cas d'usage

1. **Indexation de documents**: Extraire le texte pour recherche full-text
2. **OCR automatique**: Scanner des images contenant du texte
3. **Extraction de métadonnées**: EXIF, auteur, date de création
4. **Conversion de formats**: Normaliser différents formats en texte

## Ressources

- [Documentation Apache Tika](https://tika.apache.org/)
