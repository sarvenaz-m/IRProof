#!/usr/bin/env python3
"""Build the original, deterministic IRProof regression corpus."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def build():
    cases = []
    folder = ROOT / "corpus" / "original"
    folder.mkdir(parents=True, exist_ok=True)

    def add(key, title, category, bits, body, explanation, *, target=None,
            expected="proved", args=None, declarations="", operation="", divisor=None):
        args = args if args is not None else f"i{bits} %x"
        def fn(name, text):
            return f"define i{bits} @{name}({args}) {{\nentry:\n" + "\n".join("  " + s for s in text.splitlines()) + "\n}\n"
        ir = declarations + fn("src" if target is not None else "specimen", body)
        if target is not None:
            ir += "\n" + fn("tgt", target)
        path = folder / f"{key}.ll"
        path.write_text(ir)
        cases.append(dict(id=key, title=title, category=category, bits=bits,
                          path=path.relative_to(ROOT).as_posix(), mode="pair" if target is not None else "pass",
                          expected=expected, explanation=explanation, operation=operation,
                          divisor=divisor, origin={"kind": "original", "name": "IRProof regression corpus"}))

    for bits, d in [(8, 2), (16, 4), (32, 8), (64, 16), (128, 64)]:
        add(f"sdiv-{bits}-{d}", f"Signed division · i{bits} / {d}", "signed", bits,
            f"%q = sdiv i{bits} %x, {d}\nret i{bits} %q",
            "A sign-dependent bias preserves rounding toward zero. The expansion freezes an unconstrained operand once before reusing it.",
            operation="sdiv", divisor=d)
    add("sdiv-defined", "Defined input, smaller expansion", "signed", 32,
        "%q = sdiv i32 %x, 8\nret i32 %q",
        "The noundef parameter makes a freeze unnecessary; the rounding correction is still required for negative inputs.",
        args="i32 noundef %x", operation="sdiv", divisor=8)
    add("sdiv-exact", "Exact division keeps its contract", "signed", 32,
        "%q = sdiv exact i32 %x, 4\nret i32 %q",
        "Exact division requires discarded bits to be zero. An exact arithmetic shift carries the same restriction.",
        operation="sdiv", divisor=4)
    add("sdiv-known-nonnegative", "Known bits remove the correction", "signed", 32,
        "%positive = and i32 %x, 2147483647\n%q = sdiv i32 %positive, 8\nret i32 %q",
        "ValueTracking proves the dividend nonnegative from its sign mask, allowing one logical shift.",
        operation="sdiv", divisor=8)
    for bits, d in [(8, 8), (32, 16), (64, 9223372036854775808)]:
        add(f"udiv-{bits}", f"Unsigned division · i{bits}", "unsigned", bits,
            f"%q = udiv i{bits} %x, {d}\nret i{bits} %q",
            "Unsigned division by a power of two is a logical right shift, including a divisor with its high bit set.",
            operation="udiv", divisor=str(d))
    add("udiv-exact", "Exact unsigned division", "unsigned", 32,
        "%q = udiv exact i32 %x, 16\nret i32 %q",
        "The exact flag is transferred to lshr so the target does not silently lose the division contract.", operation="udiv", divisor=16)
    for bits, d in [(8, 16), (32, 64)]:
        add(f"urem-{bits}", f"Remainder as a bit mask · i{bits}", "unsigned", bits,
            f"%r = urem i{bits} %x, {d}\nret i{bits} %r",
            "A mask retains exactly the low bits of an unsigned remainder by a power of two.", operation="urem", divisor=d)
    for key, flags in [("mul-wrap", ""), ("mul-nsw", "nsw "), ("mul-nuw", "nuw "), ("mul-both", "nuw nsw ")]:
        add(key, "Multiply by eight" + (" · " + flags.strip() if flags else " · modular"), "overflow", 32,
            f"%p = mul {flags}i32 %x, 8\nret i32 %p",
            "Multiplication by a positive power of two becomes shl. Existing overflow flags are preserved; new flags are never invented.", operation="mul", divisor=8)
    add("mul-signbit-guard", "Sign-bit multiplier stays unchanged", "overflow", 8,
        "%p = mul nsw i8 %x, -128\nret i8 %p",
        "The sign-bit constant is a negative signed multiplier. The pass deliberately leaves this case untouched because shl nsw has a different overflow domain.")
    add("neutral-elements", "Remove neutral operations", "semantics", 32,
        "%a = add nsw i32 %x, 0\n%b = and i32 %a, -1\n%c = xor i32 %b, 0\nret i32 %c",
        "Three neutral operations disappear. The original SSA operand remains the result.")
    add("signed-minus-three", "The -3 / 2 counterexample", "signed", 32,
        "%q = sdiv i32 -3, 2\nret i32 %q", args="",
        target="%q = ashr i32 -3, 1\nret i32 %q", expected="refuted",
        explanation="Signed division returns -1; an arithmetic right shift returns -2. Replacing the former with the latter changes the result.")
    add("signed-naive-shift", "A shift loses signed rounding", "signed", 32,
        "%q = sdiv i32 %x, 2\nret i32 %q",
        "Negative odd dividends expose the missing rounding correction.",
        target="%q = ashr i32 %x, 1\nret i32 %q", expected="refuted", operation="sdiv", divisor=2)
    add("signed-remainder-mask", "Signed remainder is not a mask", "signed", 8,
        "%r = srem i8 %x, 8\nret i8 %r",
        "A negative signed remainder cannot be represented by an unsigned low-bit mask.",
        target="%r = and i8 %x, 7\nret i8 %r", expected="refuted", operation="srem", divisor=8)
    add("introduced-overflow", "An invented nsw flag changes behavior", "overflow", 8,
        "%p = mul i8 %x, 8\nret i8 %p",
        "Modular multiplication is defined for overflowing inputs. Adding nsw makes some of those inputs poison.",
        target="%p = shl nsw i8 %x, 3\nret i8 %p", expected="refuted")
    add("introduced-exact", "An invented exact flag rejects inputs", "overflow", 32,
        "%q = udiv i32 %x, 8\nret i32 %q",
        "A logical shift marked exact is poison when any discarded bit is nonzero. The source imposes no such restriction.",
        target="%q = lshr exact i32 %x, 3\nret i32 %q", expected="refuted")
    add("signbit-nsw-mismatch", "A negative multiplier changes nsw", "overflow", 8,
        "%p = mul nsw i8 %x, -128\nret i8 %p",
        "For x = 1, multiplying by -128 is representable, but shifting 1 left by seven with nsw is poison. The pass excludes this rewrite.",
        target="%p = shl nsw i8 %x, 7\nret i8 %p", expected="refuted")
    add("undef-reuse", "Duplicating undef changes multiplication", "semantics", 8,
        "%p = mul i8 %x, 2\nret i8 %p",
        "Multiplication by two always has a zero low bit. Independent undef choices in two add operands can produce an odd result. A freeze would couple those choices.",
        target="%p = add i8 %x, %x\nret i8 %p", expected="refuted")
    add("atomic-boundary", "Atomic memory reaches a model boundary", "limits", 32,
        "%old = atomicrmw add ptr %p, i32 1 seq_cst\nret i32 %old",
        "This case probes the validator's support for atomic memory. Unsupported semantics must remain unknown rather than count as a proof.",
        args="ptr %p", target="%old = atomicrmw add ptr %p, i32 1 seq_cst\nret i32 %old", expected="unknown")

    generated = ROOT / "corpus" / "generated"
    for scenario, title, note in [
        ("divide", "IRBuilder emits a signed divide", "The source is emitted by the C++ frontend and its exact pass output is checked."),
        ("diamond", "Branch facts guide the rewrite", "The noundef input and dominating comparison justify a logical shift in the nonnegative arm. The negative arm keeps the correction.")]:
        p = generated / f"{scenario}.ll"
        if p.exists():
            cases.append(dict(id="frontend-"+scenario, title=title, category="frontend", bits=32,
                              path=p.relative_to(ROOT).as_posix(), mode="pass", expected="proved", explanation=note,
                              origin={"kind":"generated", "name":"IRProof C++ IRBuilder frontend"}))
    p = generated / "diamond.ll"
    if p.exists():
        unstable = folder / "sdiv-unstable-branch.ll"
        unstable.write_text(p.read_text().replace("noundef ", ""))
        cases.append(dict(id="sdiv-unstable-branch", title="Branch knowledge needs a defined input", category="semantics", bits=32,
                          path=unstable.relative_to(ROOT).as_posix(), mode="pass", expected="proved",
                          explanation="An unconstrained input cannot safely borrow sign information from a separate use in a branch. Both divisions retain stable bias expansions.",
                          origin={"kind":"original", "name":"IRProof regression corpus"}))

    # These are unmodified, pinned third-party files. License and file hashes
    # are tracked separately in corpus/upstream/provenance.json.
    upstream = ROOT / "corpus" / "upstream" / "provenance.json"
    if upstream.exists():
        for item in json.loads(upstream.read_text())["files"]:
            cases.append({**item, "mode": "pair", "category": "semantics", "bits": 32,
                          "origin": {"kind": "upstream", "name": "Alive2", "revision": json.loads(upstream.read_text())["revision"]}})
    manifest = {"schemaVersion": 1, "version": "1.0.0", "cases": cases}
    (ROOT / "corpus" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    print(f"Wrote {len(build()['cases'])} cases")
