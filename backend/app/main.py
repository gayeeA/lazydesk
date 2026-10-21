import time, uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from . import ai, organizer
from .extractor import extract
from .schemas import ApproveRequest, CATEGORIES
app = FastAPI(title="LazyDesk")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
@app.get("/health")
def health(): return {"ok": True, "model": ai.MODEL, "categories": CATEGORIES}
@app.post("/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    out = []
    for f in files:
        orig = Path(f.filename or "file").name
        fid = f"{uuid.uuid4().hex[:8]}_{organizer.sanitize(orig, Path(orig).suffix)}"
        path = organizer.INBOX / fid
        path.write_bytes(await f.read())
        t = time.time()
        info = extract(path)
        r = ai.classify(orig, info)
        r["suggested_filename"] = organizer.sanitize(r["suggested_filename"] or orig, path.suffix)
        needs = (not r["ai_ok"]) or r["confidence"] < ai.THRESH
        out.append({"id": fid, "original": orig, **r, "needs_review": needs,
                    "seconds": round(time.time() - t, 2), "extract_error": info.get("error")})
    return {"model": ai.MODEL, "threshold": ai.THRESH, "results": out}
@app.post("/approve")
def approve(req: ApproveRequest):
    res = []
    for it in req.items:
        try:
            res.append({"id": it.id, "ok": True, "path": organizer.move_approved(it.id, it.category, it.filename)})
        except Exception as e:
            res.append({"id": it.id, "ok": False, "error": str(e)})
    return {"results": res}
