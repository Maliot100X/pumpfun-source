# fees-final lane progress (continuation notes)

Lane: fees-final. Branch claude/fees-final-20261027. Baseline parent: research/fees-readonly-order-recovery
(origin/main e0f8fa903 and later; rebased onto 25a70a642).

## Environment (reproduced)
- Container `claude-fees-final-build` from image localhost/codex-relay-build-deps:20261027, --cpus=2 --memory=3g, --network none.
  Mounts: ~/.cargo/registry -> /cargo/registry (ro); SP/lanes/fees-final/out/work -> /work; SP/lanes/fees-final/target -> /work/target.
- SDK: Linux platform-tools v1.44 (rustc 1.79.0-dev), APFS clone of REPO/work/amm-linux-v144-20261027/sdk at out/work/sdk;
  all 2,764 files hash-identical to the SDK the frontier container mounted.
- Warm target: APFS clone of REPO/work/fees-next-trial/target (deps anchor_lang-ed826685d5adc9b5, anchor_spl-6b93a8211eb72bca).
- Controller: out/tools/build.py REL (holds sbf 6-slot and podman 2-slot locks). Measurement: out/tools/measure.py (window_map normalizer).

## Step 1: frontier reproduction (done)
`verify.py --materialize` -> out/work/next633/data578-qualified; build.py next633/data578-qualified:
stripped 264fe2ec07e1492225fdfd03488d023c17795df6d7c9ec4dc0bcbd03a89d9a08, symbols 852ef570ca6d735bea404e95ba96caecf20e73e7c2db8e33a359aac66462a3e3
(identical to builds/candidate and builds/repeat). Measure: 578 normalized / 198 raw-local / 431 unique pairs; 7 unmatched originals
(76384, 120816, 137280, 147944, 163920, 243184, 249264) + 1 extra candidate (DonationFeePdaCreated::data, 648 B).

## Step 1b: parent moved to research/fees-program-id-references (origin/main 560c452e8)
Materialized to out/work/next641/id578-program-ids-qualified (+ vendor at out/work/next637/vendor/used-public).
Rebuilt in lane container: stripped 0d7bde7b97959ca45a32aa1a3b350188afb120153637de401ae02ac4307b1de3,
symbols af4c0e7c6e4d6215ac5fdac73df3d33252d74c3b0d6d589de97dd28e28d53c0b (identical to the packet).
Note: `--emit=link,llvm-ir` changes .rodata order under the qualified linker script (normalized code unchanged);
use IR emission only as a diagnostic, never for candidate artifacts. Relabeling the source tree path is byte-neutral.

## ATA (243184) mechanism, proven by IR surgery + native llc (out/tools/surgery_ata.py, objfn.py)
- Native macOS llc (platform-tools v1.44, LLVM 18.1.7) on rustc's optimized IR reproduces the candidate ATA body
  exactly: `llc -O3 -march=sbf -mattr=+store-imm,+jmp-ext -relocation-model=pic -function-sections -data-sections`.
- Only difference vs original: invoke-result branch `jeq +1; ja err` (orig) vs `jne err` (cand).
- Surgery B: re-insert the if-internal error-exit join (require!-error + invoke-error preds) right after the invoke
  block, containing PHIs + one llvm.lifetime.end -> llc output 6080 B, normalized-EQUAL to original 243184.
- Surgery C (same join, PHIs only, no lifetime marker) -> CodeGenPrepare removes it -> 6072 B (candidate shape).
- Single-predecessor variant (A) is merged by CGP -> 6072 B.
=> The original IR had a non-empty (lifetime-marker) exit-join block between the invoke check and the success
   block at ISel: a memory local whose StorageDead lies on the shared if-internal early-exit path.

## Step 2: parent research/fees-social-claim-v2-recovery (origin/main 894d562e5+), Withdraw composed -> w580
- Parent materialized at out/work/next644/social-claim-v2-qualified; rebuilt exactly (stripped 6cc20478..., symbols 13e2d199...).
  Parent measure: 579 / 198 / 432 pairs.
- Composition c2/w580 = parent + upstream fees-withdraw-tuple-ownership-source overrides `instructions/withdraw.rs` and
  `withdrawal.rs` only (packet mod.rs NOT taken: it predates the readonly declaration order). ordered.ld unchanged.
- Result: 580 normalized / 198 raw-local / 433 pairs, gained [249264], lost none; rodata 21,079 equal; 105 Source records equal.
  stripped ca7f3c9711fa3694c6d57399efc9a3d36ae6183757c29e20034c3f298eb0ac81, symbols 08c8b0d3b6e491886c63b283823072391201e8843496730b0f1b879a66e93125.
- Runtime: fees_validate_all 17,331 cases / 18 suites / 0 mismatches.
- (Earlier, on the program-ID parent, the same composition c/w579 gave 579/198, repeat identical, 17,331/0.)

## ATA screens (native macOS IR + llc, out/ata/results.jsonl; all on the w580 source)
base 6072 (diff@2200 = the branch); inline-ix 6072 (frame differs, diff@24); deref-eq 6072 (@2200);
system-id-call 6072 (@2200); nested-create-block 6072 (@2200). helper-plain: variant text bug, not run.
Native macOS full build of w579 gives 575 normalized: the 4 sysroot type_id windows differ with macOS target libs; all
user-code shapes equal -> native is fine for IR screening, container is required for candidates.

## Next steps (ATA)
Need IR where the if-internal error-exit join keeps a lifetime.end. Drop-tree sharing makes StorageDead(expected)
shared by every `return` in its scope, so plain scoping cannot produce expG. Candidates to try: forms where the
ConstraintSeeds check and post-if validation do not use the function's return drop tree (expression-valued if/else,
tail helper), or an if-let/match whose scrutinee temp is a surviving alloca with a coloring-neutral range.
