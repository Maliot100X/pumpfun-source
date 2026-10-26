# Relay epoch-close Rust reconstruction

Whole-contract byte identity remains unachieved. Acceptance requires reconstructed Rust builds. Disassembly guides source recovery; captured executable instructions do not enter compilation.

The selected Rust build matches **427 complete normalized original function windows, including 80 raw matches**, leaving65 of492 unmatched. Normalization masks only direct-call displacements and relocation immediates. Register, stack and branch differences remain failures. Relative to the416-window checkpoint, gains are11,26,83,86,117,142,143,144,162,183,204, with no losses.

The real Anchor epoch-close context restores the15464-byte parser,6880-byte Distribution initialization closure,3536-byte associated-token initialization closure,2016-byte generated wrapper and3232-byte program function. Distribution is a real Anchor account with98-byte wire data. Its typed context retains PDA seeds, stored bumps, fixed signer, token/mint, rent, mutability and program checks. Associated-token creation is nonidempotent. The handler performs the actual transfer, initializes Distribution, clears the debouncer total and advances the tracker epoch.

The original call chain is wrapper183 → program204 → handler96. Program204 calls relayer check105 before handler96; the handler has no duplicate relayer check. Direct-call auditing caught trial forms that passed the owned-key rejection fixtures but omitted the program-layer check. The selected Rust restores the check at the observed layer and matches the entire program function. Seven retained background forms bind that negative evidence. The finite runtime cases cannot establish privileged success.

Handler96 remains4008bytes versus original4000; exit145 remains4216versus3304. Checked Distribution decoding and its shared serializer still require legitimate settlement callers. Common donation112, policy106 and donation handlers remain unmatched as documented in the preceding packet. No forced-inline attributes, dummy calls, target-code blobs, binary patches or unsafe source were added. No indirect/data/allocator or full-ELF closure follows from function matches.

Eight measured source forms plus a fresh final-repository-path reproduction are retained: **nine successful Rust builds**, no source compile failures. The selected43 Rust/config inputs retain the preceding Cargo.toml/Cargo.lock. Both final build paths reproduce stripped and unstripped outputs exactly:

- Stripped:877920bytes, SHA-256 `e2f674655d6cf2b24b7abfd57fbd789b7cb664e055904f0c73e1679844b622e3`.
- Unstripped:1013136bytes, SHA-256 `7a2a6646e2dc34956f8ab81dce80cc44aa59916cf07aa3537773070aa75b0f69`.
- Capture:830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

The candidate remains larger than the capture. Complete source/build/output/function/call/data/relocation/section/residual evidence is retained. The actual output rederives34 program and both77 framework name/message implementations. A fresh registry audit checks177 resolved packages,4055files/37402916bytes against pinned archives.

All **281 distinct finite signed scenarios pass on this exact output**: the preceding241 plus40 epoch-close parser, initialization and rejection cases. Those40 cover missing accounts, stored-state owner/discriminator/enum/size/PDA/mutability, fixed signer, distribution and token constraints, prefunding, existing accounts and ignored instruction suffix. Real signatures, privileges, blockhash checks and transaction history remain enabled. Baseline/suffix/prefund receipts independently bind attempted System and ATA initialization CPIs before fixed-signer rejection and complete rollback. The previous candidate differs on missing_0/missing_1 logs; these controls are retained. Original and selected candidate match all40.

Independent receipt verification checks281cases and1688signature fields, including cryptographic signatures, canonical PDA/rent, fixtures, exact transactions/privileges, loaded token executable hash, CPI bytes/accounts/order, state/token/event/return effects and rollback. No valid fixed-relayer success was executed; no relayer address or privilege was substituted. Native Token-2022 routing, arbitrary inputs/allocator/RefCell behavior, settlement success and security acceptance remain unproved. Full observations are saved; the unchanged comparator excludes compute-metering lines and executable-image bytes. Receipt verification rechecks evidence without VM execution.

```sh
python3 -B repro/donation-relay/epoch-close-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/epoch-close-source-recovery/receipt_verify.py --runtime
```

Earlier --current checks intentionally fail after source advances; historical verification remains usable. There are five total settlement instructions, correcting the earlier ledger's count of six. Epoch-close leaves four contexts/handlers to reconstruct: distribute_after_just_swapping_v1, distribute_non_swap_output_mint_v1, just_swap_v1 and swap_then_distribute_v1. Exact remaining bodies, dispatcher and complete data/relocation/layout identity remain within the active all-contract Rust-only goal. Shared HEAD/index and unrelated edits are preserved. Hosted CI is a separate gate; the preceding hosted run failed and is not acceptance.
