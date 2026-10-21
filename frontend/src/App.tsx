import { useState, useRef } from "react";
const API = "http://localhost:8000";
const CATS = ["Documents","Certificates","Resumes","Projects","Notes","Images","Other"];
type Item = { id:string; original:string; category:string; suggested_filename:string; summary:string;
  confidence:number; reason:string; ai_ok:boolean; needs_review:boolean; seconds:number;
  status:"Ready"|"Needs Review"|"Organized"|"Error"; approved:boolean; finalPath?:string };
export default function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [total, setTotal] = useState<number|null>(null);
  const [drag, setDrag] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  async function analyze(files: FileList | File[]) {
    const list = Array.from(files); if (!list.length) return;
    setBusy(true); setErr("");
    const t = performance.now();
    const fd = new FormData(); list.forEach(f => fd.append("files", f));
    try {
      const r = await fetch(`${API}/analyze`, { method:"POST", body: fd });
      if (!r.ok) throw new Error(`Server returned ${r.status}`);
      const d = await r.json();
      setItems(d.results.map((x:any) => ({ ...x, status: x.needs_review ? "Needs Review" : "Ready", approved: !x.needs_review })));
      setTotal((performance.now() - t) / 1000);
    } catch (e:any) { setErr(`Could not reach the LazyDesk backend at ${API}. Start it with uvicorn. (${e.message})`); }
    setBusy(false);
  }
  const upd = (id:string, p:Partial<Item>) => setItems(a => a.map(i => i.id===id ? {...i, ...p} : i));
  async function approve() {
    const chosen = items.filter(i => i.approved && i.status !== "Organized");
    const r = await fetch(`${API}/approve`, { method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ items: chosen.map(i => ({ id:i.id, category:i.category, filename:i.suggested_filename })) }) });
    const d = await r.json();
    d.results.forEach((x:any) => upd(x.id, x.ok ? { status:"Organized", finalPath:x.path } : { status:"Error", reason:x.error }));
  }
  const auto = items.filter(i => !i.needs_review).length;
  const review = items.length - auto;
  const done = items.filter(i => i.status==="Organized").length;
  return (<main>
    <header><h1>LazyDesk 🛋️</h1><p className="tag">Drop it. Forget it.</p></header>
    <div className={"drop"+(drag?" over":"")} tabIndex={0} onClick={()=>input.current?.click()}
      onKeyDown={e=>e.key==="Enter" && input.current?.click()}
      onDragOver={e=>{e.preventDefault();setDrag(true)}} onDragLeave={()=>setDrag(false)}
      onDrop={e=>{e.preventDefault();setDrag(false);analyze(e.dataTransfer.files)}}>
      <input ref={input} type="file" multiple hidden onChange={e=>e.target.files && analyze(e.target.files)} />
      <strong>{busy ? "Analyzing with your local model…" : "Drop your messy files here"}</strong>
      <span>Files are read by a model running on this machine. LazyDesk makes no cloud AI calls.</span>
    </div>
    {err && <p className="err" role="alert">{err}</p>}
    {items.length>0 && <>
      <p className="summary">You gave LazyDesk {items.length} file{items.length>1?"s":""}. It prepared {auto} automatically and flagged {review} for review
        {total!==null && <> (analysis took {total.toFixed(1)}s)</>}. {done>0 && <b>{done} organized.</b>}</p>
      <ul className="list">{items.map(i => (<li key={i.id} className={"card "+i.status.replace(" ","")}>
        <div className="row"><span className="from">{i.original}</span><span className="arrow">becomes</span>
          <span className="to">{i.category}/{i.suggested_filename}</span><span className="badge">{i.status}</span></div>
        <p className="sum">{i.summary || i.reason}</p>
        <p className="meta">Confidence {(i.confidence*100).toFixed(0)}%{i.ai_ok ? " · " + i.reason : ""}</p>
        {i.status!=="Organized" && <div className="edit">
          <select value={i.category} onChange={e=>upd(i.id,{category:e.target.value})}>{CATS.map(c=><option key={c}>{c}</option>)}</select>
          <input value={i.suggested_filename} onChange={e=>upd(i.id,{suggested_filename:e.target.value})} aria-label="Filename"/>
          <label><input type="checkbox" checked={i.approved} onChange={e=>upd(i.id,{approved:e.target.checked})}/> Approve</label>
        </div>}
        {i.finalPath && <p className="meta">Moved to workspace/{i.finalPath}</p>}
      </li>))}</ul>
      <button className="go" onClick={approve} disabled={!items.some(i=>i.approved && i.status!=="Organized")}>Organize approved files</button>
    </>}
  </main>);
}
