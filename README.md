# LazyDesk 🛋️ Drop it. Forget it.

A local-first AI file organizer. Drop messy files in; an open-weight model running on your machine classifies them, proposes clean filenames, and, after you approve, moves them into category folders.

## Problem
Downloads and Desktop fill up with resumes, certificates, notes and scans. Renaming and sorting them is boring, so people postpone it.

## Solution
LazyDesk extracts text from each file, asks a local model (Gemma via Ollama by default) for structured JSON, shows the proposed actions, and organizes only what you approve.

## Why open-weight / local AI?
Files can be private. The model runs on your machine through Ollama, so LazyDesk makes no cloud AI calls. Tradeoffs: it needs capable hardware and can be slower than a hosted API. This removes a third-party AI service from the loop; it does not make the whole workflow "absolutely private".

## How it works
React UI → FastAPI → extractor (text/PDF/DOCX) → Ollama (Gemma) → JSON {category, suggested_filename, summary, confidence, reason} → confidence check → your approval → organizer → `backend/workspace/organized/<Category>/`

## Run locally
```bash
# 1. Model
ollama pull gemma3:4b          # or set LAZYDESK_MODEL to another model you have
# 2. Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
# 3. Frontend (new terminal)
cd frontend && npm install && npm run dev    # http://localhost:5173
```
Config via environment variables (see `.env.example`): `OLLAMA_URL`, `LAZYDESK_MODEL`, `LAZYDESK_CONFIDENCE_THRESHOLD`. Try it with the harmless sample files in `demo/messy/`.

## Supported files
Text/code (`.txt .md .csv .json .py .js .ts .tsx .html .css ...`), `.pdf` (first 3 pages), `.docx`. Images are classified by name/type only (no OCR). Other types go to review.

## Safety
- All file operations stay inside `backend/workspace/`; the model never supplies paths.
- Filenames are sanitized; duplicates get `_2`, `_3`; nothing is overwritten.
- Files move only after you approve. Confidence below 0.75, invalid JSON, or an unreachable model means "Needs Review", unapproved by default.
- Fixed categories: Documents, Certificates, Resumes, Projects, Notes, Images, Other.

## Limitations
- Quality depends on the model you run; small models can misclassify.
- Uploads are copied into the workspace; your originals are never moved or deleted.
- No OCR, authentication, or saved history.
- The Gemma/Ollama path has not been run end-to-end by the author yet. Measure your own accuracy and timing before publishing any numbers.

## Future work
OCR for screenshots, duplicate detection, watched inbox folder, undo.
