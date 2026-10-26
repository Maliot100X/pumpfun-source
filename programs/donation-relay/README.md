# Donation Relay reconstructed Rust

Whole captured-byte identity remains unachieved. Acceptance requires reconstructed Rust builds. Capture830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`. Captured ELF/assembly files remain analysis inputs; executable instructions do not enter compilation.

All five donation routes, epoch-close and just-swap now use real generated Anchor contexts. Just-swap retains actual Jupiter CPI, measured vault balance checks, receipt state, residual burn/close and program-layer relayer authorization. Three other settlement routes retain the prior arena reconstruction. Privileged success and exact business-body matches remain unfinished.

Selected platform-tools v1.48 output is881208bytes, SHA-256 `72c06efc203c8682fae618e997ec9b42b507ee44b6aad2f377efa9abaa63c861`. Unstripped1008488bytes, SHA-256 `baf6888b781e9a1ce1161a00d9483deb297f4eaa3a2f74b93f498d81ca345d96`. A fresh final-path Rust build reproduces both exactly. The [just-swap evidence packet](../../repro/donation-relay/just-swap-source-recovery/README.md) binds45 compiled inputs. The candidate remains larger than the capture.

Complete normalized matches rise427→447, with20gains and no losses:80 raw matches and45 unmatched original windows. Entire just-swap parser/init closures/wrapper/program/exit match. Its legitimate Distribution serializer caller also restores the complete epoch-close exit. Disassembly and a negative fixture corrected the input-mint constraint to debouncer.mint. No dummy calls preserve counts. Just-swap99, helpers90/91/109, close96, common112, policy106 and donation handlers remain unmatched. Normalization masks only call displacements and relocation immediates; register/branch/stack differences remain failures. Complete indirect/data/allocator/ELF layout closure is unproved.

All336 distinct finite signed scenarios pass, including55 new just-swap parser/init/rejection cases. Independent verification checks1985signature fields, cryptographic signatures, fixtures/PDA/rent/privileges/transactions, executable hashes, CPI bytes/accounts/order and rollback. No valid fixed-relayer/Jupiter success was executed or address/privilege substituted. Native Token-2022 routing, arbitrary inputs/allocator/RefCell behavior, settlement success and security acceptance remain unproved. Full observations remain saved; comparison omits compute-metering lines and executable-image bytes.

Cargo records remain unchanged: direct Token-2022 7.0.0 and Anchor SPL's6.0.0. Fresh registry audit checks177 packages,4055files/37402916bytes against pinned archives. Actual output rederives34 program and77 Anchor framework name/message implementations. The former owned selector ceased emission after its legitimate caller was replaced; it is not artificially retained.

```sh
python3 -B repro/donation-relay/just-swap-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/just-swap-source-recovery/receipt_verify.py --runtime
```

These rederive saved evidence without VM execution. Earlier --current checks intentionally fail after source advances. Remaining exact bodies, three generated settlement contexts, dispatcher and complete data/relocation/layout identity stay within the active all-contract Rust-only goal. This checkpoint establishes no additional whole-contract byte identity. Hosted CI failed unchanged Pump source-binding assertions and remains a separate gate.
