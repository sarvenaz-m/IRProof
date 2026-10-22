from pathlib import Path
import json,html
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether,Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

root=Path(__file__).resolve().parents[1]
r=json.loads((root/'evidence/results.json').read_text())
assert r['summary'] == {'proved':25,'refuted':9,'unknown':1,'error':0,'not_run':0}, 'The report snapshot needs updating for this evidence set.'
fontroot=Path('/usr/share/fonts/truetype/dejavu')
for name,f in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(fontroot/f)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
INK=colors.HexColor('#2b302d');DEEP=colors.HexColor('#254d49');MUTED=colors.HexColor('#5f665d');LINE=colors.HexColor('#ddd9cf');PAPER=colors.HexColor('#f6f3ec');TEAL=colors.HexColor('#3f6b64');ROSE=colors.HexColor('#a0503e')
styles={
 'eyebrow':ParagraphStyle('eyebrow',fontName='Bold',fontSize=8,leading=12,textColor=MUTED,spaceAfter=9),
 'title':ParagraphStyle('title',fontName='Bold',fontSize=30,leading=36,textColor=DEEP,spaceAfter=12),
 'h1':ParagraphStyle('h1',fontName='Bold',fontSize=23,leading=29,textColor=DEEP,spaceAfter=16),
 'h2':ParagraphStyle('h2',fontName='Bold',fontSize=12,leading=17,textColor=DEEP,spaceBefore=16,spaceAfter=8),
 'p':ParagraphStyle('p',fontName='Body',fontSize=10,leading=16,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.2,leading=12.4,textColor=MUTED,spaceAfter=5),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=8.6,leading=13,textColor=INK),
 'headcell':ParagraphStyle('headcell',fontName='Bold',fontSize=8.5,leading=12,textColor=INK),
 'metric':ParagraphStyle('metric',fontName='Bold',fontSize=26,leading=32,textColor=INK),
 'metriclabel':ParagraphStyle('metriclabel',fontName='Body',fontSize=8,leading=12,textColor=MUTED),
 'code':ParagraphStyle('code',fontName='Mono',fontSize=8.3,leading=13,textColor=INK,backColor=PAPER,borderPadding=13,spaceBefore=7,spaceAfter=12),
 'quote':ParagraphStyle('quote',fontName='Body',fontSize=12,leading=20,textColor=TEAL,leftIndent=14,borderColor=LINE,borderWidth=0,borderPadding=8,spaceBefore=7,spaceAfter=14)
}
def p(text,kind='p'):return Paragraph(text,styles[kind])
def heading(text):return p(text,'h2')
def table(headers,rows,widths):
 data=[[p(str(c),'headcell') for c in headers]]+[[p(str(c),'cell') for c in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PAPER),('LINEBELOW',(0,0),(-1,0),.7,LINE),('LINEBELOW',(0,1),(-1,-1),.4,LINE),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]))
 return t

def chrome(c,doc):
 c.saveState()
 w,h=A4
 c.setFillColor(INK);c.roundRect(46,h-45,20,20,5,stroke=0,fill=1)
 c.setStrokeColor(colors.HexColor('#e7dfc6'));c.setLineWidth(1.1)
 c.line(52,h-29,52,h-41);c.line(52,h-35,61,h-35);c.line(57,h-29,62,h-35);c.line(62,h-35,57,h-41)
 c.setFont('Bold',10);c.setFillColor(INK);c.drawString(76,h-38,'IRProof')
 c.setFillColor(MUTED);c.setFont('Body',7);c.drawRightString(w-46,h-38,'TECHNICAL REPORT  /  v1.0.0')
 c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(46,44,w-46,44)
 c.setFont('Body',7);c.setFillColor(MUTED);c.drawString(46,30,'21 October 2026  |  Checked integer transformations')
 c.drawRightString(w-46,30,f'{doc.page} / 4')
 c.restoreState()

story=[]
story += [p('COMPILER ENGINEERING / RECORDED VALIDATION','eyebrow'),p('A small rewrite,<br/>fully inspectable.','title'),p('IRProof combines a focused LLVM pass, a structured IR generator, translation validation and an evidence viewer. The result is a compact engineering project with results that can be inspected and reproduced.'),Spacer(1,8)]
metrics=Table([[p('25','metric'),p('09','metric'),p('01','metric')],[p('REFINEMENTS PROVED','metriclabel'),p('REWRITES REFUTED','metriclabel'),p('CHECK LEFT UNKNOWN','metriclabel')]],colWidths=[167,167,167])
metrics.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PAPER),('BOX',(0,0),(-1,-1),.7,LINE),('LINEAFTER',(0,0),(1,-1),.7,LINE),('TOPPADDING',(0,0),(-1,0),15),('BOTTOMPADDING',(0,1),(-1,1),15),('LEFTPADDING',(0,0),(-1,-1),17)]))
story += [metrics,heading('The problem is in the contract'),p('A replacement that looks obvious over ordinary arithmetic can fail under LLVM integer semantics. Signed division by two is the smallest example: division rounds toward zero, while an arithmetic right shift rounds down. Overflow flags and undefined values create further restrictions. [1]'),p('<b>sdiv i32 -3, 2 = -1</b><br/><b>ashr i32 -3, 1 = -2</b>','quote'),p('The captured validator output for <font name="Mono">signed-minus-three</font> reports the source value as -1 and the target value as -2. This is a real rejected pair, retained in the evidence directory.'),heading('What was built'),p('The original code includes a C++20 New Pass Manager plugin, a read-only audit, three IRBuilder specimens, 29 original cases, execution and integrity scripts, a responsive viewer, and an LLVM-23 compatibility patch for Alive2. Four public regression files are retained unchanged under their upstream license.'),p('<b>Recorded environment:</b> LLVM 23.1.4; Alive2 c9af7dbb5038 plus the included patch; Z3 5.3.1. All 35 pairs were executed. There were no tool errors or unexecuted checks.','small'),p('The contribution is implementation and evidence integration. The project does not claim a new arithmetic identity, a new solver, an upstream-accepted patch or a hardware speed improvement.','small'),PageBreak()]

story += [p('01 / COMPILER DESIGN','eyebrow'),p('Focused transformations,<br/>explicit preconditions.','h1'),table(['Component','Implemented responsibility'],[
 ('Function pass','Scalar integer rewrites, flag handling, definedness checks and branch-sensitive sign information.'),
 ('Module audit','CFG and SSA edges; instructions and flags; immediate dominators; loop depth and backedges.'),
 ('C++ frontend','Verified divide, diamond and loop specimens constructed with LLVM IRBuilder.'),
 ('Evidence runner','Exact source/target execution, conservative verdicts and file provenance.')],[118,383]),heading('Transformation rules'),table(['Source pattern','Replacement and guard'],[
 ('mul x, 2^k','shl x, k for a positive signed constant; existing nsw/nuw are transferred.'),
 ('udiv x, 2^k','lshr x, k; preserve exact when present.'),
 ('urem x, 2^k','and x, (2^k - 1).'),
 ('sdiv x, 2^k','Identity for 1; exact arithmetic shift when exact; logical shift for known nonnegative values; otherwise a bias expansion.'),
 ('Neutral operations','Remove add/sub/or/xor by zero and and by all ones.')],[118,383]),heading('General signed lowering'),Preformatted('stable = freeze x  ; omitted when x is known defined\nsign   = ashr stable, W - 1\nbias   = and sign, (2^k - 1)\nq      = ashr (stable + bias), k',styles['code']),p('The freeze is a conservative way to share one operand choice across the expansion. The bias addition receives no invented overflow flags. Branch-derived sign facts are used only for defined operands. The pass does not alter blocks or edges and preserves CFG analyses. [2]','small'),p('A signed-negative sign-bit multiplier is deliberately skipped. For x = 1, <font name="Mono">mul nsw i8 x, -128</font> is defined, but <font name="Mono">shl nsw i8 x, 7</font> is poison. The captured negative case verifies that distinction.','small'),PageBreak()]

story += [p('02 / VALIDATION AND PUBLIC CORPUS','eyebrow'),p('Evidence for each outcome.','h1'),table(['Source of cases','Proved','Refuted','Unknown'],[
 ('Original pass and frontend checks','23','0','0'),
 ('Original deliberately invalid pairs','0','7','0'),
 ('Original atomic-memory probe','0','0','1'),
 ('Four unchanged Alive2 regressions','2','2','0'),
 ('Total','25','9','1')],[248,85,85,83]),heading('A verdict needs a completed check'),p('The runner accepts a proof only from a complete recognized Alive2 summary with exactly one correct transformation and a successful process exit. It keeps refutations, failed proofs, unsupported semantics, signals, input errors and unexecuted cases separate. Manifest expectations are used to fail tests, never to manufacture the displayed verdict.'),p('The atomicrmw specimen is unknown because the validator reports an unsupported instruction. It is not a proof. Loop IR is included for frontend and graph inspection; it is excluded from the 35 claimed refinement checks.'),heading('Two complementary test layers'),p('<b>Compiled execution:</b> 1,690 before/after comparisons run through LLVM lli. These include exhaustive signed 8-bit inputs for six operations, boundary inputs at 16, 32, 64 and 128 bits, defined inputs for exact division, and a guarded sign-bit case. All passed.'),p('<b>Failure handling and interface:</b> 12 Python unit tests cover verdict classification, including partial output and crashes. Four browser arithmetic tests cover the numeric lab. Browser checks exercise search, verdict filters, raw output, provenance, CFG and SSA inspection, JSON export, keyboard tabs and mobile layout.'),heading('Public data is a regression corpus'),p('The four public Alive2 files exercise freeze/undef, an overflow intrinsic, and the two directions of poison refinement. Their full upstream revision, source paths, SHA-256 hashes and MIT license are included. This is a focused public test corpus, not a statistical benchmark or a representative sample of all LLVM programs. [3]'),p('Each record retains input, target and raw-output hashes, commands, exit status and timings. Integrity checks establish file consistency; they neither rerun the solver nor authenticate the capture.','small'),PageBreak()]

story += [p('03 / REPRODUCIBILITY AND LIMITS','eyebrow'),p('Reproduce with a clear scope.','h1'),p('Use matching LLVM 23 headers and command-line tools, a C++20 compiler, CMake, Ninja and Python. The pinned validator bootstrap additionally needs Git, re2c and pip. Full commands and platform notes are in <font name="Mono">docs/reproducibility.md</font>.'),Preformatted('cmake -S . -B build -G Ninja \\\n  -DCMAKE_BUILD_TYPE=Release -DLLVM_DIR="$LLVM_DIR"\ncmake --build build --parallel 2\nctest --test-dir build --output-on-failure\n\npython scripts/capture_frontend.py\npython scripts/make_corpus.py\npython scripts/irproof.py run --alive-tv "$ALIVE_TV" --strict\npython scripts/verify_evidence.py\npython scripts/export_demo.py',styles['code']),heading('Compatibility is part of the record'),p('The supplied patch adapts the pinned Alive2 tree to LLVM 23 APIs, removes enum cases that require LLVM 24, adds an archive-build version label, and avoids a second solver runtime through LLVM shared linkage. It leaves the SMT refinement rules unchanged. The exact revision, patch hash and captured binary hash are recorded in the lock file.','small'),heading('Limits that matter'),p('The pass handles scalar integers and a bounded set of local rewrites. It does not perform vector, floating-point, memory or interprocedural optimization. Signed lowering may add instructions; target-specific performance is not measured.'),p('Alive2 checks refinement within its supported model and resource bounds. A successful pair is not a proof of every execution of the entire pass. The loop specimen is used for analysis only. Unknown checks and tool errors must remain visible. [3, 4]'),p('The standalone browser file is a viewer for completed executions. Its BigInt lab evaluates concrete integers and does not model poison, undef or memory. Topology comes from LLVM analysis; graph coordinates come from the renderer.','small'),heading('Primary references'),p('[1] LLVM Project. LLVM Language Reference Manual. Integer operations, flags and freeze.<br/><link href="https://llvm.org/docs/LangRef.html" color="#3f6b64">llvm.org/docs/LangRef.html</link>','small'),p('[2] LLVM Project. Writing an LLVM Pass (New Pass Manager).<br/><link href="https://llvm.org/docs/WritingAnLLVMNewPMPass.html" color="#3f6b64">llvm.org/docs/WritingAnLLVMNewPMPass.html</link>','small'),p('[3] AliveToolkit. Alive2 source and regression corpus, revision c9af7dbb503878554aefafddba5889ccab237503.<br/><link href="https://github.com/AliveToolkit/alive2" color="#3f6b64">github.com/AliveToolkit/alive2</link>','small'),p('[4] Lopes, N. P., Lee, J., Hur, C.-K., Liu, Z., and Regehr, J. (2021). Alive2: Bounded Translation Validation for LLVM. PLDI 2021.<br/><link href="https://doi.org/10.1145/3453483.3454030" color="#3f6b64">doi.org/10.1145/3453483.3454030</link>','small')]

out=root/'docs/IRProof-Technical-Report.pdf'
doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=46,leftMargin=46,topMargin=76,bottomMargin=63,title='IRProof - Technical Report',author='IRProof contributors',subject='LLVM integer rewrites, Alive2 evidence and reproducible validation')
doc.build(story,onFirstPage=chrome,onLaterPages=chrome)
print(out, out.stat().st_size)
