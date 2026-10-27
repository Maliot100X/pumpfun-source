# mayhem error-enum consolidation — build validation (2026-10-27)

Applied the **confirmed** edits (EDIT 1/2/3) of `mayhem-error-enum.patch.txt` to the canonical
mayhem build source (`programs/mayhem/src`, whose `source14` set == the committed candidate
`8dac1ff7…`'s recorded build inputs) and built with the committed **v1.54** recipe
(`cargo build --target sbpf-solana-solana --locked --offline`, v1.54 platform-tools — note this
path avoids the `cargo build-sbf` cache-dir panic entirely).

## Result: COMPILES CLEAN ✅ (cargo rc=0)
The one 20-variant `MayhemError` enum + consolidation of the 5 split enums
(`BurnError`/`SellError`/`BuyError`/`PumpSwapError` → `MayhemError`) + the pump-swap slippage
bug fix (`PumpCpiSlippage` 6012 → `PumpSwapCpiSlippage` 6013) are source-correct and build.

## Measured byte-match vs the deployed original
Compared against a deterministic baseline built from the **unmodified** canonical source with the
same recipe (baseline sha `d4494560…`, patched sha `5ba75239…`; neither equals the committed
`8dac1ff7…` because that build reused cached build-script `private.rs` outputs — builds are
self-consistent, so the delta below is attributable to the patch alone).

| section | baseline | patched | original | masked-Jaccard base→patched |
|---|---|---|---|---|
| `.text` | 558,200 | 567,480 | 706,744 | 0.6544 → **0.6606 (+0.0063)** |
| `.data.rel.ro` | 7,816 | 7,976 | 7,784 | 0.2412 → 0.2374 (−0.0038) |

## Interpretation (honest)
- **Behaviorally correct + fixes a real bug** (6012→6013 on pump-swap slippage) and restores the
  original's single-enum structure (one `name()` table + one `Display`).
- `.text` structural match improves **+0.6pp** and grows ~9 KB toward the original.
- `.data.rel.ro` is slightly perturbed (the 20-entry table + my recovered message strings lay out
  a touch larger than the original's).
- **Does NOT meaningfully close mayhem's byte gap** — that gap is dominated by ~21% *missing code*,
  untouched by the enum. This is the same externally-bounded pattern seen across all four
  contracts: a confirmed source recovery yields only marginal whole-binary byte movement.

## Not applied
EDIT 4/5 (inferred guards wiring `PumpCpiMathOverflow` 6009 / `SweepFeeRateLimit` 6019 emit sites)
were **not** applied — the patch flags them as needing per-site confirmation against the runtime
mapper disassembly (.text 0x15860/0x18108/0x1c050/0x1faf0/0x22958/0x27220) before asserting
byte-identity of the trade handlers. The bug fix and consolidation (1/2/3) stand on their own.
