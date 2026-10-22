# Reproducibility

The recorded environment is Linux x86_64 with LLVM 23.1.4, C++20, CMake 3.28.3, Ninja, re2c 3.1, Python 3.12.14 and Z3 5.3.1. Exact validator revision and patch checksums are in `toolchain.lock.json`. A different compiler, path or platform can change binary hashes and timings; the semantic verdicts and test outcomes are the reproduction targets.

## Build the project

Use a complete LLVM 23 development installation. Its `opt`, `llvm-extract`, `lli` and headers must match. If the executables carry a suffix, use `llvm-config-23` in place of `llvm-config` and explicit paths for the tools below.

```sh
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_DIR="$(llvm-config --cmakedir)"
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
```

The plugin is `build/IRProofPass.so` on the recorded Linux platform. On another platform use the actual module filename CMake emits. The suite exercises 12 verdict-parser cases and 1,690 concrete comparisons, then checks all three frontend scenarios and audit properties.

## Build the pinned validator

The bootstrap verifies the official source archive checksum, applies the included patch, installs the pinned solver into an isolated prefix, and builds `alive-tv`. It needs Git for patch application, re2c, pip, CMake, Ninja and a C++20 compiler. LLVM must provide its static component libraries and the development dependencies identified by its CMake configuration.

```sh
python scripts/bootstrap_alive2.py \
  --llvm-dir "$(llvm-config --cmakedir)" --prefix build-tools --jobs 2
```

The resulting executable is `build-tools/alive2-build/alive-tv`. A checksum-matching predownloaded archive can be passed with `--archive`; `--source-only` prepares the patched source without compiling it.

The compatibility patch adapts target-machine creation and library-function lookup to LLVM 23, removes switch cases for LLVM-24-only enum entries that cannot occur in LLVM 23 input, permits an explicit version label for archive builds, and links LLVM components statically to avoid bringing in a second Z3 runtime through libLLVM. It does not modify the SMT refinement rules.

## Capture and validate

Generate the specimens first, rebuild the manifest, then validate every case:

```sh
python scripts/capture_frontend.py --opt opt \
  --plugin build/IRProofPass.so --generator build/irproof-gen
python scripts/make_corpus.py
python scripts/irproof.py run --opt opt \
  --alive-tv build-tools/alive2-build/alive-tv \
  --plugin build/IRProofPass.so --output evidence --timeout 30 --strict
python scripts/verify_evidence.py
python scripts/export_demo.py
```

`--strict` returns failure if any observed verdict differs from the manifest. The expected result of the atomic-memory case is `unknown`; it is intentionally excluded from the proof count. Reproduction overwrites the chosen evidence directory, so use a separate checkout or output directory to retain the supplied capture.

## Individual commands

```sh
opt -load-pass-plugin build/IRProofPass.so \
  -passes=irproof-pipeline -verify-each -S corpus/original/sdiv-32-8.ll -o target.ll
alive-tv corpus/original/sdiv-32-8.ll target.ll

build/irproof-gen --scenario=diamond --width=32 --divisor=8 -o diamond.ll
opt -load-pass-plugin build/IRProofPass.so \
  -passes=irproof-audit -disable-output diamond.ll
```

The function pipeline name is `irproof-strength`; the module adaptor is `irproof-pipeline`; the JSON analysis pipeline is `irproof-audit`.

## Browser checks

Open `demo/IRProof.html` directly for offline use. For module development, serve the project with `python -m http.server 8000` and open `/demo/`. The portable root `index.html` can be served by any static HTTP server.

`tests/ui/smoke.cjs` accepts an existing Chrome headless executable through `CHROME_EXECUTABLE` and the installed `playwright-core` package. It checks case filters, raw output, graph selection, loop and SSA edges, 128-bit input, JSON export, keyboard tabs and mobile overflow. The captured checks used Chromium 151.0.7922.34 and Playwright 1.62.1. Browser automation is a development dependency; the workbench itself has none.

## Technical report source

The four-page report is a snapshot of the supplied capture. `scripts/render_report.py` regenerates it with the optional dependency in `requirements-report.txt` and DejaVu Sans/Mono fonts at the standard Linux font path. Its snapshot guard rejects evidence with different verdict counts.
