# Third-party notices

## LLVM

LLVM is an external build dependency, distributed by the LLVM project under Apache-2.0 with LLVM exceptions. No LLVM source tree or binary distribution is bundled. Official source: https://github.com/llvm/llvm-project

## Alive2

The four files in `corpus/upstream/` are unmodified copies from Alive2 revision `c9af7dbb503878554aefafddba5889ccab237503`. Their original paths and hashes are recorded in `provenance.json`; the applicable MIT license is `corpus/upstream/LICENSE.Alive2`.

The compatibility patch contains modifications to MIT-licensed Alive2 source. Its license is also retained in `third_party/alive2/LICENSE`. No Alive2 binary is bundled. Official source: https://github.com/AliveToolkit/alive2

## Z3

Z3 is an external validator dependency under the MIT license. The isolated bootstrap pins `z3-solver==5.3.1.0`. No solver binary is bundled. Official source: https://github.com/Z3Prover/z3

## Fonts

Work Sans and JetBrains Mono are included as local WOFF2 fonts under the SIL Open Font License 1.1. Their complete notices are in `third_party/fonts/`. The standalone HTML embeds the same font bytes. Font packages: https://www.npmjs.com/package/@fontsource-variable/work-sans and https://www.npmjs.com/package/@fontsource-variable/jetbrains-mono

## Browser testing

The optional smoke script uses the Apache-2.0-licensed Playwright project. Playwright and Chromium are development tools and are not bundled in the workbench. Official source: https://github.com/microsoft/playwright
