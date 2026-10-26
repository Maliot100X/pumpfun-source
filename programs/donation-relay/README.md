# Donation Relay reconstructed Rust

Whole captured-byte identity remains unachieved. Acceptance requires reconstructed Rust builds. Capture830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`. Captured ELF/assembly files remain analysis inputs; executable instructions do not enter compilation.

All five donation routes, epoch-close and just-swap now use real generated Anchor contexts. Just-swap retains actual Jupiter CPI, measured vault balance checks, receipt state, residual burn/close and program-layer relayer authorization. Three other settlement routes retain the prior arena reconstruction. Privileged success and exact business-body matches remain unfinished.

Selected platform-tools v1.48 output is881424bytes, SHA-256 `53fe5b68ce2eba3634912ac86637a99f342c0884b0d2578d8702282a50b29893`. Unstripped1008704bytes, SHA-256 `63e11ff8e08c264db2512ff144f01e6247c5c52867fc9d92e384779746adc43f`. A fresh final-path Rust build reproduces both exactly. The [swap balance evidence packet](../../repro/donation-relay/swap-body-source-recovery/README.md) binds45 compiled inputs. The candidate remains larger than the capture.

Complete normalized matches rise447→448, with one gain and no losses:80 raw matches and44 unmatched original windows. Balance helper91 now matches its complete2880-byte body. All19 direct-call sites are decoded; all callees except builder90 also match completely after normalization. Owned swap data now forwards in its observed argument position without an extra byte clone. Entire just-swap parser/init closures/wrapper/program/exit match. Its legitimate Distribution serializer caller also restores the complete epoch-close exit. Disassembly and a negative fixture corrected the input-mint constraint to debouncer.mint. No dummy calls preserve counts. Just-swap99, helpers90/109, close96, common112, policy106 and donation handlers remain unmatched. Normalization masks only call displacements and relocation immediates; register/branch/stack differences remain failures. Complete indirect/data/allocator/ELF layout closure is unproved.

All336 distinct finite signed scenarios pass again, including55 just-swap parser/init/rejection cases. Independent verification checks1985signature fields, cryptographic signatures, fixtures/PDA/rent/privileges/transactions, executable hashes, CPI bytes/accounts/order and rollback. No valid fixed-relayer/Jupiter success was executed or address/privilege substituted. Native Token-2022 routing, arbitrary inputs/allocator/RefCell behavior, settlement success and security acceptance remain unproved. Full observations remain saved; comparison omits compute-metering lines and executable-image bytes.

Cargo records remain unchanged: direct Token-2022 7.0.0 and Anchor SPL's6.0.0. Fresh registry audit checks177 packages,4055files/37402916bytes against pinned archives. Actual output rederives34 program and77 Anchor framework name/message implementations. The former owned selector ceased emission after its legitimate caller was replaced; it is not artificially retained.

```sh
python3 -B repro/donation-relay/swap-body-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/swap-body-source-recovery/receipt_verify.py --runtime
```

These rederive saved evidence without VM execution. Earlier --current checks intentionally fail after source advances. Remaining exact bodies, three generated settlement contexts, dispatcher and complete data/relocation/layout identity stay within the active all-contract Rust-only goal. This checkpoint establishes no additional whole-contract byte identity. Hosted CI failed unchanged Pump source-binding assertions and remains a separate gate.
