# ingestion/pdf_parser.py
import fitz  # PyMuPDF
import tempfile
import urllib.request
import os

def extract_text_from_url(pdf_url: str) -> str:
    """Download a PDF from a URL and extract its text."""
    try:
        # arXiv links sometimes need a direct pdf extension, but usually it works directly.
        req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            pdf_bytes = response.read()
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
            
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
            
        doc.close()
        os.remove(tmp_path)
        return text
    except Exception as e:
        print(f"[pdf_parser] Error downloading or parsing PDF {pdf_url}: {e}")
        return ""
