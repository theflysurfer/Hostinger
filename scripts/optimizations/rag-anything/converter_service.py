"""
Document Converter Microservice
Converts Office documents using LibreOffice
"""

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import tempfile
from pathlib import Path

app = FastAPI(title="Document Converter Service")

SUPPORTED_FORMATS = {'.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp'}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "document-converter"}

@app.post("/convert/to-pdf")
async def convert_to_pdf(file: UploadFile):
    """Convert Office document to PDF"""

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {file_ext}. Supported: {SUPPORTED_FORMATS}"
        )

    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        input_path = Path(temp_dir) / file.filename
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Convert to PDF using LibreOffice
        try:
            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", temp_dir,
                str(input_path)
            ], check=True, capture_output=True, timeout=60)

            # Get output PDF path
            pdf_filename = input_path.stem + ".pdf"
            pdf_path = Path(temp_dir) / pdf_filename

            if not pdf_path.exists():
                raise HTTPException(status_code=500, detail="Conversion failed")

            # Return PDF file
            return FileResponse(
                path=str(pdf_path),
                media_type="application/pdf",
                filename=pdf_filename
            )

        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="Conversion timeout")
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Conversion error: {e.stderr}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9511)
