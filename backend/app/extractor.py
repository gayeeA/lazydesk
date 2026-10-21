from pathlib import Path
TEXT = {".txt",".md",".csv",".json",".py",".js",".ts",".tsx",".html",".css",".java",".c",".cpp",".yml",".yaml",".toml"}
IMAGES = {".png",".jpg",".jpeg",".gif",".webp",".bmp"}
def extract(path: Path, limit: int = 3000) -> dict:
    ext = path.suffix.lower()
    info = {"ext": ext, "size": path.stat().st_size, "text": "", "kind": "other"}
    try:
        if ext in TEXT:
            info["kind"] = "text"
            info["text"] = path.read_text(errors="ignore")[:limit]
        elif ext == ".pdf":
            from pypdf import PdfReader
            info["kind"] = "pdf"
            r = PdfReader(str(path))
            info["text"] = "\n".join((p.extract_text() or "") for p in r.pages[:3])[:limit]
        elif ext == ".docx":
            from docx import Document
            info["kind"] = "docx"
            info["text"] = "\n".join(p.text for p in Document(str(path)).paragraphs)[:limit]
        elif ext in IMAGES:
            info["kind"] = "image"  # metadata only: no OCR in MVP
    except Exception as e:
        info["error"] = f"extract failed: {e}"
    return info
