import hashlib
import json
import fitz
from config import FRAGMENTS_PATH


class PDFReader:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.fragments = []

    def extract(self):
        doc = fitz.open(self.pdf_path)
        self.fragments = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                fragment_id = f"frag-{page_num + 1:03d}"
                h = hashlib.sha256(text.encode()).hexdigest()[:12]
                self.fragments.append({
                    "fragment_id": fragment_id,
                    "pagina": page_num + 1,
                    "texto": text,
                    "hash": h,
                    "seccion": self._detect_section(text),
                })
        doc.close()
        return self.fragments

    def _detect_section(self, text: str) -> str:
        lines = text.strip().split("\n")
        for line in lines[:5]:
            line = line.strip().lower()
            if "hecho" in line or "relato" in line:
                return "hechos"
            if "prueba" in line or "documento" in line:
                return "pruebas"
            if "norma" in line or "ley" in line or "código" in line or "artículo" in line:
                return "normas"
            if "demanda" in line or "pretensión" in line:
                return "pretensiones"
            if "excepción" in line or "defensa" in line:
                return "excepciones"
        return "general"

    def save_fragments(self):
        with open(FRAGMENTS_PATH, "w", encoding="utf-8") as f:
            for frag in self.fragments:
                f.write(json.dumps(frag, ensure_ascii=False) + "\n")
        return self.fragments

    def get_full_text(self) -> str:
        return "\n\n".join(f["texto"] for f in self.fragments)
