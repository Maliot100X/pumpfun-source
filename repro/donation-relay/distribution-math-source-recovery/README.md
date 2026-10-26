# Relay distribution math and compilation reachability

Whole captured ELF identity remains unachieved. Acceptance requires reconstructed Rust builds. The selected build matches **464 of 492 complete normalized original windows**, including 86 raw matches, leaving 28 unmatched. It gains windows 69 and 113 without losing any normalized match from the preceding 462-window checkpoint. Normalization still masks only direct-call displacements and relocated immediate words; register, branch and stack differences remain failures. Raw matches decrease from 93 to 86 as layout changes.

The entire 2,224-byte remainder-allocation function 113 now matches. It allocates floor shares from u128 products, retains stable decreasing remainder order, and increments the selected original indices. Empty inputs and checked allocation-sum, total-minus-sum and increment failures remain. The quotient narrows to u64 as observed. The remainder uses `% 10000`; the final loop indexes the sorted remainder vector over `0..min(left, len)`. This recovers the captured positive-count loop without adding a second bounds-panic edge.

`math_evidence.py` verifies the entire body, all 14 actual direct callees, and their recursively closed normalized direct-call shapes. The arithmetic adapter calls resolve to actual `__multi3` and `__udivti3` symbols, rather than assuming that any normalized adapter is interchangeable. It also rechecks the recovered 440-byte RawVec growth function 69 and its actual use by the math function.

The former arena/runtime modules are no longer declared in the compiled crate. `codec.rs` exposes only constants and wire types, and the obsolete manual mint decoder is no longer compiled. Historical files remain available as analysis history. Both independent compiler dep-info records identify **27 reachable local Rust files**; the complete preserved inventory has **49 Rust/config files**. These are different counts. A topology-only trial isolates recovery of window 69 before the distribution-math edits. Cargo.toml and Cargo.lock remain unchanged.

The shared distribution worker retains owned account-field destructuring and now follows the captured indexed recipient loop. It snapshots program/mint keys, validates recipient owner, mint and token program, and only then indexes the amount. Transfers use the decoded account's AccountInfo. Its current 8,208 bytes still differ from the captured 8,264 bytes: near size does not count as a match. All eleven generated business wrappers, the dispatcher, SDK entrypoint, three settlement parsers/programs/exits, receipt builder and swap balance helper retain their complete normalized matches and actual checked targets.

Module reachability also changes optimization of the still-unmatched mint-policy function: it is now 4,016 bytes versus the captured 3,440. `policy-residual.json` retains every normalized instruction difference, including the candidate-only tail. This is a regression in that function's shape, not a lost complete match. Other business bodies, account-close helper 282, signed-CPI helper 300, resize specialization 332, indirect/data/allocator behavior and complete ELF relocations/layout remain open. All 28 unmatched original windows are listed in `remaining-windows.json`. The all-contract Rust-only goal remains active.

Nine measured source trials plus selected and independent repository-path builds are retained: **11 successful Rust builds**, with no source compile failures. Both selected paths reproduce exactly:

- Stripped: 813,912 bytes, SHA-256 `8c3de0056c65eddb5f4cd561377077e05d2a63362613916d6b4404e59e0d7640`.
- Unstripped: 923,168 bytes, SHA-256 `82692119c6d3fa66c0a74d2a890567e6f7f794a74c877b6e6fa6c01c7b73a930`.
- Capture: 830,448 bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

All **536 named runtime records, representing 534 unique input fixtures**, were rerun on the selected output. The unchanged independent verifier checks fixtures, canonical PDAs, transaction privileges, 3,107 cryptographic signature fields, executable bindings, errors, CPI sequences, effects and rollback. The sole duplicate group remains the three existing just-swap baseline/readonly labels. No successful fixed-relayer/Jupiter settlement, address substitution or privilege substitution was executed. These finite parser/rejection cases do not establish privileged-body, arbitrary-input, allocator or security acceptance. The comparator still excludes only compute-metering lines and executable-image bytes.

The registry audit checks 177 packages, 4,055 files and 37,402,916 bytes against pinned archives. The actual 34 program and 77 Anchor framework error implementations are rederived. No assembly input, captured executable fragment, ELF patch, dummy caller, forced-inline attribute, unsafe code or broader normalization was introduced.

```sh
python3 -B repro/donation-relay/distribution-math-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/distribution-math-source-recovery/receipt_verify.py --runtime
```

These commands rederive sealed evidence without VM execution; the retained runners generated the VM observations. Historical packets remain sealed. Shared HEAD/index and unrelated work remain preserved. Hosted run 40287185890 for the previous publication failed Pump source-binding assertions; this local proof does not establish green hosted CI.
