#!/usr/bin/env python3
"""Check the saved evidence chain without rerunning LLVM or Alive2."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    report = json.loads((ROOT / "evidence/results.json").read_text())
    errors = []
    manifest = json.loads((ROOT / "corpus/manifest.json").read_text())
    if {c["id"] for c in report["cases"]} != {c["id"] for c in manifest["cases"]}:
        errors.append("Manifest and captured case IDs differ")
    for c in report["cases"]:
        if sha256(ROOT / c["path"]) != c["inputSha256"]:
            errors.append(c["id"] + ": original input changed")
        raw_path = ROOT / "evidence" / c["evidenceFile"]
        if sha256(raw_path) != c["evidenceSha256"]:
            errors.append(c["id"] + ": evidence record changed")
        if c["mode"] == "pair":
            src = ROOT / "evidence/ir" / (c["id"] + ".src.ll")
            tgt = ROOT / "evidence/ir" / (c["id"] + ".tgt.ll")
        else:
            src = ROOT / c["path"]
            tgt = ROOT / "evidence/ir" / (c["id"] + ".ll")
        if sha256(src) != c["sourceSha256"] or sha256(tgt) != c["targetSha256"]:
            errors.append(c["id"] + ": checked module changed")
    upstream = json.loads((ROOT / "corpus/upstream/provenance.json").read_text())
    for c in upstream["files"]:
        if sha256(ROOT / c["path"]) != c["sha256"]:
            errors.append(c["id"] + ": upstream file changed")
    for p in (ROOT / "evidence/audits").glob("*.json"):
        audit = json.loads(p.read_text())
        if sha256(ROOT / "corpus/generated" / (p.stem + ".ll")) != audit["sourceSha256"]:
            errors.append(p.name + ": audit source changed")
    lock = json.loads((ROOT / "toolchain.lock.json").read_text())
    if sha256(ROOT / lock["alive2"]["patch"]) != lock["alive2"]["patchSha256"]:
        errors.append("Validator patch changed")
    counts = {k: sum(c["status"] == k for c in report["cases"]) for k in report["summary"]}
    if counts != report["summary"]:
        errors.append("Summary counts disagree with per-case results")
    result = {"status": "failed" if errors else "passed", "cases": len(report["cases"]),
              "upstreamFiles": len(upstream["files"]), "audits": 3, "errors": errors,
              "scope": "File integrity and record consistency; not an independent solver proof"}
    print(json.dumps(result, indent=2))
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
