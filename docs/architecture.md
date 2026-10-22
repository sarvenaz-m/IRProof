# Architecture

The project separates compiler work, evidence collection and presentation. A browser interaction cannot manufacture or change a validator verdict.

## Compiler layer

`StrengthReductionPass` is an optional function pass for LLVM 23's New Pass Manager. It takes a snapshot of the original binary instructions, rewrites supported scalar cases and erases replaced instructions after updating their uses. Newly inserted instructions are not revisited during that run.

`APInt` is used for constant inspection rather than a machine-sized integer. A positive power-of-two multiplier becomes `shl`; unsigned division becomes `lshr`; unsigned remainder becomes `and`. The signed sign-bit multiplier is excluded. Existing `nsw`, `nuw` and `exact` flags are transferred only on paths with corresponding semantics. The signed bias addition receives no new overflow flag.

Signed division has four paths: divide by one, exact division, a provably nonnegative operand, and the general bias expansion. The general expansion conservatively freezes an operand before duplicating it if its definedness is not established. DominatorTree, AssumptionCache, ValueTracking and a local DomConditionCache support the nonnegative path. Branch-derived facts are consulted only for a defined operand. Removed values are also removed from the local condition cache.

The pass preserves CFG analyses. It does not claim preservation of every analysis affected by instruction changes. `-verify-each` checks the generated module during the recorded runs.

`AuditPass` is a required, read-only module pass. It obtains function analyses through the module-to-function proxy and emits JSON for blocks, instructions, flags, uses, immediate dominators, loop depths, CFG edges and SSA edges. Stable IDs are based on traversal order. The JSON is a diagnostic view; the original LLVM modules remain authoritative.

`irproof-gen` uses LLVMContext, Module, IRBuilder and the LLVM verifier to construct three specimens. The diamond uses an explicit PHI at the merge. The loop has index and accumulator PHIs with a backedge. Arguments, widths, divisors and scenario names are checked before generation.

## Validation layer

`scripts/irproof.py` invokes tools with argument arrays and no shell. It retains stdout and stderr, the return code, elapsed wall-clock time and the command. A per-case wall-clock budget terminates an unfinished subprocess.

Pass cases compare the original module with the emitted target. Explicit src/tgt regressions are separated with LLVM's own `llvm-extract`, then renamed consistently and checked in two-file mode. This preserves referenced declarations and attributes. Alive2's one-file pair mode omits a summary, so it is not used by the runner.

A verdict comes from a complete, recognized summary. One completed proof with a successful process exit is required for `proved`. Refutations, failed proofs, unsupported instructions, signals, syntax errors and empty summaries have separate paths. The manifest's expected result is a test oracle only; it never supplies the displayed verdict.

The evidence chain records hashes for the original case, checked source, checked target and raw execution record. `verify_evidence.py` checks those relationships, the four upstream file hashes, audit inputs and the patch hash. This establishes file consistency, not independent mathematical verification or a cryptographic signature.

## Presentation layer

The interface uses native JavaScript modules, local variable fonts, CSS and SVG. It has no external runtime dependencies. A single-file export embeds its fonts, code, styles and captured data; its content security policy blocks network connections. The source modules remain separate for maintenance.

Filters and search operate on captured cases. Graph topology is supplied by the audit; layout is computed by the renderer. The input lab uses BigInt, checks the selected signed range, and makes no claim to execute LLVM semantics. Text from tool output is escaped before it reaches the page. Tabs and graph nodes support keyboard operation, and reduced-motion preferences are honored.

## What belongs to this project

The original contribution is the pass, frontend specimens, audit format, curated original cases, runner, provenance checks, viewer, and an LLVM-23 compatibility patch for the pinned validator. LLVM, Alive2 and Z3 supply the underlying compiler and verification machinery. The arithmetic identities are established techniques. No upstream acceptance or new theoretical result is claimed.

## Presentation

The viewer uses a warm ivory surface, graphite text, muted petrol actions and clay accents. Semantic CSS tokens in `demo/assets/style.css` keep controls, syntax, plots and graph states consistent. Verdicts retain their written labels and icons as well as their distinct colors. Local fonts and the self-contained export keep the same appearance offline. The report and repository wordmark share this palette.
