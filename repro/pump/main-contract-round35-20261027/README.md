# Main Pump verified checkpoint — Round35

The maintained main contract matches **737 / 1,035 original function windows (71.2%)**, including **145 raw byte-equal bodies**. Those windows cover **900,048 / 1,792,208 original text bytes (50.2%)**. The closed direct-call subset contains 145 windows and excludes data references. Normalization masks specified call/address operands; it does not establish referenced data or whole-program identity. **Whole-ELF identity remains false.** These metrics measure binary coverage, not engineering work completed.

The captured-loader regression passes **44 suites / 10,468 cases** and **156 focused suites / 7,610 executions**, with **18,074 matching paired diagnostic-log cases**. These corpora overlap. Diagnostics exclude source coordinates and compute usage. Every original/candidate result retains its serialized transaction bytes; signatures and main-instruction attribution are rechecked. The complete corpus contains 18,078 paired executions. No current-chain acceptance is implied.

This round adds 74 distinct instruction inputs: the previously reviewed 22 comprise 12 extension and 10 IDL inputs, the final QuoteControl component adds 34, and the final V1 parser component adds 18. The existing 308-case extension suite is replaced by a stricter comparison of those same inputs; they are not counted as new cases. The numeric native-distribution planner retains 619 existing cases, not new coverage. Selected primary files are bound by the frozen integration plan:

- `src/admin_set_idl_authority.rs`
- `src/create_v2.rs`
- `src/distribution.rs`
- `src/extend_account.rs`
- `src/nested_create.rs`

Actual window changes against Round34 are +4 normalized and +8 raw. This description is generated from final evidence and does not infer source correctness from a count gain.

The source-specific pure text recipe is preserved as `text-order.ld`. The final compiler recipe `ordered.ld` includes the bounded two-object `.data.rel.ro` ordering. The fixed Borsh Location and debug-argument table have 0/2 original-relative starts before and 2/2 after the selected data order. These are only the two checked objects, not a whole-data-layout metric. The proof independently finds their original owner bodies and LDDW references, verifies Location/table fields and methods, and accounts for every text/data byte, pointer, relocation, symbol and remaining file byte. There is no post-link editing, padding, or injected original code/data. The concrete original table type, complete allocation extents, remaining data layout and the five tracked TypeId constants remain unresolved.

The opt-in `linux-v1.44-sbf` profile uses the pinned native macOS v1.44 compiler/host libraries with exactly25 SBF target libraries from the official Linux x86_64 v1.44 archive. Per-build inventories prove that only that target-library directory changed. This is a reproducible hybrid recipe, not proof of the original SDK. Its separate external-only cache has an ordinary clean producer, fresh cached parity and producer-unavailable controls. Every main crate is compiled again; no compiled main-Pump object enters that cache.

Four final compilations reproduce both ELF hashes: initial, repeat, maintained-source and archived-source builds. Two separate identity compilations support the initial and archived data-order certificates. Archive reproduction actually builds a fresh identity from archived primary, derives a new certificate with pure `text-order.ld`, then compiles a fresh final and requires both expected ELF hashes. The original admitted certificate is preserved unchanged as provenance. The read-only verifier uses explicit bundled artifact paths; its local transformation replay is not represented as fresh admission.

```sh
python repro/pump/main-contract-round35-20261027/verify.py
python repro/pump/main-contract-round35-20261027/reproduce.py \
  --registry-home /path/to/qualified/cargo-home \
  --dependency-cache /path/to/qualified/external-cache \
  --sdk /path/to/native-macos-v1.44 \
  --target-library-directory /path/to/linux-v1.44/rust/lib/rustlib/sbf-solana-solana/lib \
  --output work/reproduce-main-round35
```

The reproduction creates separate sibling identity and certificate paths; `--output` remains the final build directory. The native SDK and official target libraries are external, hash-bound inputs, not bundled or downloaded by the archive. A changed cache/profile context needs its own ordinary producer and parity proof. The original executable is used for evidence/comparison only, never as compiler or linker code/data input.

[Previous maintained checkpoint: Round34](../main-contract-round34-20261027/README.md). The remaining 298 function windows, validation paths, data, relocations and original build provenance remain open. [Parallel work queue](../../../research/main-pump-parallel-checkpoint-20261027/REMAINING-WORK.json).
