export function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
export function drawGraph(func, mode = 'cfg', selected = '') {
  if (!func) return '<p class="empty">No recorded graph is available.</p>';
  let nodes, edges, positions = new Map();
  if (mode === 'cfg') {
    nodes = func.blocks.map(b => ({id:b.id, title:b.label.replace(/^%/, ''), sub:`${b.instructions.length} instructions · depth ${b.loopDepth}`, loop:b.loopDepth > 0}));
    edges = func.cfg;
    const named = new Map(func.blocks.map((b, i) => [b.label, i]));
    nodes.forEach((n, i) => {
      if (nodes.length === 4) {
        const diamond = named.has('%merge');
        const coords = diamond ? [[290,20],[100,140],[480,140],[290,270]] : [[290,15],[290,125],[510,230],[60,255]];
        positions.set(n.id, coords[i]);
      } else positions.set(n.id, [100 + (i % 3) * 250, 25 + Math.floor(i / 3) * 130]);
    });
  } else {
    nodes = func.blocks.flatMap(b => b.instructions.map(i => ({id:i.id, title:i.opcode, sub:i.text.trim().slice(0, 29), loop:false})));
    edges = func.dataflow;
    nodes.forEach((n, i) => positions.set(n.id, [25 + (i % 4) * 202, 20 + Math.floor(i / 4) * 105]));
  }
  const w = 840, h = mode === 'cfg' ? 380 : Math.max(270, Math.ceil(nodes.length / 4) * 105 + 20), nw = mode === 'cfg' ? 200 : 178, nh = 66;
  const paths = edges.map(e => {
    const a = positions.get(e.from), b = positions.get(e.to);
    if (!a || !b) return '';
    const back = !!e.backedge;
    const x1 = a[0] + nw/2, y1 = a[1] + nh, x2 = b[0] + nw/2, y2 = b[1];
    const d = back ? `M${a[0]+nw} ${a[1]+nh/2} C${w-5} ${a[1]+nh/2} ${w-5} ${b[1]+nh/2} ${b[0]+nw} ${b[1]+nh/2}`
      : `M${x1} ${y1} C${x1} ${y1+40} ${x2} ${y2-40} ${x2} ${y2}`;
    return `<path class="graph-edge ${back?'backedge':''}" d="${d}" marker-end="url(#arrow-${mode})"/>${e.label?`<text class="edge-label" x="${(x1+x2)/2+8}" y="${(y1+y2)/2}">${escapeHTML(e.label)}</text>`:''}`;
  }).join('');
  return `<svg class="ir-graph" viewBox="0 0 ${w} ${h}" role="img" aria-label="${mode==='cfg'?'Control flow':'SSA data dependency'} graph"><defs><marker id="arrow-${mode}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L8 4L0 8z" class="graph-arrow"/></marker></defs>${paths}${nodes.map(n => {
    const [x,y] = positions.get(n.id);
    return `<g class="graph-node ${selected===n.id?'selected':''} ${n.loop?'in-loop':''}" data-node="${escapeHTML(n.id)}" role="button" tabindex="0" aria-label="Inspect ${escapeHTML(n.title)}" transform="translate(${x},${y})"><rect width="${nw}" height="${nh}" rx="10"/><circle cx="17" cy="22" r="3"/><text class="node-title" x="29" y="27">${escapeHTML(n.title)}</text><text class="node-sub" x="16" y="49">${escapeHTML(n.sub)}</text></g>`;
  }).join('')}</svg>`;
}
