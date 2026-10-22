#!/usr/bin/env python3
"""Generate structured IR specimens and capture the compiled audit pass."""
import argparse
from pathlib import Path
import json
from irproof import ROOT, execute, digest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--generator", default="build/irproof-gen")
    ap.add_argument("--opt", default="opt")
    ap.add_argument("--plugin", default="build/IRProofPass.so")
    ap.add_argument("--output", type=Path, default=ROOT / "evidence")
    args = ap.parse_args()
    folder = ROOT / "corpus/generated"
    folder.mkdir(parents=True, exist_ok=True)
    (args.output / "audits").mkdir(parents=True, exist_ok=True)
    records = []
    for scenario in ["divide", "diamond", "loop"]:
        path = folder / f"{scenario}.ll"
        gen = execute([args.generator, "--scenario=" + scenario, "--width=32", "--divisor=8", "-o", str(path)])
        if gen["exitCode"] != 0:
            raise SystemExit(gen["stderr"])
        audit = execute([args.opt, "-load-pass-plugin", args.plugin, "-passes=irproof-audit", "-disable-output", str(path)])
        if audit["exitCode"] != 0:
            raise SystemExit(audit["stderr"])
        data = json.loads(audit["stdout"])
        data["sourceSha256"] = digest(path)
        (args.output / "audits" / f"{scenario}.json").write_text(json.dumps(data, indent=2) + "\n")
        records.append({"scenario": scenario, "generation": gen, "analysis": audit, "sourceSha256": digest(path)})
    (args.output / "frontend-runs.json").write_text(json.dumps(records, indent=2) + "\n")
    print("Captured divide, diamond and loop specimens with their LLVM analyses.")


if __name__ == "__main__":
    main()
