# Fees lane `fees-final` (2026-10-27)

Parent: [Social claim-v2 recovery](../fees-social-claim-v2-recovery/README.md) (579/585 normalized,
198 raw-local). This packet composes the upstream
[Withdraw tuple-ownership source](../fees-withdraw-tuple-ownership-source/README.md) onto that parent
in the qualified linker layout, and records a proven compiler mechanism for the associated-token
validator (original `243184`).

## Result

| | Parent (`social-claim-v2-qualified`) | This candidate (`w580`) |
| --- | ---: | ---: |
| Normalized original windows | 579 / 585 | **580 / 585** |
| Raw-local original windows | 198 | 198 |
| Unique pairs | 432 | 433 |
| Matched original text bytes | 742,520 | 750,520 |
| Unmatched original windows | 6 | 5 |
| `.rodata` (21,079 bytes) equal | yes | yes |
| Global Source records equal | 105 / 105 | 105 / 105 |

Newly matched window: **`249264` Withdraw (8,000 bytes)**. Lost windows: none (normalized or raw).
Remaining unmatched originals: `76384` ExtendFeeConfig, `120816` SweepBuyback,
`147944` CrankDonationFeePda, `163920` CreateDonationFeePda, `243184` associated-token validator.
The extra compiled `DonationFeePdaCreated::data` helper (648 bytes) remains.

The composition copies exactly two files from the Withdraw packet's overrides
(`instructions/withdraw.rs`, `withdrawal.rs`). The parent's `instructions/mod.rs` is kept, because the
packet's `mod.rs` predates the readonly-order recovery and would revert its `admin`/`fee_sharing`
declaration order. The parent's `ordered.ld` is used unchanged; all compiled input sections still
match its selectors (readonly payload, Source records and raw-local set are unchanged).

| Artifact | SHA-256 |
| --- | --- |
| Stripped (`builds/w580/candidate.so.gz`) | `ca7f3c9711fa3694c6d57399efc9a3d36ae6183757c29e20034c3f298eb0ac81` |
| Symbols (`builds/w580/symbols.so.gz`) | `08c8b0d3b6e491886c63b283823072391201e8843496730b0f1b879a66e93125` |

Both are produced by the parent recipe (Linux platform-tools v1.44, `cargo rustc --release
--locked --offline --jobs 1`, `-Zremap-cwd-prefix=`, qualified `ordered.ld` through `linker.sh`,
v1.52 `llvm-objcopy --strip-all`). A second build from a fresh label is byte-identical
(`builds/w580-repeat.json`). The full 18-suite differential (`scripts/fees_validate_all.py`) passes
**17,331 cases with 0 mismatches** against the original (`runtime/w580-summary.json`).

Measurement uses the repository normalizer (`research/fees-composed-frontier188/window_map.py`):
`tools/measure.py` (counts, gained/lost sets) and `tools/datacheck.py` (readonly bytes, Source records,
direct-call agreement). Outputs are in `measurement/`.

## Associated-token validator recovered with stable Rust (`ata-letelse`, 581 / 200)

On top of w580, one line of `instructions/fee_sharing/mod.rs` turns the creation `if` into a labeled block whose
guard is a `let`-`else` (Source lines 273/278/299/306 unchanged; the old closing brace closes the block):

```rust
    'create: { let true = associated_account.owner == &anchor_lang::system_program::ID else { break 'create };
```

| | w580 | ata-letelse |
| --- | ---: | ---: |
| Normalized | 580 | **581** (gained `243184`, 6,080 bytes) |
| Raw-local | 198 | **200** (gained `235304`, `236240`) |
| Unique pairs | 433 | 434 |
| Lost windows | - | none |

`.rodata` (21,079 bytes) and all 105 Source records stay equal. Stripped
`02a04fa4cde2fbf28d59bab4aeec1a585c5f1f7aa1d6248cd6c5d5997b36db06`, symbols
`fb2e04e0a3234b22c4ac1f3bac672a2f436b78ec9ec598819bab7ec4d527da3c` (`builds/ata-letelse/`).
Upstream main already matches this window with a `try` block (`#![feature(try_blocks)]`,
`research/fees-ata-prefix-integration`); this form needs no feature flag and is an independent confirmation of the
mechanism below, not an extra window for the current 582 frontier.

Why: with `if cond { .. }` the condition temporary lives across the body, so the `require!` error path's first exit
block is the empty `StorageDead(cond)` node and SimplifyCFG deletes it; the success block then follows the invoke
test and ISel emits `jne err`. With `let true = cond else { break 'create };` the temporary dies before the body,
the `require!`/`invoke?` exits go straight to the non-empty `StorageDead(expected)` return join, that block keeps
the slot after the invoke test, and ISel emits the original `jeq ok; ja err`. Native IR screens (`ata-mechanism/
native-screens.jsonl`): `if cond {} else { break 'create; }` also matches; `if !cond { break }` flips the owner-check
polarity (6,072 B); closure/nested-fn isolation reshapes the body (6,288 B).

## Associated-token validator (`243184`): the IR-level proof

The candidate body (6,072 bytes) equals the original (6,080 bytes) except at the `invoke` result
test: original `jeq r2,r1,+1; ja err` versus candidate `jne r2,r1,err`. Native platform-tools
v1.44 `llc` reproduces rustc's backend exactly on rustc's optimized IR (the unmodified IR gives the
candidate body), so single-block IR edits isolate the cause (`ata-mechanism/surgery-results.json`,
`tools/surgery_ata*.py`, `tools/surgery_newalloca.py`):

- **Exact matches (6,080 bytes, normalized-equal to the original):** re-insert the if-internal
  error-exit join (predecessors: the `require!(create_if_missing)` error path and the `invoke` error
  path) immediately after the invoke block, containing the error PHIs plus one lifetime end that does
  not change any stack live range: either a redundant end of an already-dead temporary (`expB`) or
  the end of `expected` on those two return paths only (`expG`).
- **Negative controls:** the same join with PHIs only is deleted by CodeGenPrepare (`expC`, 6,072);
  a single-predecessor join is merged by CodeGenPrepare (`expA`, 6,072); starting `instruction`'s
  lifetime before the `require!` (`expD`), ending `expected` after the whole `if` on all paths
  (`expE`), or adding any new 1/8/24/32-byte local spanning the `if` (`expF*`) all change frame offsets.

Mechanism: SBF has no `reverseBranchCondition`. When the success block is the IR-next block,
SelectionDAG inverts the test (`jne err`) and MachineBlockPlacement must keep the fallthrough. When a
non-removable block sits between the test and both successors, ISel emits `jeq ok; ja err`;
placement then moves `ok` next and cannot reverse the branch, leaving the original `jeq +1; ja`.
In rustc's codegen order that slot is the block created by the `require!` error path's exit
(MIR `StorageDead(_27)`), which is empty in the candidate and removed by the first SimplifyCFG.
So the original source gives that exit join real IR content without changing frame layout.
MIR drop-tree sharing explains why simple scoping changes cannot do this: every `return` in
`expected`'s scope shares one `StorageDead(expected)` node. Native IR screens of four further source
forms (instruction as call temporary, `*owner == ID`, `System::id()` comparison, nested create block)
all keep the success block adjacent (`ata/results.jsonl` summary in PROGRESS.md).

## Verify (no rebuild)

```sh
python3 -B research/claude-fees-final-20261027/verify.py
python3 -B research/claude-fees-final-20261027/verify.py --materialize /abs/new/w580
```

The verifier decompresses both ELFs, checks their SHA-256, re-measures 580/198 with the repository
normalizer against the parent's published symbols ELF, and checks `.rodata` and the 105 Source records.

## Reproduce

```sh
python3 -B research/fees-social-claim-v2-recovery/verify.py --materialize /abs/parent
cp research/claude-fees-final-20261027/overrides/programs/pump-fees/src/instructions/withdraw.rs \
   /abs/parent/programs/pump-fees/src/instructions/withdraw.rs
cp research/claude-fees-final-20261027/overrides/programs/pump-fees/src/withdrawal.rs \
   /abs/parent/programs/pump-fees/src/withdrawal.rs
# build with the parent's controller recipe (see tools/build.py for the container form used here)
python3 research/claude-fees-final-20261027/tools/measure.py candidate-symbols.so
```

`source.patch` is the exact diff against the materialized parent. `tools/` holds the lane's build
controller (container `claude-fees-final-build`, shared slot locks), native diagnostic driver, IR
block lister, disassembler and surgery scripts. Whole-ELF and capture equality remain false.
