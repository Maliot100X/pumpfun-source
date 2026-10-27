# Relay SDK dependency and error-path recovery

Whole captured ELF identity remains unachieved. Acceptance requires reconstructed Rust builds. The selected native build matches **476 of 492 complete normalized original windows**, including **107 raw matches**, leaving **16 unmatched**. It gains11 windows from the465-window checkpoint with no lost normalized matches. Normalization still masks only direct-call displacements and relocated immediate words; register, branch and stack differences remain failures.

The measured dependency boundary is Anchor Lang/SPL0.32.1, generated macros0.32.2, solana-invoke0.4.0 and direct Token-2022 8.0.1. This is a source build result, not a claim that the capture authenticates these exact historical version choices. REA's `inspect_rust_binary` result `ev_fbd7f3689f3a3893d60e67f2358b1ec3d92d56c16427096fe7ae2891a035785b` finds no cargo-auditable dependency section and no read-only rustc commit path. Its complete summary and limitations are retained in rea-rust-inspection.json.

The SDK change recovers entire signed-CPI300, close282, resize332, IDL resize172 and Token-2022 helper windows240/242/243/244/344. The pinned sources explain two structural mismatches: solana-invoke borrows the stable instruction layout instead of cloning its vectors; Anchor closes accounts using resize(0). Every recovered body and its actual direct callees are checked, with recursive direct-call shape closure. The complete distribution worker108 and transfer226 now also have recursive direct-call shape closure. This does not prove indirect-call/data behavior or whole ELF identity.

Two application corrections recover complete windows4 and167. Failed share-total admission retains the observed `(sum,10000u32)` compared values, producing the captured1352-byte error helper. SwapReceipt's account macro is placed at captured line5, restoring the entire1120-byte checked decoder. All eleven business wrappers, dispatcher/SDK entrypoint, three settlement parser/program/exit layers, math113, growth69, receipt81 and swap balance91 retain their complete normalized matches.

The remaining original ordinals are56,90,92,93,94,95,96,97,98,99,100,106,109,112,267,351. They include application handlers, CPI builder, cleanup, common donation, mint policy and three boxed-string standard-library type-ID constants. Policy106 remains3440 bytes with three register-choice instruction differences at1360/1368/1376. Reversing fee operands and a boolean predicate were measured and rejected; no broader mask was introduced. All16 remain explicit in remaining-windows.json.

Four source controls plus selected and independent repository-path builds are retained: **six successful native Rust builds**, no source compile failures. Both final paths reproduce exactly:

- Stripped818,088 bytes, SHA-256 `8d6dea7b7b8332809b8dc4581460f658733c0e677e3936c7c1aa7df6bd62eba3`.
- Unstripped926,016 bytes, SHA-256 `ba4f9842888dfd9109753b92e5ab41c176466d9d6cb476ffcf415f8b176c7a74`.
- Capture830,448 bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

Compiler dep-info still identifies28 reachable local Rust files within50 inventoried Rust/config files. The five application caller filename/line/column descriptors remain matched. Native vendor sysroot strings differ from the Linux capture. Captured machine instructions are not compiler inputs; no assembly, binary patches or dummy callers were introduced. The accepted SDK dependency contains its own upstream unsafe implementation; application reconstruction added no unsafe source.

All **536 named runtime records, representing534 unique fixtures**, pass on this exact output. The independent verifier checks canonical inputs/PDAs/rent, transactions/effective privileges,3,107 cryptographic signature fields, executable bindings, errors, CPI order, effects and rollback. No successful fixed-relayer/Jupiter settlement, address substitution or privilege substitution was executed. Finite parser/rejection cases do not close privileged-body, arbitrary-input, allocator or security acceptance. The frozen comparator excludes only compute-metering lines and executable-image bytes.

The registry audit checks **177 packages, 4,005 files and 37,610,821 bytes** against pinned archives. All177 archives are retained for portable verification. Earlier primary material remains explicitly historical and is checked against the union of historical/current locks. Actual34 program and77 Anchor error implementations are independently rederived.

The prior465-window Linux control completed with465normalized/87raw matches and no ELF identity. Its full output/source bindings and two offline-resolution failure logs are retained. The failures were fixed by supplying the public sparse index and complete checksum-verified lock archives; they were not Rust source failures. It is a control for the preceding source, not validation of this new SDK source. Standard-library microprobes across native1.43–1.51, Linux1.48 sysroot and authenticated Linux1.49 sysroot retain nonmatching type-ID constants. They do not establish a unique compiler or rule out untested SDK/sysroot builds.

```sh
python3 -B repro/donation-relay/sdk32-source-recovery/verify.py --check-registry-source
work/test-env/bin/python -B repro/donation-relay/sdk32-source-recovery/receipt_verify.py --runtime
```

These commands rederive saved evidence without VM execution. The all-contract Rust-only goal remains active and whole-contract counts do not rise from these Relay windows. Earlier packets remain sealed, and shared HEAD/index and unrelated work remain preserved. Hosted run40325550614 failed; local verification does not establish hosted green.

## Subsequent live-source advance

During packaging, the shared checkout advanced independently to `rea-jupiter-cpi-20261026`. Its verifier passed with `--current`:477/492 normalized windows,107raw and whole ELF unequal. This packet remains the immutable476-window source snapshot. Its optional `--current` guard now fails deliberately because live source changed; the default historical verifier passes. Do not overwrite the newer root from this packet. The latest pointer is `repro/donation-relay/current.json`; the later snapshot reports527 runtime records under its own grouping, not this packet's536-record grouping.
