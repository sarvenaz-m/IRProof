import {icon} from './icons.mjs';
import {escapeHTML, drawGraph} from './graphs.mjs';
import {parseInteger, roundingSample, plotRounding} from './math.mjs';

const evidence = window.IRPROOF_EVIDENCE;
const app = document.querySelector('#app');
if (!evidence?.cases?.length) {
  app.innerHTML = '<main class="page"><h1>IRProof</h1><p>The evidence bundle is missing. Export a completed run with scripts/export_demo.py.</p></main>';
  throw new Error('Missing IRProof evidence bundle');
}
const labels = {proved:'Proved', refuted:'Refuted', unknown:'Unknown', error:'Tool error', not_run:'Not run'};
const categories = {signed:'Signed arithmetic', unsigned:'Unsigned arithmetic', overflow:'Flags & overflow', semantics:'Definedness & refinement', limits:'Model boundaries', frontend:'Generated IR'};
const initial = new URLSearchParams(location.hash.slice(1));
const state = {
  route:['verification','graphs','notes'].includes(initial.get('view')) ? initial.get('view') : 'verification',
  selected:evidence.cases.some(c=>c.id===initial.get('case')) ? initial.get('case') : 'sdiv-32-8',
  tab:'comparison', filter:'all', search:'', graph:'diamond', graphMode:'cfg', node:'', rail:false,
  labX:'-3', labWidth:32, labDivisor:2
};
if (!evidence.cases.some(c=>c.id===state.selected)) state.selected = evidence.cases[0].id;
const current = () => evidence.cases.find(c=>c.id===state.selected);
const e = escapeHTML;
const short = s => String(s || '').slice(0,12);
const goodVersion = evidence.tools?.opt?.version?.match(/LLVM version ([^\s]+)/)?.[1] || 'recorded';
const date = new Date(evidence.generatedAt).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'});
const count = status => evidence.cases.filter(c=>c.status===status).length;

function pill(status) { return `<span class="status-pill ${e(status)}">${icon(status==='proved'?'check':status==='refuted'?'close':'clock',12)}${labels[status] || status}</span>`; }
function shell() {
  app.innerHTML = `<div class="layout">
    <aside class="rail ${state.rail?'open':''}" aria-label="Workspace navigation">
      <div class="brand"><div class="brand-mark"><svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 7v22m0-11h16m-7-11 8 11-8 11"/></svg></div><span class="brand-name">IRProof<span>.</span></span></div>
      <div class="eyebrow nav-heading">Workbench</div>
      <nav>${[['verification','proof','Verification',String(evidence.cases.length)],['graphs','graph','Graph inspector',''],['notes','book','Method notes','']].map(([route,ico,title,n])=>`<button data-route="${route}" class="nav-item ${state.route===route?'active':''}" ${state.route===route?'aria-current="page"':''} aria-label="${title}">${icon(ico)}<span class="nav-text">${title}</span><span class="nav-count">${n}</span></button>`).join('')}</nav>
      <div class="rail-card"><div class="circle">${icon('shield',15)}</div><strong>Every verdict has a trail.</strong><p>Source, target, tool output and hashes travel together.</p></div>
      <div class="rail-footer"><span class="version">v1.0.0</span><div>Integer Rewrite Workbench</div><div>C++20 · LLVM · Alive2</div></div>
    </aside>
    <div class="workspace"><header class="topbar"><div style="display:flex;gap:11px;align-items:center"><button class="icon-button mobile-menu" data-action="menu" aria-label="Toggle navigation">${icon('menu',15)}</button><div class="breadcrumb">WORKSPACE <span>/</span> <b>${state.route==='verification'?'INTEGER REWRITES':state.route==='graphs'?'IR STRUCTURE':'METHOD NOTES'}</b></div></div><div class="top-actions"><span class="capture-label"><span class="live-dot"></span>Captured run · ${e(date)}</span><button class="outline" data-action="export">${icon('download',13)} Export evidence</button></div></header>
    <main class="page" id="main-content">${state.route==='verification'?verification():state.route==='graphs'?graphPage():notesPage()}</main></div></div><div id="toast" role="status" aria-live="polite"></div>`;
  bindLab();
  persist();
}
function persist() {
  try { history.replaceState(null,'',`#view=${state.route}&case=${encodeURIComponent(state.selected)}`); } catch {}
}
function verification() {
  return `<section class="hero"><div><div class="eyebrow">A closer look at compiler correctness</div><h1>Small rewrites. Precise reasoning.</h1><p>Follow an integer transformation from LLVM IR to a checked result. Inspect the details that make it hold.</p></div><button class="primary" data-action="counterexample">Open a counterexample ${icon('arrow',15)}</button></section>
    <section class="stats" aria-label="Recorded validation results">
    ${[[null,'code',evidence.cases.length,'Cases in this run','Original + upstream'],['proved','check',count('proved'),'Refinements proved','Alive2'],['refuted','close',count('refuted'),'Counterexamples found','Expected negatives'],['unknown','clock',count('unknown'),'Unresolved checks','Kept separate']].map(([s,ico,n,label,note])=>`<div class="stat ${s||''}"><div class="stat-icon">${icon(ico,18)}</div><div><div class="stat-number">${n.toString().padStart(2,'0')}</div><div class="stat-caption">${label}</div></div><span class="stat-note">${note}</span></div>`).join('')}</section>
    ${(count('error')||count('not_run'))?`<p class="capture-note">${count('error')} tool errors and ${count('not_run')} unexecuted checks are excluded from the proof counts. Use the case filters to inspect them.</p>`:''}
    <section class="bench" aria-label="Transformation workbench"><aside class="corpus"><div class="corpus-head"><h2 class="panel-title">Transformation library</h2><p class="panel-kicker">${evidence.cases.length} recorded cases / ${evidence.version}</p><label class="search-box">${icon('search',13)}<input id="case-search" aria-label="Search transformations" placeholder="Find a transformation…" value="${e(state.search)}"></label><div class="filter-row" role="group" aria-label="Filter cases">${['all','proved','refuted','unknown',...(count('error')?['error']:[]),...(count('not_run')?['not_run']:[])].map(s=>`<button class="filter ${state.filter===s?'active':''}" data-filter="${s}" aria-pressed="${state.filter===s}">${s==='all'?'All':labels[s]}</button>`).join('')}</div></div><div class="case-list" id="case-list">${caseList()}</div></aside><article class="case-detail" id="case-detail">${detail()}</article></section>
    <section class="lower-grid"><article class="card"><div class="card-top"><h2 class="panel-title">The rounding lab</h2><span class="small-tag">Concrete values</span></div>${lab()}</article><article class="card"><div class="card-top"><h2 class="panel-title">From rewrite to evidence</h2><span class="small-tag">LLVM ${e(goodVersion)}</span></div>${pipeline()}</article></section>${footer()}`;
}
function caseList() {
  const visible = evidence.cases.filter(c=>(state.filter==='all'||c.status===state.filter) && `${c.title} ${c.id} ${c.explanation}`.toLowerCase().includes(state.search.toLowerCase()));
  if (!visible.length) return '<p class="empty">No matching transformations.</p>';
  let previous='';
  return visible.map(c=>{
    const group=c.category!==previous?`<div class="case-group">${categories[c.category]||e(c.category)}</div>`:''; previous=c.category;
    return `${group}<button class="case-row ${c.id===state.selected?'active':''}" data-case="${e(c.id)}" aria-pressed="${c.id===state.selected}"><span class="status-dot ${e(c.status)}" title="${labels[c.status]}"></span><div><div class="case-title">${e(c.title)}</div><div class="case-meta">${e(c.origin?.kind==='upstream'?'Alive2 regression':c.mode==='pass'?'C++ pass → Alive2':'Source / target pair')}</div></div><span class="case-index">${String(evidence.cases.indexOf(c)+1).padStart(2,'0')}</span></button>`;
  }).join('');
}
function codePanel(title, code, target=false) {
  const lines=code.split('\n');
  const source=current().sourceIR||'';
  const highlight=line=>{
    const tokens=line.match(/;.*|%[\w.]+|@[\w.]+|\b(?:define|ret|sdiv|udiv|srem|urem|ashr|lshr|shl|and|add|mul|sub|xor|or|freeze|nsw|nuw|exact|noundef|br|phi|icmp|call|atomicrmw|seq_cst)\b|\bi\d+\b|\b-?\d+\b|[^\s]+|\s+/g)||[];
    return tokens.map(t=>{
      let c=t.startsWith(';')?'syntax-comment':/^[%@]/.test(t)?'syntax-value':/^i\d+$/.test(t)?'syntax-type':/^-?\d+$/.test(t)?'syntax-num':/^(define|ret|sdiv|udiv|srem|urem|ashr|lshr|shl|and|add|mul|sub|xor|or|freeze|nsw|nuw|exact|br|phi|icmp|call|atomicrmw)$/.test(t)?'syntax-op':'';
      return c?`<span class="${c}">${e(t)}</span>`:e(t);
    }).join('');
  };
  return `<div class="code-panel"><div class="code-toolbar"><span class="code-title"><b>${title}</b> · ${target?'target.ll':'source.ll'}</span><button class="code-copy" data-copy="${target?'target':'source'}" aria-label="Copy ${target?'target':'source'} IR">${icon('copy',12)}</button></div><pre tabindex="0" aria-label="${title} LLVM IR">${lines.map((line,i)=>`<span class="code-line ${target && line.trim() && !source.includes(line.trim())?'changed':''}"><span class="line-num">${i+1}</span><span class="code-text">${highlight(line)}</span></span>`).join('')}</pre></div>`;
}
function detail() {
  const c=current();
  return `<header class="detail-head"><div><div class="eyebrow">${categories[c.category]||'Transformation'}</div><h2>${e(c.title)}</h2><div class="detail-meta"><span>${c.mode==='pass'?'irproof-strength':'src → tgt'}</span><span>·</span><span>${e(c.bits)}-bit specimen</span><span>·</span><span>${c.durationMs==null?'No timing':c.durationMs.toFixed(0)+' ms'}</span></div></div>${pill(c.status)}</header><div class="tabs" role="tablist" aria-label="Case details">${[['comparison','code','IR comparison'],['raw','proof','Validator output'],['provenance','shield','Provenance']].map(([s,ico,title])=>`<button role="tab" class="tab ${state.tab===s?'active':''}" data-tab="${s}" aria-selected="${state.tab===s}" aria-controls="case-tab-content">${icon(ico,13)}${title}</button>`).join('')}</div><div class="tab-content" id="case-tab-content" role="tabpanel">${state.tab==='comparison'?comparison(c):state.tab==='raw'?rawTab(c):provenanceTab(c)}</div>`;
}
function comparison(c) {
  const titles={proved:'The target refines the source.',refuted:'This rewrite changes the contract.',unknown:'This check remains unresolved.',error:'The tool did not finish a valid check.',not_run:'This pair has not been checked.'};
  return `<div class="code-grid">${codePanel('Before',c.sourceIR||'')}${codePanel('After',c.targetIR||'',true)}</div><div class="verdict-box ${e(c.status)}"><div class="verdict-symbol">${icon(c.status==='proved'?'check':c.status==='refuted'?'close':'clock',14)}</div><div><div class="verdict-title">${titles[c.status]}</div><div class="verdict-text">${e(c.explanation)} ${c.status==='unknown'?e(c.reason):''}</div></div></div><div class="evidence-strip">${icon('shield',13)} <span>SHA-256</span><code>${short(c.evidenceSha256)}…</code><span>·</span><span>${e(c.mode==='pass'?'LLVM pass output validated':'Explicit source / target checked')}</span><button class="text-link" data-tab="raw">Inspect the output ${icon('arrow',11)}</button></div><div class="proof-method"><span>Captured tool result · source-to-target refinement</span><span>All-input check within Alive2’s model and bounds</span></div>`;
}
function rawTab(c) {
  return `<p class="capture-note">${e(c.reason)} The output below was captured by the local runner. Opening this panel does not rerun LLVM or the solver.</p><div class="terminal"><div class="terminal-head"><i></i><i></i><i></i><span>alive-tv · ${e(c.id)}</span></div>${e(c.rawOutput||'No validator output was captured for this case.')}</div><div style="display:flex;justify-content:flex-end;margin-top:13px"><button class="outline" data-action="download-case">${icon('download',12)} Download case record</button></div>`;
}
function provenanceTab(c) {
  const revision=c.origin?.revision;
  return `<p class="capture-note">Each captured result is tied to its original input and output files. The full package retains commands, exit codes, elapsed times and stdout/stderr.</p><table class="hash-table"><tbody>${[
    ['Origin',e(c.origin?.name)],['Original input',`<code>${e(c.path)}</code>`],['Original SHA-256',`<code>${e(c.inputSha256)}</code>`],['Checked source SHA-256',`<code>${e(c.sourceSha256)}</code>`],
    ...(c.targetSha256?[['Checked target SHA-256',`<code>${e(c.targetSha256)}</code>`]]:[]),['Evidence SHA-256',`<code>${e(c.evidenceSha256)}</code>`],
    ['LLVM',`<code>${e(evidence.tools?.opt?.version)}</code>`],['Alive2 revision',`<code>${e(evidence.toolchain?.alive2?.revision||'See toolchain.lock.json')}</code>`],
    ['Solver',`<code>${e(evidence.toolchain?.z3?.version||'See toolchain.lock.json')}</code>`],['Budget',`${e(evidence.timeoutSeconds)} seconds per check`],
    ...(revision?[['Upstream revision',`<code>${e(revision)}</code>`]]:[]),...(c.url?[['Original regression',`<a href="${e(c.url)}" target="_blank" rel="noreferrer">View pinned upstream file ${icon('external',11)}</a>`]]:[])
  ].map(([a,b])=>`<tr><td>${a}</td><td>${b}</td></tr>`).join('')}</tbody></table>`;
}
function lab() {
  return `<form id="lab-form"><div class="lab-form"><label><span class="field-label">Signed input</span><input id="lab-x" inputmode="numeric" value="${e(state.labX)}" autocomplete="off" spellcheck="false"></label><label><span class="field-label">Divisor</span><select id="lab-divisor">${[2,4,8,16,64].map(d=>`<option ${state.labDivisor===d?'selected':''}>${d}</option>`).join('')}</select></label><label><span class="field-label">Integer width</span><select id="lab-width">${[8,16,32,64,128].map(w=>`<option value="${w}" ${state.labWidth===w?'selected':''}>i${w}</option>`).join('')}</select></label></div><div class="presets">${[-128,-9,-3,-1,0,1,7,127].map(n=>`<button type="button" class="preset ${state.labX===String(n)?'active':''}" data-preset="${n}">${n}</button>`).join('')}</div><div id="lab-result" aria-live="polite"></div></form>`;
}
function bindLab() {
  if (!document.querySelector('#lab-form')) return;
  const update=()=>{
    state.labX=document.querySelector('#lab-x').value;
    state.labDivisor=Number(document.querySelector('#lab-divisor').value);
    state.labWidth=Number(document.querySelector('#lab-width').value);
    document.querySelectorAll('[data-preset]').forEach(el=>el.classList.toggle('active',el.dataset.preset===state.labX));
    const area=document.querySelector('#lab-result');
    try {
      const x=parseInteger(state.labX,state.labWidth), r=roundingSample(x,state.labDivisor,state.labWidth), bad=r.source!==r.naive;
      area.innerHTML=`<div class="lab-results"><div class="lab-value"><span>sdiv · source</span><strong>${r.source}</strong></div><div class="lab-value ${bad?'bad':''}"><span>ashr · naive shift</span><strong>${r.naive}</strong></div><div class="lab-value"><span>bias + ashr · corrected</span><strong>${r.corrected}</strong></div></div><p class="lab-foot">${bad?`The naive shift differs. A bias of ${r.bias} restores rounding toward zero.`:'These concrete results agree. One input alone does not establish refinement.'}</p>${plotRounding(state.labDivisor,state.labWidth)}<div class="plot-legend"><span><i class="legend-line"></i>Signed division</span><span><i class="legend-line naive"></i>Naive shift</span></div><p class="lab-foot">Exact integer arithmetic in this browser. This illustration does not model undef, poison or memory and does not call Alive2.</p>`;
    } catch(err) { area.innerHTML=`<p class="lab-error">${e(err.message)}</p>`; }
  };
  document.querySelector('#lab-form').addEventListener('submit',event=>event.preventDefault());
  for (const id of ['lab-x','lab-divisor','lab-width']) document.querySelector('#'+id).addEventListener('input',update);
  update();
}
function pipeline() {
  return [['01','Produce and inspect IR','A small C++ frontend constructs branches, PHI nodes and a loop. The audit pass records control flow and SSA dependencies.'],['02','Apply a focused C++ pass','Scalar power-of-two rewrites preserve the relevant flags. Signed division uses a rounding correction and a stable operand.'],['03','Check source against target','Alive2 checks the exact pair. Counterexamples, unsupported semantics and incomplete runs receive separate verdicts.'],['04','Keep the evidence','Input hashes, raw output and the toolchain revision accompany each result.']].map(([n,title,text])=>`<div class="pipeline-step"><div class="step-num">${n}</div><div><strong>${title}</strong><p>${text}</p></div></div>`).join('');
}
function graphPage() {
  return `<section class="hero"><div><div class="eyebrow">Inside the IR</div><h1>Structure you can inspect.</h1><p>Control flow, immediate dominators, loop depth and SSA dependencies recorded by the C++ audit pass.</p></div><span class="small-tag">Read-only analysis · CFG preserved</span></section><article class="card"><div class="graph-controls"><label class="sr-only" for="graph-scenario">IR specimen</label><select id="graph-scenario">${Object.keys(evidence.audits||{}).map(k=>`<option value="${e(k)}" ${state.graph===k?'selected':''}>${k==='diamond'?'Branch + PHI':k==='loop'?'Loop + accumulator':'Signed division'}</option>`).join('')}</select><div class="segmented" role="group" aria-label="Graph type"><button class="segment ${state.graphMode==='cfg'?'active':''}" data-graph-mode="cfg">Control flow</button><button class="segment ${state.graphMode==='dataflow'?'active':''}" data-graph-mode="dataflow">Data dependencies</button></div><span class="small-tag" style="margin-left:auto">LLVM analysis output</span></div><div id="graph-area">${graphContent()}</div></article><div class="notes-grid"><article class="card"><h2 class="panel-title">What is measured</h2><p class="capture-note" style="margin-top:12px">Edges and instructions come from the recorded LLVM analysis. Layout is computed in the browser. Click a node to inspect its IR.</p></article><article class="card"><h2 class="panel-title">Why the branch matters</h2><p class="capture-note" style="margin-top:12px">In the nonnegative arm, the dominating comparison can justify a logical shift. The negative arm still needs the signed rounding correction.</p></article></div>${footer()}`;
}
function graphContent() {
  const audit=evidence.audits?.[state.graph], func=audit?.functions?.[0];
  if (!func) return '<p class="empty">No captured audit for this specimen.</p>';
  const block=func.blocks.find(b=>b.id===state.node||b.instructions.some(i=>i.id===state.node));
  const ins=block?.instructions.find(i=>i.id===state.node);
  return `<div class="graph-surface">${drawGraph(func,state.graphMode,state.node)}</div><div class="graph-info"><b>${e(func.name)}</b> · ${func.blocks.length} blocks · ${func.instructions} instructions · ${func.dataflow.length} SSA edges${block?`<br><b>${e(block.label)}</b> · immediate dominator ${e(block.immediateDominator||'entry / none')} · loop depth ${block.loopDepth}${ins?`<br><code>${e(ins.text)}</code>`:`<pre class="terminal" style="min-height:0;max-height:240px;margin-bottom:0">${e(block.instructions.map(i=>i.text).join('\n'))}</pre>`}`:'<br>Select a node to inspect its instructions.'}</div>`;
}
function notesPage() {
  return `<section class="hero"><div><div class="eyebrow">Scope, evidence and boundaries</div><h1>What each result means.</h1><p>The pass makes a small set of transformations. The workbench makes their reasoning inspectable.</p></div></section><article class="card notes"><h2>A directional contract</h2><p>LLVM optimizations are checked as source-to-target refinement. The target must preserve behavior where the source is defined. Making a poison result more defined may be allowed; introducing poison on a source-defined input is not.</p><div class="note-callout"><p><code>sdiv -3, 2 = -1</code>, while <code>ashr -3, 1 = -2</code>. The discrepancy comes from rounding toward zero versus rounding down.</p></div><h3>Three semantic outcomes, plus execution state</h3><p><b>Proved</b> means Alive2 verified the captured pair within its model and bounds. <b>Refuted</b> means it produced a counterexample. <b>Unknown</b> covers a timeout, incomplete proof or unsupported semantics. Tool errors and cases that were never run stay visible separately.</p><h3>Flags and arbitrary values need care</h3><p>The pass transfers <code>nsw</code>, <code>nuw</code> and <code>exact</code> only when the replacement has matching semantics. The sign-bit multiplier is left unchanged. A signed bias expansion uses <code>freeze</code> when a source operand is not known to be defined, so its duplicated uses share one value.</p><h3>What the pass changes</h3><p>Scalar integer multiplication, unsigned division and unsigned remainder by powers of two; signed division by positive powers of two; and selected neutral operations. It does not rewrite vectors or alter the control-flow graph. An instruction-count increase in signed lowering is expected; this project makes no hardware speed claim.</p><h3>Public regression corpus</h3><p>The package combines original focused cases with four unchanged MIT-licensed Alive2 regressions. Their upstream revision, file hashes and license are included. The frontend and pass outputs are original project artifacts.</p><h3>Recorded evidence and interactive exploration</h3><p>The browser displays completed executions. It does not run LLVM or Alive2. The rounding lab evaluates concrete integers with BigInt and has a narrower model than LLVM. Graph edges come from LLVM; graph positions come from the renderer.</p><h3>Practical limits</h3><p>These results apply to the captured functions and flags, not every possible compiler input or every future version of the toolchain. Alive2 is a bounded validator, and its upstream documentation excludes interprocedural transformations. Loops require particular care with unrolling bounds. A full compiler or an upstream LLVM bug fix is outside this release’s scope.</p><h3>Toolchain</h3><p>LLVM ${e(goodVersion)} · Alive2 revision <code>${e(short(evidence.toolchain?.alive2?.revision))}</code> · Z3 ${e(evidence.toolchain?.z3?.version||'recorded in lock file')}. The Alive2 compatibility patch in <code>patches/</code> is included in the captured build and recorded in the lock file.</p><div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:22px"><a class="outline" href="https://llvm.org/docs/LangRef.html" target="_blank" rel="noreferrer">LLVM language reference ${icon('external',11)}</a><a class="outline" href="https://github.com/AliveToolkit/alive2" target="_blank" rel="noreferrer">Alive2 documentation ${icon('external',11)}</a></div></article>${footer()}`;
}
function footer() { return `<footer class="footer"><div>IRProof <span style="margin:0 6px">/</span> Integer Rewrite Workbench <span style="margin:0 6px">/</span> v1.0.0</div><div>Recorded evidence. Inspectable transformations.</div></footer>`; }
function toast(message) {
  const el=document.querySelector('#toast'); el.textContent=message; el.className='toast';
  setTimeout(()=>{el.textContent='';el.className='';},2500);
}
function download(name, value) {
  const blob=new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}), url=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function refreshDetail() { document.querySelector('#case-detail').innerHTML=detail(); persist(); }
app.addEventListener('click',async event=>{
  const target=event.target.closest('button,a,[data-node]'); if (!target) return;
  if (target.dataset.route) {state.route=target.dataset.route;state.rail=false;shell();}
  if (target.dataset.case) {state.selected=target.dataset.case;document.querySelector('#case-list').innerHTML=caseList();refreshDetail();}
  if (target.dataset.tab) {state.tab=target.dataset.tab;refreshDetail();}
  if (target.dataset.filter) {state.filter=target.dataset.filter;shell();}
  if (target.dataset.copy) {
    const text=target.dataset.copy==='source'?current().sourceIR:current().targetIR;
    try {await navigator.clipboard.writeText(text);toast('IR copied.');}
    catch {toast('Clipboard unavailable here. Select the IR text to copy it.');}
  }
  if (target.dataset.preset) {document.querySelector('#lab-x').value=target.dataset.preset;document.querySelector('#lab-x').dispatchEvent(new Event('input'));}
  if (target.dataset.graphMode) {state.graphMode=target.dataset.graphMode;state.node='';shell();}
  if (target.dataset.node) {state.node=target.dataset.node;document.querySelector('#graph-area').innerHTML=graphContent();}
  if (target.dataset.action==='menu') {state.rail=!state.rail;document.querySelector('.rail').classList.toggle('open',state.rail);}
  if (target.dataset.action==='counterexample') {state.selected='signed-minus-three';state.filter='all';state.search='';state.tab='comparison';shell();document.querySelector('.bench').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});}
  if (target.dataset.action==='export') {download('IRProof-evidence.json',evidence);toast('Evidence exported.');}
  if (target.dataset.action==='download-case') download(`IRProof-${current().id}.json`,current());
});
app.addEventListener('input',event=>{
  if (event.target.id==='case-search') {state.search=event.target.value;document.querySelector('#case-list').innerHTML=caseList();}
});
app.addEventListener('change',event=>{
  if (event.target.id==='graph-scenario') {state.graph=event.target.value;state.node='';document.querySelector('#graph-area').innerHTML=graphContent();}
});
app.addEventListener('keydown',event=>{
  const n=event.target.closest('[data-node]');
  if (n&&(event.key==='Enter'||event.key===' ')) {event.preventDefault();n.dispatchEvent(new MouseEvent('click',{bubbles:true}));}
  if (event.key==='Escape'&&state.rail) {state.rail=false;document.querySelector('.rail').classList.remove('open');}
  if (event.target.matches('[role="tab"]')&&['ArrowRight','ArrowLeft','Home','End'].includes(event.key)) {
    event.preventDefault();
    const tabs=['comparison','raw','provenance'], currentIndex=tabs.indexOf(state.tab);
    const index=event.key==='Home'?0:event.key==='End'?2:(currentIndex+(event.key==='ArrowRight'?1:2))%3;
    state.tab=tabs[index];refreshDetail();document.querySelector(`[role="tab"][data-tab="${state.tab}"]`).focus();
  }
});
shell();
