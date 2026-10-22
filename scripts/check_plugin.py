#!/usr/bin/env python3
"""Exercise the compiled plugin and compare concrete executions with LLVM lli."""
import argparse
from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(argv, **kwargs):
    p = subprocess.run(argv, text=True, capture_output=True, timeout=60, **kwargs)
    if p.returncode:
        raise RuntimeError(f"Command failed ({p.returncode}): {argv}\n{p.stdout}\n{p.stderr}")
    return p.stdout


def main():
    ap = argparse.ArgumentParser()
    for name in ["opt", "lli", "plugin", "generator"]:
        ap.add_argument("--" + name, required=True)
    args = ap.parse_args()
    comparisons = 0
    with tempfile.TemporaryDirectory(prefix="irproof-test-") as tmp:
        tmp = Path(tmp)
        modules, checks = [], []
        def pair(name, bits, body, values):
            nonlocal comparisons
            src = f"define i{bits} @{name}(i{bits} noundef %x) {{\nentry:\n{body}\n}}\n"
            source, target = tmp / "source.ll", tmp / "target.ll"
            source.write_text(src)
            run([args.opt, "-load-pass-plugin", args.plugin, "-passes=irproof-pipeline", "-verify-each", "-S", str(source), "-o", str(target)])
            transformed = re.search(r"^define.*?^\}", target.read_text(), re.S | re.M).group(0)
            modules.extend([src, transformed.replace("@" + name + "(", "@" + name + "_target(")])
            for value in values:
                i = comparisons
                checks.extend([f"  %a{i} = call i{bits} @{name}(i{bits} {value})",
                               f"  %b{i} = call i{bits} @{name}_target(i{bits} {value})",
                               f"  %eq{i} = icmp eq i{bits} %a{i}, %b{i}",
                               f"  %ok{i} = and i1 {'true' if i == 0 else '%ok' + str(i - 1)}, %eq{i}"])
                comparisons += 1
            return transformed

        for op, d in [("sdiv", 2), ("sdiv", 4), ("sdiv", 64), ("udiv", 8), ("urem", 16), ("mul", 4)]:
            pair(f"{op}_{d}_i8", 8, f"  %q = {op} i8 %x, {d}\n  ret i8 %q", range(-128, 128))
        for bits in [16, 32, 64, 128]:
            edge = [-(1 << (bits - 1)), -(1 << (bits - 1)) + 1, -129, -128, -17, -9, -8, -7, -3, -2, -1,
                    0, 1, 2, 3, 7, 8, 9, 127, 128, (1 << (bits - 1)) - 2, (1 << (bits - 1)) - 1]
            pair(f"sdiv_edge_i{bits}", bits, f"  %q = sdiv i{bits} %x, 8\n  ret i{bits} %q", edge)
        # An exact operation is executed only on inputs within its defined domain.
        pair("exact_i8", 8, "  %q = sdiv exact i8 %x, 4\n  ret i8 %q", range(-128, 128, 4))
        kept = pair("signbit_guard", 8, "  %q = mul nsw i8 %x, -128\n  ret i8 %q", [0, 1])
        assert "mul nsw" in kept, "The sign-bit multiplier must stay untouched"
        full = "\n".join(modules) + "\ndefine i32 @main() {\nentry:\n" + "\n".join(checks) + f"\n  %bad = xor i1 %ok{comparisons - 1}, true\n  %status = zext i1 %bad to i32\n  ret i32 %status\n}}\n"
        harness = tmp / "harness.ll"
        harness.write_text(full)
        run([args.opt, "-passes=verify", "-disable-output", str(harness)])
        run([args.lli, str(harness)])
        for scenario in ["divide", "diamond", "loop"]:
            path = tmp / f"{scenario}.ll"
            run([args.generator, f"--scenario={scenario}", "-o", str(path)])
            data = json.loads(run([args.opt, "-load-pass-plugin", args.plugin, "-passes=irproof-audit", "-disable-output", str(path)]))
            f = data["functions"][0]
            assert f["instructions"] > 0
            assert len(f["blocks"]) == (1 if scenario == "divide" else 4)
            assert all(edge["from"] != "" and edge["to"] != "" for edge in f["dataflow"])
            if scenario == "loop":
                assert any(edge["backedge"] for edge in f["cfg"]), "Loop backedge missing"
                assert max(b["loopDepth"] for b in f["blocks"]) == 1
            if scenario == "diamond":
                reduced = tmp / "diamond.reduced.ll"
                run([args.opt, "-load-pass-plugin", args.plugin, "-passes=irproof-pipeline", "-verify-each", "-S", str(path), "-o", str(reduced)])
                assert "lshr" in reduced.read_text(), "Dominating branch knowledge was not used"
                assert "irproof.bias" in reduced.read_text(), "Negative branch lost its correction"
        print(json.dumps({"concreteComparisons": comparisons, "generators": 3, "auditChecks": "passed", "status": "passed"}))


if __name__ == "__main__":
    main()
