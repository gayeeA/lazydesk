import re, shutil
from pathlib import Path
from .schemas import CATEGORIES
WORKSPACE = Path(__file__).resolve().parents[2] / "workspace"
INBOX = WORKSPACE / "inbox"
ORGANIZED = WORKSPACE / "organized"
for p in (INBOX, ORGANIZED): p.mkdir(parents=True, exist_ok=True)
def sanitize(name: str, ext: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9._ -]", "", stem).strip(" .")[:80].replace(" ", "_") or "file"
    return stem + ext.lower()
def unique(dest: Path) -> Path:
    if not dest.exists(): return dest
    i = 2
    while (c := dest.with_name(f"{dest.stem}_{i}{dest.suffix}")).exists(): i += 1
    return c
def move_approved(src_id: str, category: str, filename: str) -> str:
    if category not in CATEGORIES: raise ValueError("bad category")
    src = (INBOX / src_id).resolve()
    if src.parent != INBOX.resolve() or not src.is_file(): raise ValueError("file not in workspace")
    folder = ORGANIZED / category; folder.mkdir(exist_ok=True)
    dest = unique(folder / sanitize(filename, src.suffix))
    shutil.move(str(src), str(dest))  # move only, never overwrite
    return str(dest.relative_to(WORKSPACE))
