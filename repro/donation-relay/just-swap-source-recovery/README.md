# Relay just-swap Rust reconstruction

Whole captured ELF identity remains unachieved. Acceptance requires reconstructed Rust builds. Disassembly guides natural source recovery; no captured machine instructions enter compilation.

The selected Rust build matches **447 complete normalized original function windows, including80 raw matches**, leaving45of492 unmatched. Normalization masks only direct-call displacements and relocation immediates. Register, branch and stack differences remain failures. Against the427-window checkpoint there are20gains and no losses:10,13,20,21,22,43,44,82,118,145,150,151,152,153,161,168,185,202,227,246.

The real JustSwapV1 context is976bytes, with the Jupiter account stored as AccountInfo rather than UncheckedAccount. This restores the observed layout and context destructor. Entire18568-byte parser150,6664-byte receipt-init closure151,3584-byte ATA-init closure152,1432-byte wrapper185,3096-byte program202 and4056-byte exit153 match. Receipt initialization is nonidempotent and allocates49wirebytes. The parser retains real signer, program, PDA, token/ATA, mint, rent and mutability constraints. Program202 checks the fixed relayer through105 before calling handler99. The handler has no duplicate relayer guard.

One source hypothesis incorrectly constrained input mint to distribution.mint. The original parser instead compares debouncer.mint. Four differing stack loads identified that field. A separate signed fixture that changes debouncer.mint reproduces a log mismatch on the rejected source; corrected source matches the complete parser and fixture. The negative source/build/receipt is retained. Early local bump binding also changes five program-function instructions; passing the bump in the observed argument order restores the whole program function. These are measured compiler effects, not unique historical source attribution.

This legitimate caller also restores shared Distribution serializer20 and token reload21. Entire epoch-close exit145 now matches3304bytes, replacing the4216-byte inlined version. No redundant or dummy calls preserve match counts. Checked Distribution decoder161, token burn instruction helpers and event serialization also match.

Business bodies remain incomplete: just-swap99 is4272versus4448bytes; measured swap helper91 is2800versus2880; CPI builder90 is2656versus2496; burn/close109 is2808versus2856. The Rust performs actual Jupiter CPI with ordered account metas and PDA signer seeds, reloads input then output, checks exact consumption and positive output, initializes the receipt, reloads input again, burns residual input and closes the input vault, then constructs its event. Privileged success was not executed; these unmatched bodies are source hypotheses. Close handler96 remains4008versus4000. Common112, mint policy106, donation handlers, three other settlement routes, dispatcher and whole data/relocation/layout closure remain unfinished. No new forced-inline attributes, unsafe source, target blobs, ELF patches or broader masks were added.

Three successful source forms plus a fresh final-repository-path reproduction are retained: **four successful Rust builds**. Two earlier source compile failures are also retained: an incorrect error-variant name and an argument borrow mismatch. The selected45 Rust/config inputs preserve preceding Cargo.toml/Cargo.lock. Both final build paths reproduce exact stripped and unstripped outputs:

- Stripped881208bytes, SHA-256 `72c06efc203c8682fae618e997ec9b42b507ee44b6aad2f377efa9abaa63c861`.
- Unstripped1008488bytes, SHA-256 `baf6888b781e9a1ce1161a00d9483deb297f4eaa3a2f74b93f498d81ca345d96`.
- Capture830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

The candidate remains larger than the capture. Complete source/build/output/function/call/data/relocation/section/residual evidence is sealed. A fresh registry audit checks177 resolved packages,4055files/37402916bytes against pinned archives. Actual output rederives all34 program and77 Anchor framework names/messages. The owned framework-name selector ceased emission after replacing its legitimate legacy caller; no second emitted selector is claimed or artificially retained. Its source remains in the unchanged dependency.

All **336 distinct finite signed scenarios pass on this exact output**: prior281 plus55 just-swap parser, state, PDA, signer, mutability, mint, initialization and rejection cases. Duplicate distribution readonly/PDA labels count once. Independent verification checks336cases/1985signature fields, cryptographic signatures, canonical PDA/rent, exact fixtures/transactions/privileges, loaded executable hashes, CPI bytes/accounts/order and rollback. Baseline/suffix/prefund receipts bind attempted System receipt creation or top-up/allocate/assign, then ATA creation and token initialization before fixed-signer rejection. Prior-candidate negative controls retain missing_3/missing_5 and debouncer_mint_field log differences. Full original/selected observations match.

No valid fixed-relayer or Jupiter success was executed. No address or privilege substitution was used. Native Token-2022 routing, arbitrary inputs/allocator/RefCell behavior, settlement success and security acceptance remain unproved. Full observations are retained; the unchanged comparator excludes compute-metering log lines and executable-image bytes. Runtime runners execute VMs; these verification commands only rederive saved evidence:

```sh
python3 -B repro/donation-relay/just-swap-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/just-swap-source-recovery/receipt_verify.py --runtime
```

Historical --current checks intentionally fail once source advances. Three settlement contexts remain: distribute_after_just_swapping_v1, distribute_non_swap_output_mint_v1 and swap_then_distribute_v1. Whole-body, indirect/data/allocator and whole-ELF identity remain within the active all-contract Rust-only goal. This checkpoint establishes no additional whole-contract identity. Shared HEAD/index and unrelated edits remain preserved. Hosted run40278511874 failed unchanged Pump source-binding assertions; local Relay evidence is not hosted CI acceptance.
