#!/usr/bin/env python3
"""Run LLVM and Alive2, retaining raw evidence and conservative verdicts."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(argv: list[str], timeout: float = 30.0) -> dict:
    start = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                              encoding="utf-8", errors="replace", check=False)
        return {"command": argv, "exitCode": proc.returncode, "stdout": proc.stdout,
                "stderr": proc.stderr, "durationMs": round((time.monotonic() - start) * 1000, 2), "timedOut": False}
    except subprocess.TimeoutExpired as exc:
        def decode(value):
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
        return {"command": argv, "exitCode": None, "stdout": decode(exc.stdout),
                "stderr": decode(exc.stderr), "durationMs": round((time.monotonic() - start) * 1000, 2), "timedOut": True}


def classify(run: dict) -> tuple[str, str]:
    """Never infer a proof from an exit code, an expectation, or partial success."""
    output = run.get("stdout", "") + "\n" + run.get("stderr", "")
    if run.get("timedOut"):
        return "unknown", "The validator exceeded the wall-clock budget."
    # Summaries are required: a crash after printing a success is still an error.
    pattern = (r"Summary:\s*(\d+) correct transformations\s*"
               r"(\d+) incorrect transformations\s*(\d+) failed-to-prove transformations\s*"
               r"(\d+) Alive2 errors")
    matches = list(re.finditer(pattern, output))
    if run.get("exitCode", 0) is not None and run.get("exitCode", 0) < 0:
        return "error", "The validator terminated by signal."
    if matches:
        correct, incorrect, failed, errors = map(int, matches[-1].groups())
        if incorrect:
            return "refuted", "Alive2 found a counterexample to refinement."
        if failed:
            return "unknown", "Alive2 did not complete a proof."
        if errors:
            if re.search(r"unsupported|not supported|unimplemented", output, re.I):
                return "unknown", "The pair uses semantics outside this validator's supported model."
            return "error", "Alive2 reported a tool or input error."
        if correct == 1 and run.get("exitCode") == 0:
            return "proved", "Alive2 verified this source-to-target refinement."
        return "error", "Expected exactly one checked transformation."
    if re.search(r"unsupported|not supported|unimplemented", output, re.I):
        return "unknown", "The pair uses semantics outside this validator's supported model."
    return "error", "No complete, recognized Alive2 summary was produced."


def function_text(module: str, name: str) -> str:
    # This is presentation extraction, not an LLVM parser. Verification always
    # receives the original full modules, including declarations and attributes.
    found = re.search(r"^define\s+[^\n]*@" + re.escape(name) + r"\([^\n]*\)[^\n]*\{\n.*?^\}", module, re.M | re.S)
    return found.group(0) if found else module


def version(tool: str) -> dict:
    path = shutil.which(tool) or (tool if Path(tool).is_file() else None)
    if not path:
        return {"available": False, "requested": tool}
    result = execute([str(path), "--version"], 15)
    return {"available": True, "name": Path(path).name,
            "version": (result["stdout"] + result["stderr"]).strip(), "sha256": digest(Path(path).resolve())}


def run_suite(args) -> int:
    manifest = json.loads((ROOT / "corpus" / "manifest.json").read_text())
    out = Path(args.output).resolve()
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "ir").mkdir(parents=True, exist_ok=True)
    tools = {"opt": version(args.opt), "alive2": version(args.alive_tv)}
    extract_tool = args.llvm_extract or str(Path(args.opt).with_name("llvm-extract"))
    tools["llvmExtract"] = version(extract_tool)
    if not tools["opt"]["available"]:
        raise SystemExit("LLVM opt is missing. Pass --opt with its executable path.")
    plugin = Path(args.plugin).resolve()
    if not plugin.is_file():
        raise SystemExit("The pass plugin is missing. Build it and pass --plugin.")
    records = []
    for case in manifest["cases"]:
        source = ROOT / case["path"]
        text = source.read_text()
        record = {**case, "inputSha256": digest(source), "sourceSha256": digest(source), "status": "not_run"}
        raw = {"caseId": case["id"], "inputSha256": digest(source)}
        if case["mode"] == "pass":
            target = out / "ir" / f"{case['id']}.ll"
            transform = execute([args.opt, "-load-pass-plugin", str(plugin), "-passes=irproof-pipeline", "-verify-each", "-S", str(source), "-o", str(target)])
            raw["transform"] = transform
            if transform["exitCode"] != 0 or transform["timedOut"]:
                record.update(status="error", reason="LLVM could not produce a verified target module.")
                record["sourceIR"] = text
                record["targetIR"] = ""
            else:
                record["sourceIR"] = function_text(text, "specimen")
                record["targetIR"] = function_text(target.read_text(), "specimen")
                record["targetSha256"] = digest(target)
                validator_cmd = [args.alive_tv, str(source), str(target)]
        else:
            # Alive2's one-file src/tgt mode omits its summary. Extract both
            # functions with LLVM itself and use two-file mode consistently.
            # llvm-extract retains referenced declarations and attributes.
            prepared = []
            paths = []
            if not tools["llvmExtract"]["available"]:
                raise SystemExit("llvm-extract is required for paired regressions.")
            for name in ["src", "tgt"]:
                path = out / "ir" / f"{case['id']}.{name}.ll"
                extraction = execute([extract_tool, "--func=" + name, "-S", str(source), "-o", str(path)])
                prepared.append(extraction)
                if extraction["exitCode"] != 0:
                    record.update(status="error", reason="LLVM could not extract a validator input.")
                    break
                # The curated functions have simple, unquoted identifiers. This
                # rename includes recursive references as well as the definition.
                renamed = re.sub(r"@" + name + r"(?=[\s(])", "@specimen", path.read_text())
                path.write_text(renamed)
                paths.append(path)
            raw["extraction"] = prepared
            if record["status"] != "error":
                record["sourceIR"] = function_text(paths[0].read_text(), "specimen")
                record["targetIR"] = function_text(paths[1].read_text(), "specimen")
                record["sourceSha256"] = digest(paths[0])
                record["targetSha256"] = digest(paths[1])
                validator_cmd = [args.alive_tv, str(paths[0]), str(paths[1])]
        if record["status"] != "error":
            if tools["alive2"]["available"]:
                check = execute(validator_cmd, args.timeout)
                raw["validation"] = check
                status, reason = classify(check)
                record.update(status=status, reason=reason, durationMs=check["durationMs"],
                              rawOutput=check["stdout"] + check["stderr"])
            else:
                record.update(status="not_run", reason="Alive2 is not available in this environment.", rawOutput="")
        record["expectationMet"] = record["status"] == case["expected"]
        evidence = out / "raw" / f"{case['id']}.json"
        evidence.write_text(json.dumps(raw, indent=2) + "\n")
        record["evidenceFile"] = f"raw/{case['id']}.json"
        record["evidenceSha256"] = digest(evidence)
        records.append(record)
        print(f"{record['status']:8s} {case['id']}", flush=True)
    counts = {status: sum(r["status"] == status for r in records)
              for status in ["proved", "refuted", "unknown", "error", "not_run"]}
    report = {"schemaVersion": SCHEMA_VERSION, "project": "IRProof", "version": "1.0.0",
              "generatedAt": datetime.now(timezone.utc).isoformat(), "tools": tools,
              "pluginSha256": digest(plugin), "timeoutSeconds": args.timeout,
              "summary": counts, "cases": records}
    (out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(counts))
    return 1 if args.strict and any(not r["expectationMet"] for r in records) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run", help="Transform and validate the curated corpus")
    run.add_argument("--opt", default=os.getenv("LLVM_OPT", "opt"))
    run.add_argument("--alive-tv", default=os.getenv("ALIVE_TV", "alive-tv"))
    run.add_argument("--llvm-extract", help="Defaults to llvm-extract next to opt")
    run.add_argument("--plugin", default="build/IRProofPass.so")
    run.add_argument("--output", default="evidence")
    run.add_argument("--timeout", type=float, default=30)
    run.add_argument("--strict", action="store_true", help="Fail if any actual verdict differs from the manifest")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    return run_suite(args)


if __name__ == "__main__":
    sys.exit(main())
