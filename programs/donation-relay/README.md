# Donation Relay reconstructed Rust

Whole captured-byte identity remains unachieved. Acceptance requires reconstructed Rust builds. The capture is 830,448 bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`. Captured instructions remain analysis inputs and do not enter compilation.

The selected Rust build matches **464 of 492 complete normalized windows**, including 86 raw matches, leaving 28 unmatched. It recovers the entire 2,224-byte remainder allocator and 440-byte growth function with no lost normalized matches from the 462-window checkpoint. All 14 actual math callees match; recursively closed direct-call shapes are checked. Only call displacements and relocated immediate words are normalized.

All eleven business instructions use generated Anchor contexts. The complete dispatcher, SDK entrypoint, three settlement parser/program/exit layers, receipt builder and swap balance helper match. The shared distribution worker is now 8,208 versus 8,264 bytes and remains unmatched. The mint-policy body expands to 4,016 versus 3,440 bytes after compilation cleanup and also remains unmatched. Business bodies, transitive close/CPI/resize helpers and full data/relocation/layout identity remain open.

The [distribution math evidence packet](../../repro/donation-relay/distribution-math-source-recovery/README.md) retains nine source trials and two independent final builds. The stripped output is 813,912 bytes, SHA-256 `8c3de0056c65eddb5f4cd561377077e05d2a63362613916d6b4404e59e0d7640`; unstripped is 923,168 bytes, SHA-256 `82692119c6d3fa66c0a74d2a890567e6f7f794a74c877b6e6fa6c01c7b73a930`. Both final paths reproduce exactly. Compiler dep-info identifies 27 reachable local Rust files within 49 inventoried Rust/config files. Obsolete arena modules no longer enter compilation. Cargo records remain unchanged.

All 536 named runtime records pass on this output, representing 534 unique fixtures and 3,107 signature fields. Independent verification checks canonical inputs/PDAs/rent, real transactions/privileges/signatures, executable bindings, errors, CPI order, effects and rollback. No successful fixed-relayer/Jupiter settlement or address/privilege substitution was executed. These finite cases do not close privileged-body, arbitrary-input, allocator or security acceptance. The frozen comparator excludes compute-metering lines and executable-image bytes.

The registry audit checks 177 packages, 4,055 files and 37,402,916 bytes against pinned archives. Actual emitted 34 program and 77 Anchor error implementations are rederived.

```sh
python3 -B repro/donation-relay/distribution-math-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/distribution-math-source-recovery/receipt_verify.py --runtime
```

These commands verify saved evidence without VM execution. Historical --current checks intentionally fail after source advances. The all-contract Rust-only goal remains active; this checkpoint establishes no additional whole-contract identity. Hosted CI remains a separate gate.
