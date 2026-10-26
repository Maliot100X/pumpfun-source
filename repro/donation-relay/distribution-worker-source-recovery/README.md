# Relay distribution worker and caller-source reconstruction

Whole captured ELF identity remains unachieved. Acceptance requires reconstructed Rust builds. The selected build matches **465 of 492 complete normalized original windows**, including 86 raw matches, leaving 27 unmatched. It gains worker108 without losing any normalized match from the 464-window checkpoint. Only direct-call displacements and relocated immediate words are normalized; register, branch and stack differences remain failures.

The entire 8,264-byte distribution worker now matches. Its transfer destination clones the original recipient AccountInfo after typed decoding and recipient owner/mint/program validation. This restores the captured account-metadata loads and register/stack use; cloning the decoded wrapper instead gave an 8,208-byte mismatch. Empty amounts still pass recipient validation before the amount lookup. Actual transfer_checked CPIs, signer groups, owned source/mint/program/authority fields, checked index failures and borrowed receipt collection remain.

`worker_evidence.py` decodes all **51 actual direct call targets** and verifies complete normalized callee bodies, including transfer226, fair math113 and receipt81. This does not establish transitive closure: direct callees8 and226 have unmatched transitive shapes, and close282, signed-CPI300 and resize332 remain open. The complete math function113 and its recursively closed 14 direct calls remain matched, as do growth69, all eleven generated business wrappers, the complete dispatcher/SDK entrypoint and the three settlement parser/program/exit layers.

Relocated caller data now independently verifies **five application filename/line/column tuples**. The recipient and amount bounds checks name `programs/contracts/src/tools/distribution/shared.rs` at91:45 and118:54. Math allocation/bounds descriptors name `programs/contracts/src/tools/fair_distribution.rs` at27:32,28:46 and63:45. Pure Rust source is placed at these paths with the observed coordinates. Root-relative `include!` statements preserve the existing Rust namespace and macro line36. An intermediate relative-include trial retains its incorrect `/../` path as a measured control. The preceding application data mismatch is fixed; native vendor sysroot strings still begin `/Users/runner/` whereas the capture uses `/home/runner/`. No raw ELF identity follows from normalized bodies or matching source tuples.

Six source trials plus selected and independent repository-path builds are retained: **eight successful native Rust builds**, no source compile failures in this packet. Compiler dep-info identifies **28 reachable local Rust files** within **50 inventoried Rust/config files**. The source inventory includes preserved obsolete files that no longer compile. Cargo.toml/Cargo.lock remain unchanged. Both selected paths reproduce exactly:

- Stripped: 813,968 bytes, SHA-256 `fb4fcb3a95211ff2b3b4dde34257eb6632876a2d0ad4658fd32d45f159c7d518`.
- Unstripped: 923,224 bytes, SHA-256 `2402f38e6f7863c3f61b195c2b2041252c30552de9f2e9620f6106f212db4c5c`.
- Capture: 830,448 bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

All **536 named runtime records, representing 534 unique input fixtures**, were rerun on this exact selected output. The independent receipt verifier checks canonical fixtures/PDAs/rent, transaction bytes/effective privileges, 3,107 cryptographic signature fields, executable bindings, errors, CPI order, effects and rollback. The original duplicate group remains the just-swap baseline and two readonly labels. No successful fixed-relayer/Jupiter settlement, address substitution or privilege substitution occurred. These finite parser/rejection cases do not establish privileged-body, arbitrary-input, allocator, RefCell or security acceptance. The frozen comparator excludes compute-metering lines and executable-image bytes.

All 27 remaining original windows are explicit in `remaining-windows.json`. Business handlers, mint-policy106 (4,016 versus3,440 bytes), account-close/CPI/resize helpers, indirect/data/allocator behavior and complete relocation/layout identity remain open. The goal still covers all contracts and dependencies. No whole-contract acceptance count rises. No assembly compiler input, captured executable fragment, binary patch, dummy caller, forced-inline attribute, unsafe code or broader normalization is used.

The registry audit checks 177 packages, 4,055 files and 37,402,916 bytes against pinned archives. Actual emitted 34 program and77 Anchor framework error names/messages are independently rederived.

```sh
python3 -B repro/donation-relay/distribution-worker-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/distribution-worker-source-recovery/receipt_verify.py --runtime
```

These rederive sealed evidence without VM execution. Retained runners generated the saved VM observations. Historical packets remain sealed; their --current checks intentionally fail after source advances. Shared HEAD/index and unrelated work remain preserved. Prior hosted run40290390326 failed; this local proof does not establish green hosted CI.
