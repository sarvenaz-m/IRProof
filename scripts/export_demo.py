#!/usr/bin/env python3
"""Export a captured run as a portable workbench without network dependencies."""
from pathlib import Path
import argparse
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, default=ROOT / "evidence/results.json")
    ap.add_argument("--output", type=Path, default=ROOT / "demo/IRProof.html")
    args = ap.parse_args()
    data = json.loads(args.results.read_text())
    if data.get("schemaVersion") != 1 or not data.get("cases"):
        raise SystemExit("A completed, schema-v1 run is required.")
    lock = ROOT / "toolchain.lock.json"
    data["toolchain"] = json.loads(lock.read_text()) if lock.exists() else {}
    data["audits"] = {p.stem: json.loads(p.read_text()) for p in sorted((args.results.parent / "audits").glob("*.json"))}
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=True).replace("<", "\\u003c")
    assets = ROOT / "demo/assets"
    (assets / "evidence.js").write_text("window.IRPROOF_EVIDENCE=" + payload + ";\n")
    css = (assets / "style.css").read_text()
    for font in ["work-sans", "jetbrains-mono"]:
        encoded = base64.b64encode((assets / f"{font}.woff2").read_bytes()).decode()
        css = css.replace(f"url('./{font}.woff2')", f"url('data:font/woff2;base64,{encoded}')")
    scripts = []
    for name in ["icons", "graphs", "math", "app"]:
        script = (assets / f"{name}.mjs").read_text()
        script = re.sub(r"^import .*?;\n", "", script, flags=re.M)
        script = re.sub(r"\bexport function\b", "function", script)
        scripts.append(script)
    code = "\n".join(scripts)
    if "</script" in code.lower():
        raise SystemExit("Unsafe script terminator in source")
    mark = base64.b64encode((assets / "mark.svg").read_bytes()).decode()
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; font-src data:; img-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="theme-color" content="#254d49"><title>IRProof — Integer Rewrite Workbench</title>
<meta name="description" content="Recorded LLVM and Alive2 validation, with inspectable IR and concrete counterexamples.">
<link rel="icon" href="data:image/svg+xml;base64,{mark}"><style>{css}</style></head>
<body><div id="app"></div><script>window.IRPROOF_EVIDENCE={payload};</script><script>(()=>{{'use strict';\n{code}\n}})();</script></body></html>'''
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    if args.output.resolve() == (ROOT / "demo/IRProof.html").resolve():
        for entrypoint in [ROOT / "index.html", ROOT / "demo/index.html"]:
            entrypoint.write_text(html)
    print(f"Exported {args.output.name}: {args.output.stat().st_size:,} bytes; {len(data['cases'])} captured cases")


if __name__ == "__main__":
    main()
