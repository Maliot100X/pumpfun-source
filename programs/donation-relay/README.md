# Donation Relay reconstructed Rust

Whole captured-byte identity remains unachieved. Acceptance requires reconstructed Rust builds. Capture830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`. Captured ELF/assembly files remain analysis inputs; executable instructions do not enter compilation.

All eleven business instructions now use actual generated Anchor contexts. The entire dispatcher and SDK entrypoint match after existing normalization, with actual targets checked for every business wrapper. Distribution routes retain real token CPIs, recipient validation, weight allocation, receipt/event construction, residual burn/close and account-closing exits. Each program layer retains the fixed-relayer check before its handler. Privileged success and exact business-body closure remain unfinished.

Selected platform-tools v1.48 output is814200bytes, SHA-256 `f7c7a67fe1b3b83e97ef9d91cd821fdae5f374da9c69207ae4a15548c2412808`. Unstripped923880bytes, SHA-256 `14969da690851324ddf65c2e83abbfad1c666ed7dc6a0b17e5c5e3a81d47b580`. A fresh final-path Rust build reproduces both exactly. The [generated settlement evidence packet](../../repro/donation-relay/settlement-generated-source-recovery/README.md) binds49 compiled inputs. Candidate size is smaller than the capture and does not establish identity.

462complete normalized windows/93raw,30unmatched original Relay windows. There are16gains and two losses versus448: all three settlement parsers/exits/wrappers/program functions, dispatcher, SDK entrypoint, processed-event serialization and borrowed receipt builder recover complete matches. Old exact growth/resize specializations69/332 no longer match; no dummy callers retain them. Equal-sized but instruction-different bodies remain failures. Normalization masks only call displacements and relocation immediates. Body workers, math, transitive close/CPI helpers and full indirect/data/allocator/ELF layout identity remain open.

All536 named test records pass on this exact output, covering534unique input fixtures and3107signature fields. This corrects earlier distinct-scenario wording: the prior336records contain334unique inputs because two readonly labels repeat the just-swap baseline. All200new distribution/combined inputs are unique. Independent verification checks canonical fixtures/PDAs/rent, serialized states, actual transactions/effective privileges, cryptographic signatures, executable hashes, CPI bytes/accounts/order, effects and rollback. No successful fixed-relayer/Jupiter execution or address/privilege substitution occurred. Finite rejection cases do not close privileged-body/arbitrary-input/allocator/RefCell/native-Token2022/settlement/security acceptance. Full observations remain saved; comparison omits compute-metering lines and executable-image bytes.

Cargo records remain unchanged: direct Token-2022 7.0.0 and Anchor SPL's6.0.0. Fresh registry audit checks177 packages,4055files/37402916bytes against pinned archives. Actual emitted34program and77Anchor framework name/message implementations are rederived.

```sh
python3 -B repro/donation-relay/settlement-generated-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/settlement-generated-source-recovery/receipt_verify.py --runtime
```

These rederive saved evidence without VM execution. Earlier --current checks intentionally fail after source advances. All business contexts are generated; remaining exact bodies, transitive helpers and complete data/relocation/layout identity stay within the active all-contract Rust-only goal. This checkpoint establishes no additional whole-contract identity. Hosted CI remains a separate gate.
