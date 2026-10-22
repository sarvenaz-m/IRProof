#!/usr/bin/env python3
"""Build the pinned validator in an isolated prefix using an existing LLVM 23."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def command(argv, cwd=None, env=None):
    subprocess.run([str(a) for a in argv], cwd=cwd, env=env, check=True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--llvm-dir", type=Path, required=True, help="Directory containing LLVMConfig.cmake")
    ap.add_argument("--prefix", type=Path, default=ROOT / "build-tools")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--archive", type=Path, help="Use an already-downloaded, checksum-matching source archive")
    ap.add_argument("--source-only", action="store_true", help="Prepare and verify the patched source without building")
    args = ap.parse_args()
    if args.jobs < 1:
        ap.error("jobs must be positive")
    lock = json.loads((ROOT / "toolchain.lock.json").read_text())
    prefix = args.prefix.resolve()
    prefix.mkdir(parents=True, exist_ok=True)
    archive = args.archive.resolve() if args.archive else prefix / "alive2-source.zip"
    if not archive.exists():
        with urllib.request.urlopen(lock["alive2"]["archiveUrl"], timeout=60) as src, archive.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    if sha256(archive) != lock["alive2"]["archiveSha256"]:
        raise SystemExit("Alive2 source archive checksum does not match toolchain.lock.json.")
    patch = ROOT / lock["alive2"]["patch"]
    if sha256(patch) != lock["alive2"]["patchSha256"]:
        raise SystemExit("The compatibility patch checksum has changed.")
    source = prefix / "alive2-src"
    marker = source / ".irproof-source.json"
    identity = {"revision": lock["alive2"]["revision"], "patchSha256": sha256(patch)}
    fresh_source = not source.exists()
    if not fresh_source:
        if not marker.exists() or json.loads(marker.read_text()) != identity:
            raise SystemExit("Existing source prefix has a different identity. Choose a new --prefix.")
    else:
        source.mkdir()
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                parts = Path(info.filename).parts[1:]
                if not parts:
                    continue
                target = source.joinpath(*parts)
                if not target.resolve().is_relative_to(source.resolve()):
                    raise SystemExit("Unsafe path in source archive")
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise SystemExit("Symlinks are not accepted in the source archive")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(z.read(info))
    # An archive nested in the caller's Git worktree inherits that worktree.
    # In that case git apply can skip every path and still return success.
    # Give the extracted source its own worktree before applying or checking it.
    command(["git", "init", "--quiet", source])
    if fresh_source:
        command(["git", "apply", "--check", patch], cwd=source)
        command(["git", "apply", patch], cwd=source)
    # Check cached sources too: an identity marker alone cannot prove that the
    # compatibility changes are present. Write it only after this check passes.
    command(["git", "apply", "--reverse", "--check", patch], cwd=source)
    marker.write_text(json.dumps(identity, indent=2) + "\n")
    if args.source_only:
        print(f"Prepared pinned source and verified patch: {source}")
        return

    # The solver is isolated from the caller's Python packages and is never
    # installed globally. No credentials or external service is required.
    pydeps = prefix / "python"
    if not (pydeps / "z3").exists():
        command([sys.executable, "-m", "pip", "install", "--target", pydeps, lock["z3"]["pythonDistribution"]])
    probe = subprocess.run([sys.executable, "-c", "import z3; print('.'.join(map(str,z3.get_version()[:3])))"],
                           env={**os.environ, "PYTHONPATH": str(pydeps)}, check=True, text=True, capture_output=True)
    actual = probe.stdout.strip()
    if actual != lock["z3"]["version"]:
        raise SystemExit(f"Unexpected solver version: {actual}")
    include = pydeps / "z3/include"
    version_header = include / "z3_version.h"
    if not version_header.exists():
        major, minor, build = actual.split(".")
        version_header.write_text(f"#define Z3_MAJOR_VERSION {major}\n#define Z3_MINOR_VERSION {minor}\n#define Z3_BUILD_NUMBER {build}\n")
    libdir = pydeps / "z3/lib"
    solver = libdir / ("libz3.dylib" if sys.platform == "darwin" else "libz3.so")
    if not solver.exists():
        raise SystemExit("The expected Z3 shared library is absent. This workflow targets Linux/macOS.")
    build = prefix / "alive2-build"
    env = dict(os.environ)
    loader_var = "DYLD_LIBRARY_PATH" if sys.platform == "darwin" else "LD_LIBRARY_PATH"
    env[loader_var] = str(libdir) + os.pathsep + env.get(loader_var, "")
    command(["cmake", "-S", source, "-B", build, "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TV=ON",
             "-DALIVE_VERSION_OVERRIDE=" + lock["alive2"]["revision"][:12] + "-irproof-llvm23",
             f"-DLLVM_DIR={args.llvm_dir.resolve()}", f"-DZ3_INCLUDE_DIR={include}", f"-DZ3_LIBRARIES={solver}"], env=env)
    command(["cmake", "--build", build, "--target", "alive-tv", "--parallel", args.jobs], env=env)
    print(f"Validator: {build / 'alive-tv'}")


if __name__ == "__main__":
    main()
