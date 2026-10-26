# Relay generated settlement and complete dispatch reconstruction

Whole captured ELF identity remains unachieved. Acceptance requires reconstructed Rust builds. The selected build matches **462 complete normalized original windows, including93 raw matches**, leaving30of492 unmatched. Against the448-window checkpoint there are16gains and two losses. Normalization masks only direct-call displacements and relocation immediates; register, branch and stack differences remain failures.

All eleven business instructions now use actual generated Anchor contexts. The executable dispatch path forwards directly to Anchor; the former arena dispatcher no longer handles business routes. The complete2216-byte dispatcher169 and448-byte SDK entrypoint194 match. `settlement_evidence.py` decodes every actual direct dispatch target and verifies all eleven generated business wrappers. It does not infer routing from a nearby symbol or from normalized calls alone.

## Recovered contexts and call layers

| Instruction | Parser | Account exit | Program function |
|---|---:|---:|---:|
|distribute_after_just_swapping_v1|15496bytes|3488bytes|2984bytes|
|distribute_non_swap_output_mint_v1|13296bytes|2416bytes|2984bytes|
|swap_then_distribute_v1|16632bytes|3824bytes|3120bytes|

Each entire window in this table matches after existing normalization, as do their wrappers. The contexts retain typed state/token/mint/program/signer decoding, stored/canonical PDA seeds, associated-token addresses, mint-program relations, mutability, fixed relayer/Jupiter/mint addresses, nonidempotent output-ATA initialization and real distribution/receipt account-closing exits. Receipt-to-distribution binding uses the captured custom6033 constraint. The all-generated source uses the observed AccountInfo Jupiter field and boxed mint interfaces. Context sizes are696,640and920bytes respectively.

Every program function retains check105 before its business handler; no duplicate or omitted handler-layer relayer check is introduced. Combined distribution retains only its observed epoch business gate before weight admission and account partition. It does not inherit just-swap's extra initialized-state or mint business checks. Recipient prefix and Jupiter suffix remain distinct ordered slices.

The captured dispatcher visits donation, pubkey donation, native donation, native pubkey donation, payer donation, close, combined, just-swap, after-swap distribution, non-swap distribution and whitelist in that order. Restoring this declaration order recovers the entire dispatcher. Combined uses one48-byte owned argument aggregate. Binding the remaining-account slice before constructing it restores the entire3120-byte program function; equal length alone did not establish that match.

The shared distribution context is208bytes: remaining slice at0, source AccountInfo at16, mint at64, token program at112 and authority at160. This explicitly retains the corrected source/authority mapping. Its80-byte arguments carry share slice, signer groups, total, expected token program and decimals. The worker retains sequential recipient decoding/authority/mint/program checks, including zero allocations, and actual transfer_checked CPIs. Allocation uses a stable decreasing remainder order with original indices. Caller weight admission remains a checked u32 sum of10000, with no invented recipient cap, uniqueness check or positive-weight rule. Residual input is reloaded, burned when nonzero and closed. Combined closes the output vault after distribution and input cleanup. Generated exits close distribution and, for after-swap, receipt state accounts.

The receipt builder uses borrowed share and amount slices. Its observed iterator index/length fields at32/40 distinguish it from the earlier owned amount iterator. The complete808-byte helper81 now matches. Destructuring the worker's owned account fields at entry restores observed eager field copies and removes the separate aggregate-drop body, but does not yet recover worker108 completely.

Gains:81,119,146,147,148,149,154,155,169,184,186,187,194,200,201,203. Lost exact matches:69,332, the earlier RawVec growth and AccountInfo resize specializations. Their old matching bodies no longer appear after genuine callers and the executable arena path change. No dummy call preserves their counts.

## Remaining source and whole-file differences

After-swap97 is5216versus5216bytes but instruction-different; non-swap98 is5600versus5696; combined100 is5440versus5328; shared distribution108 is7192versus8264; fair math113 is2520versus2224. Equal sizes are not accepted. Close96, just-swap99, cleanup109, Jupiter builder90, common donation112, policy106 and donation handlers remain unmatched. [remaining-windows.json](remaining-windows.json) lists all30 remaining original Relay windows, with unclassified helpers left explicit.

Full generated exit windows do not prove their unmatched account-close callee282. Signed-CPI adapter300, allocator/resource behavior, indirect/data references and complete ELF relocation/layout identity remain open. The original all-contract Rust-only scope remains active; these Relay counts do not close other contracts. No new whole-contract identity is established. No new forced-inlining attributes, dummy calls, assembly compiler inputs, captured executable fragments, ELF patches, unsafe code or broader normalization are used.

Seven measured source forms plus final-repository-path reproduction are retained: **eight successful Rust builds**, no source compile failures in this packet. They cover the first two contexts; all-generated routing; combined argument aggregation; instruction order; early remaining-slice binding; borrowed receipt iteration; and worker field destructuring. Final49 inventoried Rust/config inputs retain Cargo.toml/Cargo.lock. Both final paths reproduce exact outputs:

- Stripped814200bytes, SHA-256 `f7c7a67fe1b3b83e97ef9d91cd821fdae5f374da9c69207ae4a15548c2412808`.
- Unstripped923880bytes, SHA-256 `14969da690851324ddf65c2e83abbfad1c666ed7dc6a0b17e5c5e3a81d47b580`.
- Capture830448bytes, SHA-256 `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`.

The candidate is now smaller than the capture. File size does not establish closeness or identity. Complete source/build/output/function/call/data/relocation/section/residual evidence remains sealed. A fresh registry audit checks177 packages,4055files/37402916bytes against pinned archives. Actual emitted34 program and77 Anchor framework names/messages are independently rederived; no second owned framework selector is claimed.

## Runtime evidence and corrected input count

All **536 named test records pass on the exact selected output**, comprising the preceding336 plus132 distribution and68 combined cases. They represent **534 unique input fixtures**, determined from complete starting account states, instruction bytes and ordered metas. The earlier336 records contain334unique fixtures: just-swap wrong_relayer, epoch_tracker_readonly and debouncer_readonly share one input. This corrects the earlier distinct-scenario wording without rewriting historical packets. All200 new inputs are unique. The executable image is bound separately and does not inflate the input count.

The new cases cover shares decoding and truncation/count boundaries, ignored suffixes, missing accounts, state owner/discriminator/size/enum/PDA constraints, readonly and signer flags, token owner/mint/authority/address constraints, wrong programs, receipt binding, alias inputs and combined output-ATA initialization. Some fields fail only at the fixed signer constraint; no deeper business-gate coverage is inferred from them.

Independent verification reconstructs each new canonical fixture and mutation, checks canonical PDA/rent/serialized-state bytes, real transactions and effective privileges, verifies3107signature fields cryptographically, binds executable hashes where observed, checks exact errors, full original/candidate observations and rollback. Combined baseline/suffix/prefund receipts additionally bind the entire attempted ATA→Token size→System creation/top-up/allocate/assign→Token initialization sequence before signer rejection. Distribution-only parser cases issue no CPIs. Eight previous-candidate log differences are retained as negative controls.

No valid fixed-relayer/Jupiter success was executed, and no address or privilege substitution was used. These finite parser/rejection cases do not prove privileged bodies, arbitrary inputs/allocator/RefCell behavior, native Token-2022 routing, settlement success or security acceptance. Full observations are saved; the frozen comparator excludes compute-metering lines and executable-image bytes.

```sh
python3 -B repro/donation-relay/settlement-generated-source-recovery/verify.py --current --check-registry-source
work/test-env/bin/python -B repro/donation-relay/settlement-generated-source-recovery/receipt_verify.py --runtime
```

These rederive saved evidence without VM execution. The retained runtime runners executed VMs using recorded work-directory invocations. Earlier --current checks intentionally fail after source advances; historical verification remains usable. Shared HEAD/index and unrelated work remain preserved. Hosted CI remains a separate gate.
