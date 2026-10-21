import json, os, httpx
from dotenv import load_dotenv
from .schemas import CATEGORIES

load_dotenv()
URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("LAZYDESK_MODEL", "gemma3:1b")
THRESH = float(os.getenv("LAZYDESK_CONFIDENCE_THRESHOLD", "0.75"))
NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "0"))
PROMPT = """You organize files. Classify the file into exactly one category from: {cats}.
Return ONLY JSON: {{"category":"","suggested_filename":"","summary":"","confidence":0.0,"reason":""}}
suggested_filename: short, descriptive, Words_With_Underscores, keep the original extension {ext}.
confidence: 0 to 1, be honest; use low values when content is unclear.
File name: {name}
File type: {ext}, {size} bytes
Content excerpt:
{text}"""
def _fallback(reason):
    return {"category":"Other","suggested_filename":None,"summary":"","confidence":0.0,"reason":reason,"ai_ok":False}
def classify(name: str, info: dict) -> dict:
    text = info["text"] or "(no extractable text; judge by name/type only)"
    prompt = PROMPT.format(cats=", ".join(CATEGORIES), ext=info["ext"], name=name, size=info["size"], text=text)
    try:
        options = {"temperature": 0.1, "num_gpu": NUM_GPU}
        r = httpx.post(f"{URL}/api/chat", timeout=120, json={
            "model": MODEL, "stream": False, "format": "json", "options": options,
            "messages": [{"role":"user","content":prompt}]})
        r.raise_for_status()
        d = json.loads(r.json()["message"]["content"])
        cat = d.get("category")
        conf = float(d.get("confidence", 0))
        if cat not in CATEGORIES:
            return _fallback(f"Model returned invalid category: {cat!r}")
        return {"category":cat,"suggested_filename":str(d.get("suggested_filename") or name),
                "summary":str(d.get("summary","")),"confidence":max(0.0,min(1.0,conf)),
                "reason":str(d.get("reason","")),"ai_ok":True}
    except httpx.HTTPError as e:
        return _fallback(f"Local model unreachable ({type(e).__name__}). Is Ollama running with '{MODEL}' pulled?")
    except (ValueError, KeyError, TypeError) as e:
        return _fallback(f"Model returned invalid JSON ({type(e).__name__})")
