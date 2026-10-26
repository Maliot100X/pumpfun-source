# Relay swap balance and CPI source recovery

Whole captured ELF identity remains unachieved. Acceptance requires reconstructed Rust builds. This checkpoint adds one complete normalized function match: balance helper91,2880bytes. Total448of492 complete normalized windows,80raw matches and44unmatched; no preceding match is lost. Normalization masks only direct-call displacements and relocation immediates. Register, branch and stack differences remain failures.

The selected helper snapshots cached input/output amounts, invokes Jupiter, reloads input then output, checks input-before minus input-after with overflow handling, requires exact expected consumption, checks output-after minus output-before and requires a positive delta. Rich errors retain source filename programs/contracts/src/cpi/jupiter.rs and lines92/103, with actual observed/expected values on input mismatch. All2880bytes match after the existing normalization.

`balance_evidence.py` independently decodes all19 actual direct-call sites. The18 edges other than builder90 reach complete normalized callee matches, including both token reloads, error conversion/name/formatting and copies. Builder90 remains unmatched; this is not transitive closure. Exact relocated source-filename bytes are checked at both sites. The source/call audit also matters: a thin vector pointer can produce the same forwarding instructions while representing a different argument position or ownership. The selected function receives the distribution signer key in the observed position and forwards an owned Vec without a new byte allocation. No data clone/to_vec remains. The CPI builder preserves ordered PDA-only signer metas, account cloning and explicit unsigned/signed invocation branches.

Seven measured source forms plus final-repository-path reproduction are retained: **eight successful Rust builds**, no failed builds in this packet. They cover thin-vector ABI, actual owned-vector/key argument order, seed-field snapshots, positive epoch predicate, CPI construction order, borrowed-key controls and direct-result/receipt-field controls. Similar sizes do not count as matches. Some equivalent changes emit the same helper body. The selected form restores observed allocation/ownership and construction order; it is not unique historical source attribution.

Unmatched bodies remain explicit. Handler99 is4456versus4448bytes; builder90 is2496versus2496 but differs in instructions; burn/close109 is2936versus2856; close96 remains4008versus4000. Builder size equality establishes no match. Seed fields are copied into locals as observed, and the handler retains real receipt updates, extra input reload, residual burn and input closure. Common112, policy106 and donation handlers remain unresolved. Three other settlement contexts, dispatcher and complete data/relocation/layout identity remain open. No forced-inline attributes, dummy calls, assembly compiler input, captured executable blobs, binary patches, unsafe source or additional masks were added.

Selected45 inventoried Rust/config inputs retain preceding Cargo.toml/Cargo.lock. Both final build paths reproduce exact stripped and unstripped outputs:

- Stripped881424bytes, SHA-256 `53fe5b68ce2eba3634912ac86637a99f342c0884b0d2578d8702282a50b29893`.
- Unstripped1008704bytes, SHA-256 `63e11ff8e08c264db2512ff144f01e6247c5c52867fc9d92e384779746adc43f`.
- Capture830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

The candidate remains larger than the capture. Complete source/build/output/function/call/data/relocation/section/residual evidence is retained. Registry audit freshly checks177packages,4055files/37402916bytes against pinned archives. Actual emitted34program and77Anchor framework name/message implementations are rederived. No second owned framework selector is emitted or claimed.

All **336 distinct finite signed scenarios pass again on this exact output**. No new distinct scenario is added. Independent saved-receipt verification checks1985signature fields, cryptographic signatures, canonical PDA/rent, exact fixtures/transactions/privileges, executable hashes, CPI bytes/accounts/order, state/token/event/return effects and rollback. All prior close and just-swap parser/init rejection cases are rerun, together with donation/native/Token-2022/IDL cases. Prior negative controls remain bound, including the debouncer-mint constraint correction.

No successful fixed-relayer/Jupiter execution was performed; no address or privilege substitution was used. These finite cases do not prove the modified privileged bodies. Native Token-2022 routing, arbitrary-input/allocator/RefCell behavior, settlement success and security acceptance remain unproved. Full observations are saved. The comparator still excludes only compute-metering log lines and executable-image bytes.

```sh
python3 -B repro/donation-relay/swap-body-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/swap-body-source-recovery/receipt_verify.py --runtime
```

These commands rederive saved evidence without VM execution; the retained runtime runners executed VMs. Their recorded work-directory invocations are retained rather than substituted with a moved script. Earlier --current checks intentionally fail after source advances. The original all-contract Rust-only goal remains active. This checkpoint establishes no additional whole-contract identity. Shared HEAD/index and unrelated edits remain preserved; hosted CI is a separate gate.
