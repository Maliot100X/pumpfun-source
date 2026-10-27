# Recovery findings — parallel audit + byte-closing session (2026-10-27)

Review bundle of **successful** findings from a parallel-subagent pass over the four core
contracts. All artifacts here are documentation + staged patches under a non-pinned
`research/` path — **no active source, scripts, or pinned assets are changed**, so this
should clear the pass-27 guard and is safe to review/merge independently of the
per-contract build pipelines.

## TL;DR
- **Behavioral reconstruction is 100% complete and oracle-validated on all 4 contracts** —
  0 differential mismatches across **59,570** replay cases (pump 15,052 · amm 17,462 ·
  fees 17,461 · mayhem 9,595), full Anchor dispatch (56/56 · 38/38 · 31/31 · 25/25).
- **Whole-binary byte-identity is 0/4 and externally bounded** — confirmed three independent
  ways (per-contract audits, an exhaustive compiler sweep, a 5-agent RE workflow) and by the
  repo's own `docs/COMPLETION.md`. Closing it needs inputs we don't hold: the authentic
  original source, the exact Linux build environment, and (for `pump_amm::create_config`) a
  deploy admin private key.

## ⭐ Headline: a real mayhem bug + the recovered error enum
The original mayhem compiles **one 20-variant `#[error_code]` enum** (codes 6000–6019),
confirmed three ways from `deployed.so` (the `name()` pointer array at `.data.rel.ro`
0xb1a94 with a `0x14`=20 length header, the `Display::fmt` dispatch, and the reconstruction's
own discriminants). The reconstruction **split it into 5 enums**, so it emits 5 name tables +
5 `Display` fns where the original has one.

**Bug:** the pump-swap paths emit `PumpCpiSlippage` (**6012**) where the original uses
`PumpSwapCpiSlippage` (**6013**) — an on-chain-observable wrong error code. Consolidation +
fix patch: [`recovery/mayhem-error-enum.patch.txt`](recovery/mayhem-error-enum.patch.txt).

The patch targets `programs/mayhem/src/*` — **confirmed to be the canonical build source** via
the committed candidate's `recorded-build-inputs.json` / `source14.json` (the 12-file tree,
not the stray 18-file root `src/`). **Now compile-validated** on the committed v1.54 recipe
(builds clean; measured byte delta in [`recovery/mayhem-enum-validation.md`](recovery/mayhem-enum-validation.md)):
it fixes the bug and nudges `.text` structural match +0.6pp toward the original, with only
marginal whole-binary movement (mayhem's gap is dominated by ~21% missing code).

## Measured byte win (reproducible)
**fees path-string recovery: 4 → 10 of 20** matching `programs/pump-fees/src/*.rs` strings,
with **zero `.text` regression** (masked-slot Jaccard 0.789938 → 0.789986, `.text` Δ unchanged
−10,232). Mechanic: `#[path="…"] mod <same_name>;` relocation of already-delegated modules —
no body change, no ref edits. Six TIER-0 relocations applied (withdraw, create_donation_fee_pda,
admin_cto_sharing_config, claim_social_fee_pda, buyback/mod, update_fee_shares). Full tiered
plan to 13/20 + the paths that must NOT move (inline admin handlers regress `.text`):
[`recovery/fees-pathstring-restructure.txt`](recovery/fees-pathstring-restructure.txt).

## Compiler sweep (first exhaustive; definitive negative)
`sweep/compiler-sweep-results.jsonl`: built pump & fees across v1.44/1.45/1.46 vs the originals —
byte-match moves **< 0.5 points**, **v1.44 is best** (pump masked-Jaccard 0.754, fees 0.790).
The compiler is not the gap; the originals are Linux-built, so a native rebuild can't byte-match
regardless of version.

## Per-contract audits
Independent read-only audits with exact numbers, closeable-vs-bounded breakdown, and the named
external blocker per contract: [`audits/`](audits/).
- pump `.text` −119 KB (365 unmatched windows: missing helpers).
- pump_amm `.text` +39 KB (monomorphization; `create_config` needs an admin key — not in-repo).
- pump_fees `.text` −10 KB, opcode-mix 0.971, **0 closeable logic windows** (regalloc/scheduling + Location metadata).
- mayhem `.text` −149 KB (21% smaller — partial reimpl; the recoverable error surface is above).

## Other recovery targets (staged, lower confidence)
- mayhem path-string restructure 0→9: [`recovery/mayhem-pathstring.txt`](recovery/mayhem-pathstring.txt).
- pump missing-helper recovery targets (ranked): [`recovery/pump-helpers.txt`](recovery/pump-helpers.txt).
- Consolidated targeting ledger: [`recovery/TARGETING.md`](recovery/TARGETING.md), full handoff: [`recovery/HANDOFF.md`](recovery/HANDOFF.md).

## Build-environment note (saves an hour)
`cargo build-sbf` 2.1.21 panics (`'-' after minor version number`) because
`validate_platform_tools_version` semver-parses every `~/.cache/solana/*` dir name, and the
cross-build dirs (`v1.44-linux-probe`, `v1.48-osx-x86_64`, `v1.49-linux-x86_64`, …) are invalid
semver. Workaround: build with a curated `HOME/.cache/solana` symlinking only clean-named version
dirs. Details in `recovery/HANDOFF.md`.

## What this bundle does NOT claim
Byte-identity for any of the four programs (it is externally bounded). Report progress as
`matched_text_bytes`, `raw_equal_functions`, masked-Jaccard, and the path-string oracle —
never as "bytes to identity."
