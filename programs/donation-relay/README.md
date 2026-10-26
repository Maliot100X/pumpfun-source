# Donation Relay reconstructed Rust

Whole captured-byte identity remains unachieved. Acceptance requires reconstructed Rust builds. The capture is830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`. Captured ELF/assembly files remain analysis inputs; target executable instructions do not enter compilation.

All five donation routes use generated Anchor contexts, a common Rust body, typed mint policy, instruction handlers and program-layer events. Epoch-close now also uses a real typed context and Distribution account, actual token transfer/state updates and the observed program-layer relayer check. Four other settlement routes retain the prior arena reconstruction. There are five total settlement instructions; prior ledgers saying six were incorrect.

The selected platform-tools v1.48 output is877920bytes, SHA-256 `e2f674655d6cf2b24b7abfd57fbd789b7cb664e055904f0c73e1679844b622e3`. Unstripped output is1013136bytes, SHA-256 `7a2a6646e2dc34956f8ab81dce80cc44aa59916cf07aa3537773070aa75b0f69`. A fresh final-path Rust build reproduces both exactly. The [epoch-close evidence packet](../../repro/donation-relay/epoch-close-source-recovery/README.md) binds43 compiled inputs and complete source/output/receipt evidence. The candidate remains larger than the capture.

Complete normalized matches rise416→427, with11gains and no losses:80 raw matches and65 unmatched original windows. Entire close parser, initialization closures, generated wrapper and program function match. Close handler96 remains4008versus4000bytes, exit145 remains4216versus3304. Common donation112, policy106 and donation handlers also remain unmatched. Normalization masks only call displacements and relocation immediates; register/branch/stack differences remain failures. Source/package/module topology and complete call/data/indirect/allocator/ELF layout closure are unproved.

All281 distinct finite signed scenarios pass, including27 Token-2022 policy fixtures and40 new close parser/initialization/rejection cases. Independent verification checks1688signature fields, exact fixtures/PDA/rent/privileges/transactions, token program hashes, CPI bytes/accounts/order, state/token/event/return effects and rollback. Fixed-relayer success was not executed. Call-map auditing separately caught and corrected missing program-layer authorization in trial forms that finite rejection tests could not detect. Native Token-2022 routing, arbitrary input/allocator/RefCell behavior, settlement success and security acceptance remain unproved. Full observations remain saved; comparison omits compute-metering lines and executable-image bytes.

Cargo records remain unchanged from the preceding checkpoint: direct Token-2022 7.0.0 and Anchor SPL's6.0.0. A fresh registry audit checks177 resolved packages,4055files/37402916bytes against pinned archives. Final34 program and both77 framework name/message implementations are rederived from actual output.

```sh
python3 -B repro/donation-relay/epoch-close-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/epoch-close-source-recovery/receipt_verify.py --runtime
```

These rederive saved evidence without VM execution. Earlier --current checks intentionally fail after source advances. Remaining exact bodies, four generated settlement contexts, dispatcher and complete data/relocation/layout identity stay within the active all-contract Rust-only goal. This checkpoint establishes no additional whole-contract byte identity. Hosted CI remains a separate, currently failing gate.
